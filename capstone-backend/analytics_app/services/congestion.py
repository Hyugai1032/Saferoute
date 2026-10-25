#analytics_app/services/congestion.py
"""
Hybrid congestion forecast + rule-based risk scoring.

Forecast (what changes with data):
  - No logs yet      -> prior only (population or capacity x hazard x arrival S-curve)
  - 1-5 logs         -> blend of prior and Holt trend (shifts toward Holt as logs arrive)
  - 6+ logs          -> Holt trend only
Risk level (always the same rules): weighted score + guardrails + forecast tiers.
"""
from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Dict, Any, List, Tuple

from django.db.models import Count, OuterRef, Subquery, Sum
from django.utils import timezone


@dataclass
class CongestionParams:
    window_minutes: int = 60       # how far back to compute inflow/outflow (display only)
    horizon_minutes: int = 60      # how far ahead to predict
    # weights for hybrid score
    w_occ: float = 0.50
    w_pred: float = 0.40
    w_vuln: float = 0.10


MODEL_VERSION = "hybrid-v1"

# How far back a center's logs count as "the current event".
EVENT_LOOKBACK_HOURS = 72
# How many of the newest logs Holt smoothing uses.
HOLT_MAX_POINTS = 12
# Number of logs at which the forecast relies fully on live data.
FULL_TRUST_LOGS = 6

# Cold-start prior. PLACEHOLDERS: replace with values fitted from DROMIC reports.
PRIOR = {
    # share of the catchment population expected to stay in ECs, by hazard level
    "evac_rate": {"LOW": 0.03, "MEDIUM": 0.08, "HIGH": 0.15},
    # fallback when barangay population is missing: expected fill as a share of capacity
    # (assumption, not calibrated)
    "capacity_fill": {"LOW": 0.60, "MEDIUM": 0.85, "HIGH": 1.10},
    "k_per_hour": 0.35,   # steepness of the arrival S-curve
    "t50_hours": 8.0,     # hours after event start when half of evacuees have arrived
}
_LEVEL = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _capacity_of(center) -> int:
    capacity_raw = getattr(center, "individual_capacity_max", None)
    try:
        return int(capacity_raw or 0)
    except (TypeError, ValueError):
        return 0


# --------------------------------------------------------------------------- #
# Forecast building blocks
# --------------------------------------------------------------------------- #

def _hazard_level(center) -> str:
    return max(
        getattr(center, "flood_susceptibility", "LOW") or "LOW",
        getattr(center, "landslide_susceptibility", "LOW") or "LOW",
        key=lambda s: _LEVEL.get(s, 0),
    )


def _logistic(t_hours: float, k: float, t50: float) -> float:
    # guard against overflow for very large |t|
    z = clamp(-k * (t_hours - t50), -60.0, 60.0)
    return 1.0 / (1.0 + math.exp(z))


def prior_expected_demand(center, centers_in_barangay: int = 1) -> Tuple[float, str]:
    """
    Expected eventual evacuees for this center, without any logs.
    Returns (demand, source) where source is "population", "capacity" or "none".
    """
    level = _hazard_level(center)

    brgy = getattr(center, "barangay", None)
    pop = int(getattr(brgy, "population", 0) or 0) if brgy else 0
    if pop > 0:
        rate = PRIOR["evac_rate"].get(level, PRIOR["evac_rate"]["LOW"])
        return pop * rate / max(1, centers_in_barangay), "population"

    capacity = _capacity_of(center)
    if capacity > 0:
        fill = PRIOR["capacity_fill"].get(level, PRIOR["capacity_fill"]["LOW"])
        return capacity * fill, "capacity"

    return 0.0, "none"


def prior_arrivals(demand: float, event_start, now, horizon_minutes: int) -> float:
    """Arrivals expected between now and now+horizon, following the S-curve."""
    if demand <= 0:
        return 0.0
    # No logs yet: treat "now" as the start of the event.
    start = event_start or now
    t = max(0.0, (now - start).total_seconds() / 3600)
    h = horizon_minutes / 60
    k, t50 = PRIOR["k_per_hour"], PRIOR["t50_hours"]
    return demand * (_logistic(t + h, k, t50) - _logistic(t, k, t50))


