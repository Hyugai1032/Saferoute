#analytics_app/services/congestion.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Dict, Any

from django.db.models import OuterRef, Subquery, Sum
from django.utils import timezone


@dataclass
class CongestionParams:
    window_minutes: int = 60       # how far back to compute inflow/outflow
    horizon_minutes: int = 60      # how far ahead to predict
    # weights for hybrid score
    w_occ: float = 0.50
    w_pred: float = 0.40
    w_vuln: float = 0.10


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _capacity_of(center) -> int:
    capacity_raw = getattr(center, "individual_capacity_max", None)
    try:
        return int(capacity_raw or 0)
    except (TypeError, ValueError):
        return 0


def _no_capacity_result(center, capacity: int, params: CongestionParams) -> Dict[str, Any]:
    # If capacity is missing, DON'T return 400.
    # Return a valid LOW-risk payload so the frontend table won't spam 400s.
    return {
        "center_id": center.id,
        "capacity": capacity,
        "latest_log_time": None,

        "current_total": 0,
        "occupancy": 0.0,

        "window_minutes": params.window_minutes,
        "horizon_minutes": params.horizon_minutes,
        "total_in_window": 0,
        "total_out_window": 0,
        "net_rate_per_min": 0.0,

        "predicted_total": 0,
        "predicted_occupancy": 0.0,

        "vulnerable_total": 0,
        "vulnerability_ratio": 0.0,

        "risk_score": 0.0,
        "risk_level": "LOW",
        "recommendation": "No capacity configured for this center.",
    }


def _build_result(
    *,
    center,
    capacity: int,
    latest,
    total_in: int,
    total_out: int,
    params: CongestionParams,
) -> Dict[str, Any]:
    """
    The actual model. It does no database work: callers fetch `latest` (the newest log
    row or None) and the in/out totals for the window, either one center at a time
    (compute_congestion_risk) or for many centers at once (compute_congestion_risk_bulk).
    """
    current_total = int(getattr(latest, "total_current", 0) or 0)
    occupancy = current_total / float(capacity)

    # Vulnerability ratio from latest snapshot (optional but good)
    if latest and current_total > 0:
        vulnerable_total = (
            int(getattr(latest, "children_count", 0) or 0)
            + int(getattr(latest, "senior_count", 0) or 0)
            + int(getattr(latest, "pwd_count", 0) or 0)
            + int(getattr(latest, "pregnant_count", 0) or 0)
            + int(getattr(latest, "lactating_count", 0) or 0)
        )
        vulnerability_ratio = vulnerable_total / float(current_total)
        vulnerability_ratio = clamp(vulnerability_ratio, 0.0, 1.0)
    else:
        vulnerable_total = 0
        vulnerability_ratio = 0.0

    net_flow = total_in - total_out
    net_rate_per_min = net_flow / float(params.window_minutes) if params.window_minutes > 0 else 0.0

    # For congestion prediction, negative net rate means it's easing; clamp to 0 to avoid “negative risk”
    net_rate_per_min = max(0.0, net_rate_per_min)

    # 3) short-horizon forecast
    predicted_total = current_total + (net_rate_per_min * params.horizon_minutes)
    predicted_occupancy = predicted_total / float(capacity)

    # 4) risk score (hybrid)
    risk_score = (
        params.w_occ * occupancy
        + params.w_pred * predicted_occupancy
        + params.w_vuln * vulnerability_ratio
    )

    # Guardrails / risk level
    if predicted_occupancy >= 1.0:
        risk_level = "CRITICAL"
    elif occupancy >= 0.95:
        risk_level = "HIGH"
    elif risk_score >= 0.90:
        risk_level = "HIGH"
    elif risk_score >= 0.70:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

    # Recommendation text (optional)
    if risk_level == "CRITICAL":
        recommendation = "Center likely to exceed capacity soon. Redirect evacuees to nearby centers."
    elif risk_level == "HIGH":
        recommendation = "High congestion risk. Prepare overflow plan and monitor inflow closely."
    elif risk_level == "MODERATE":
        recommendation = "Moderate risk. Continue monitoring and prepare additional resources."
    else:
        recommendation = "Low risk. Normal monitoring."

    return {
        "center_id": center.id,
        "capacity": capacity,
        "latest_log_time": latest.date_recorded.isoformat() if latest else None,

        "current_total": current_total,
        "occupancy": round(occupancy, 4),

        "window_minutes": params.window_minutes,
        "horizon_minutes": params.horizon_minutes,
        "total_in_window": total_in,
        "total_out_window": total_out,
        "net_rate_per_min": round(net_rate_per_min, 4),

        "predicted_total": int(round(predicted_total)),
        "predicted_occupancy": round(predicted_occupancy, 4),

        "vulnerable_total": vulnerable_total,
        "vulnerability_ratio": round(vulnerability_ratio, 4),

        "risk_score": round(risk_score, 4),
        "risk_level": risk_level,
        "recommendation": recommendation,
    }


