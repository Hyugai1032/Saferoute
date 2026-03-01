from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional, Dict, Any

from django.db.models import Sum
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


def compute_congestion_risk(
    *,
    center,
    EvacuationLogModel,
    params: CongestionParams = CongestionParams(),
) -> Dict[str, Any]:
    """
    Hybrid Real-Time Congestion Risk Model (no training required)

    Requires:
      - center.capacity (int)
      - logs fields (based on your schema):
        date_recorded, individuals_in, individuals_out, total_current,
        children_count, lactating_count, pregnant_count, pwd_count, senior_count
    """

    capacity = getattr(center, "individual_capacity_max", None)
    if not capacity or capacity <= 0:
        return {
            "center_id": center.id,
            "error": "Center capacity is missing or invalid.",
        }

    # 1) latest snapshot
    latest = (
        EvacuationLogModel.objects
        .filter(center_id=center.id)
        .order_by("-date_recorded")
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

    total_in = int(agg["total_in"] or 0)
    total_out = int(agg["total_out"] or 0)

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