def holt_trend_per_min(points, alpha: float = 0.5, beta: float = 0.3) -> Optional[float]:
    """
    Holt's linear (double exponential) smoothing on irregularly spaced logs.
    points = [(datetime, total_current), ...] oldest -> newest.
    Returns the smoothed trend in persons/minute (can be negative), or None if < 2 points.
    """
    if len(points) < 2:
        return None
    # Start the trend at the first observed slope instead of 0, so a few logs are enough.
    first_dt = max(1.0, (points[1][0] - points[0][0]).total_seconds() / 60)
    level = float(points[0][1])
    trend = (float(points[1][1]) - float(points[0][1])) / first_dt
    for (t_prev, _), (t, y) in zip(points, points[1:]):
        dt = max(1.0, (t - t_prev).total_seconds() / 60)
        prev_level = level
        level = alpha * float(y) + (1 - alpha) * (level + trend * dt)
        trend = beta * (level - prev_level) / dt + (1 - beta) * trend
    return trend


# --------------------------------------------------------------------------- #
# Result builders (no database work)
# --------------------------------------------------------------------------- #

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

        "model": "none",
        "model_version": MODEL_VERSION,
        "data_points": 0,
        "data_weight": 0.0,
        "expected_demand": 0,
        "demand_source": "none",
    }


def _build_result(
    *,
    center,
    capacity: int,
    latest,
    total_in: int,
    total_out: int,
    points: List[Tuple[Any, int]],
    event_start,
    centers_in_barangay: int,
    params: CongestionParams,
) -> Dict[str, Any]:
    """
    The actual model. It does no database work: callers fetch `latest` (newest log row
    or None), the in/out totals for the window, and the recent (time, total_current)
    points, either one center at a time or for many centers at once.
    """
    now = timezone.now()
    current_total = int(getattr(latest, "total_current", 0) or 0)
    occupancy = current_total / float(capacity)

    # Vulnerability ratio from latest snapshot
    if latest and current_total > 0:
        vulnerable_total = (
            int(getattr(latest, "children_count", 0) or 0)
            + int(getattr(latest, "senior_count", 0) or 0)
            + int(getattr(latest, "pwd_count", 0) or 0)
            + int(getattr(latest, "pregnant_count", 0) or 0)
            + int(getattr(latest, "lactating_count", 0) or 0)
        )
        vulnerability_ratio = clamp(vulnerable_total / float(current_total), 0.0, 1.0)
    else:
        vulnerable_total = 0
        vulnerability_ratio = 0.0

    # ---- Forecast ---------------------------------------------------------- #
    trend = holt_trend_per_min(points)                         # None when < 2 logs
    observed_pred = current_total + (trend or 0.0) * params.horizon_minutes

    demand, demand_source = prior_expected_demand(center, centers_in_barangay)
    # Only arrivals still to come: subtract who is already there.
    remaining_demand = max(0.0, demand - current_total)
    prior_pred = current_total + prior_arrivals(
        remaining_demand, event_start, now, params.horizon_minutes
    )

    # Trust live data more as logs accumulate (0 logs -> prior, FULL_TRUST_LOGS+ -> observed)
    w = min(1.0, len(points) / float(FULL_TRUST_LOGS))
    if demand <= 0:              # nothing to blend with -> rely on live data alone
        w = 1.0 if points else 0.0

    predicted_total = max(0.0, w * observed_pred + (1 - w) * prior_pred)
    predicted_occupancy = predicted_total / float(capacity)

    if w == 0:
        model = "prior"
    elif w < 1:
        model = "hybrid"
    else:
        model = "observed"

    # Kept for the frontend ("net rate / min"); never shown as negative risk.
    net_rate_per_min = max(0.0, trend or 0.0)

    # ---- Risk score (rule-based, unchanged weights) ------------------------ #
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
    elif predicted_occupancy >= 0.85:      # forecast-driven tier
        risk_level = "HIGH"
    elif predicted_occupancy >= 0.60:      # forecast-driven tier
        risk_level = "MODERATE"
    elif risk_score >= 0.90:
        risk_level = "HIGH"
    elif risk_score >= 0.70:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"

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

        # new: lets the UI / paper show how the forecast was made
        "model": model,                      # prior / hybrid / observed
        "model_version": MODEL_VERSION,
        "data_points": len(points),
        "data_weight": round(w, 2),
        "expected_demand": int(round(demand)),
        "demand_source": demand_source,      # population / capacity / none
    }


# --------------------------------------------------------------------------- #
# Single-center version
# --------------------------------------------------------------------------- #