def compute_congestion_risk(
    *,
    center,
    EvacuationLogModel,
    params: CongestionParams = CongestionParams(),
) -> Dict[str, Any]:
    """
    Hybrid Real-Time Congestion Risk Model (no training required)

    Single-center version: 2 queries per call. Fine for one center; for many centers
    use fetch_latest_logs() + compute_congestion_risk_bulk() instead.

    Requires:
      - center.capacity (int)
      - logs fields (based on your schema):
        date_recorded, individuals_in, individuals_out, total_current,
        children_count, lactating_count, pregnant_count, pwd_count, senior_count
    """
    capacity = _capacity_of(center)
    if capacity <= 0:
        return _no_capacity_result(center, capacity, params)

    # 1) latest snapshot
    latest = (
        EvacuationLogModel.objects
        .filter(center_id=center.id)
        .order_by("-date_recorded", "-id")
        .only(
            "date_recorded",
            "total_current",
            "children_count",
            "lactating_count",
            "pregnant_count",
            "pwd_count",
            "senior_count",
        )
        .first()
    )

    # 2) compute inflow/outflow in window
    since = timezone.now() - timedelta(minutes=params.window_minutes)
    agg = (
        EvacuationLogModel.objects
        .filter(center_id=center.id, date_recorded__gte=since)
        .aggregate(
            total_in=Sum("individuals_in"),
            total_out=Sum("individuals_out"),
        )
    )

    return _build_result(
        center=center,
        capacity=capacity,
        latest=latest,
        total_in=int(agg["total_in"] or 0),
        total_out=int(agg["total_out"] or 0),
        params=params,
    )


# --------------------------------------------------------------------------- #
# Bulk versions: a fixed number of queries no matter how many centers there are.
# --------------------------------------------------------------------------- #

def fetch_latest_logs(centers_qs, EvacuationLogModel):
    """
    Evaluate `centers_qs` and find each center's newest log, using 2 queries in total
    (the centers, with the newest log id attached by a subquery; then the log rows).

    Returns (centers, latest_by_center): a list of center objects and a dict
    {center_id: newest log row or None}. "Newest" = highest date_recorded, ties broken
    by highest id (the same rule the serializer uses).
    """
    newest_log_id = (
        EvacuationLogModel.objects
        .filter(center_id=OuterRef("pk"))
        .order_by("-date_recorded", "-id")
        .values("id")[:1]
    )
    centers = list(centers_qs.annotate(latest_log_pk=Subquery(newest_log_id)))
    logs = EvacuationLogModel.objects.in_bulk(
        [c.latest_log_pk for c in centers if c.latest_log_pk]
    )
    return centers, {c.id: logs.get(c.latest_log_pk) for c in centers}


def compute_congestion_risk_bulk(
    *,
    centers,
    latest_by_center,
    EvacuationLogModel,
    params: CongestionParams = CongestionParams(),
) -> Dict[int, Dict[str, Any]]:
    """
    Same result as compute_congestion_risk() for every center, but the in/out totals for
    all centers come from ONE grouped query. `latest_by_center` comes from
    fetch_latest_logs().

    Returns {center_id: result_dict}. If computing one center raises, that center gets
    {"error": "..."} and the others are unaffected.
    """
    centers = list(centers)

    # Read each capacity once, guarded per center, so one bad row can't break the rest.
    capacities = {}
    results = {}
    for c in centers:
        try:
            capacities[c.id] = _capacity_of(c)
        except Exception as exc:
            results[c.id] = {"error": f"Prediction failed for this center: {exc}"}

    with_capacity = [cid for cid, cap in capacities.items() if cap > 0]
    flows = {}
    if with_capacity:
        since = timezone.now() - timedelta(minutes=params.window_minutes)
        rows = (
            EvacuationLogModel.objects
            .filter(center_id__in=with_capacity, date_recorded__gte=since)
            .order_by()                      # no default ordering leaking into GROUP BY
            .values("center_id")
            .annotate(total_in=Sum("individuals_in"), total_out=Sum("individuals_out"))
        )
        flows = {
            r["center_id"]: (int(r["total_in"] or 0), int(r["total_out"] or 0))
            for r in rows
        }

    for center in centers:
        if center.id in results:        # already failed above
            continue
        try:
            capacity = capacities[center.id]
            if capacity <= 0:
                results[center.id] = _no_capacity_result(center, capacity, params)
                continue

            total_in, total_out = flows.get(center.id, (0, 0))
            results[center.id] = _build_result(
                center=center,
                capacity=capacity,
                latest=latest_by_center.get(center.id),
                total_in=total_in,
                total_out=total_out,
                params=params,
            )
        except Exception as exc:  # keep one bad center from sinking the whole map
            results[center.id] = {"error": f"Prediction failed for this center: {exc}"}

    return results