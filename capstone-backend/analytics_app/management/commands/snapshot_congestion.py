#analytics_app/management/commands/snapshot_congestion.py
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from evac_app.models import EvacuationCenter, EvacuationLog
from analytics_app.models import CongestionSnapshot
from analytics_app.services.congestion import (
    CongestionParams,
    EVENT_LOOKBACK_HOURS,
    compute_congestion_risk_bulk,
    fetch_latest_logs,
)


class Command(BaseCommand):
    help = (
        "Save a congestion prediction for every active center, and fill in the actual "
        "occupancy for older snapshots whose horizon has passed. Run every 30-60 minutes."
    )

    def add_arguments(self, parser):
        parser.add_argument("--horizon", type=int, default=60, help="Forecast horizon in minutes")
        parser.add_argument("--window", type=int, default=60, help="Inflow/outflow window in minutes")

    def handle(self, *args, **opts):
        created = self._take_snapshots(opts["window"], opts["horizon"])
        filled = self._fill_actuals()
        self.stdout.write(self.style.SUCCESS(
            f"Saved {created} snapshot(s); filled actuals for {filled} older snapshot(s)."
        ))

    def _take_snapshots(self, window, horizon):
        # Only centers with logs in the current event window (skip idle centers).
        since = timezone.now() - timedelta(hours=EVENT_LOOKBACK_HOURS)
        active_ids = (
            EvacuationLog.objects
            .filter(date_recorded__gte=since)
            .values_list("center_id", flat=True)
            .distinct()
        )
        centers_qs = EvacuationCenter.objects.filter(id__in=list(active_ids)).select_related("barangay")

        centers, latest_by_center = fetch_latest_logs(centers_qs, EvacuationLog)
        results = compute_congestion_risk_bulk(
            centers=centers,
            latest_by_center=latest_by_center,
            EvacuationLogModel=EvacuationLog,
            params=CongestionParams(window_minutes=window, horizon_minutes=horizon),
        )

        rows = []
        for center in centers:
            r = results.get(center.id) or {}
            if "error" in r or r.get("capacity", 0) <= 0:
                continue
            rows.append(CongestionSnapshot(
                center=center,
                horizon_minutes=horizon,
                model=r["model"],
                model_version=r["model_version"],
                capacity=r["capacity"],
                current_total=r["current_total"],
                predicted_total=r["predicted_total"],
                risk_score=r["risk_score"],
                risk_level=r["risk_level"],
                features={
                    "occupancy": r["occupancy"],
                    "net_rate_per_min": r["net_rate_per_min"],
                    "vulnerability_ratio": r["vulnerability_ratio"],
                    "data_points": r["data_points"],
                    "data_weight": r["data_weight"],
                    "expected_demand": r["expected_demand"],
                    "demand_source": r["demand_source"],
                    "flood_susceptibility": center.flood_susceptibility,
                    "landslide_susceptibility": center.landslide_susceptibility,
                    "hour_of_day": timezone.now().hour,
                },
            ))
        CongestionSnapshot.objects.bulk_create(rows)
        return len(rows)

    def _fill_actuals(self):
        now = timezone.now()
        filled = 0
        pending = CongestionSnapshot.objects.filter(actual_total_at_horizon__isnull=True)
        for snap in pending.iterator():
            target_time = snap.created_at + timedelta(minutes=snap.horizon_minutes)
            if target_time > now:
                continue
            log = (
                EvacuationLog.objects
                .filter(center_id=snap.center_id, date_recorded__lte=target_time)
                .order_by("-date_recorded", "-id")
                .only("total_current")
                .first()
            )
            snap.actual_total_at_horizon = int(log.total_current or 0) if log else 0
            snap.save(update_fields=["actual_total_at_horizon"])
            filled += 1
        return filled