def compute_congestion_risk(
    *,
    center,
    EvacuationLogModel,
    params: CongestionParams = CongestionParams(),
) -> Dict[str, Any]:
    """Single-center version (4 queries). For many centers use the bulk path."""
    capacity = _capacity_of(center)
    if capacity <= 0:
        return _no_capacity_result(center, capacity, params)

    now = timezone.now()

    latest = (
        EvacuationLogModel.objects
        .filter(center_id=center.id)
        .order_by("-date_recorded", "-id")
        .only(
            "date_recorded", "total_current",
            "children_count", "lactating_count", "pregnant_count",
            "pwd_count", "senior_count",
        )
        .first()
    )

    since = now - timedelta(minutes=params.window_minutes)
    agg = (
        EvacuationLogModel.objects
        .filter(center_id=center.id, date_recorded__gte=since)
        .aggregate(total_in=Sum("individuals_in"), total_out=Sum("individuals_out"))
    )

    recent = list(
        EvacuationLogModel.objects
        .filter(center_id=center.id, date_recorded__gte=now - timedelta(hours=EVENT_LOOKBACK_HOURS))
        .order_by("date_recorded", "id")
        .values_list("date_recorded", "total_current")
    )
    event_start = recent[0][0] if recent else None
    points = recent[-HOLT_MAX_POINTS:]

    centers_in_barangay = 1
    if getattr(center, "barangay_id", None):
        centers_in_barangay = center.__class__.objects.filter(barangay_id=center.barangay_id).count()

    return _build_result(
        center=center,
        capacity=capacity,
        latest=latest,
        total_in=int(agg["total_in"] or 0),
        total_out=int(agg["total_out"] or 0),
        points=points,
        event_start=event_start,
        centers_in_barangay=centers_in_barangay,
        params=params,
    )


# --------------------------------------------------------------------------- #
# Bulk versions: a fixed number of queries no matter how many centers there are.
# --------------------------------------------------------------------------- #

def fetch_latest_logs(centers_qs, EvacuationLogModel):
    """
    Evaluate `centers_qs` and find each center's newest log, using 2 queries in total.
    Returns (centers, latest_by_center).
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
    Same result as compute_congestion_risk() for every center, using a fixed number of
    queries. `latest_by_center` comes from fetch_latest_logs().
    Returns {center_id: result_dict}; a failing center gets {"error": "..."}.
    """
    centers = list(centers)
    now = timezone.now()

    capacities = {}
    results = {}
    for c in centers:
        try:
            capacities[c.id] = _capacity_of(c)
        except Exception as exc:
            results[c.id] = {"error": f"Prediction failed for this center: {exc}"}

    with_capacity = [cid for cid, cap in capacities.items() if cap > 0]
    flows: Dict[int, Tuple[int, int]] = {}
    points_by_center: Dict[int, list] = defaultdict(list)
    centers_per_barangay: Dict[int, int] = {}

    if with_capacity:
        # 1) in/out totals for the window
        since = now - timedelta(minutes=params.window_minutes)
        rows = (
            EvacuationLogModel.objects
            .filter(center_id__in=with_capacity, date_recorded__gte=since)
            .order_by()
            .values("center_id")
            .annotate(total_in=Sum("individuals_in"), total_out=Sum("individuals_out"))
        )
        flows = {
            r["center_id"]: (int(r["total_in"] or 0), int(r["total_out"] or 0))
            for r in rows
        }

        # 2) recent (time, total_current) points for Holt + event start
        recent = (
            EvacuationLogModel.objects
            .filter(
                center_id__in=with_capacity,
                date_recorded__gte=now - timedelta(hours=EVENT_LOOKBACK_HOURS),
            )
            .order_by("center_id", "date_recorded", "id")
            .values_list("center_id", "date_recorded", "total_current")
        )
        for cid, ts, total in recent:
            points_by_center[cid].append((ts, total))

        # 3) how many centers share each barangay (splits barangay population)
        barangay_ids = {getattr(c, "barangay_id", None) for c in centers} - {None}
        if barangay_ids and centers:
            CenterModel = centers[0].__class__
            centers_per_barangay = {
                r["barangay_id"]: r["n"]
                for r in (
                    CenterModel.objects
                    .filter(barangay_id__in=barangay_ids)
                    .order_by()
                    .values("barangay_id")
                    .annotate(n=Count("id"))
                )
            }

    for center in centers:
        if center.id in results:
            continue
        try:
            capacity = capacities[center.id]
            if capacity <= 0:
                results[center.id] = _no_capacity_result(center, capacity, params)
                continue

            all_points = points_by_center.get(center.id, [])
            total_in, total_out = flows.get(center.id, (0, 0))
            results[center.id] = _build_result(
                center=center,
                capacity=capacity,
                latest=latest_by_center.get(center.id),
                total_in=total_in,
                total_out=total_out,
                points=all_points[-HOLT_MAX_POINTS:],
                event_start=all_points[0][0] if all_points else None,
                centers_in_barangay=centers_per_barangay.get(getattr(center, "barangay_id", None), 1),
                params=params,
            )
        except Exception as exc:
            results[center.id] = {"error": f"Prediction failed for this center: {exc}"}

    return results