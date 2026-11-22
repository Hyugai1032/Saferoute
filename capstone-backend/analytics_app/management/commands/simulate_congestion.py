#analytics_app/management/commands/simulate_congestion.py
"""
DEV ONLY. Replays a made-up evacuation at one center, log by log, and grades the
congestion forecast against what the scenario says actually happened.

    python manage.py simulate_congestion --center 12 --scenario surge
    python manage.py simulate_congestion --center 12 --cleanup

At each step it adds one back-dated log, asks the model for a prediction "as of" that
moment (only the logs up to then exist), and later compares it with the scenario's real
count at that time + horizon. It also scores a "no change" baseline: the model is only
useful if it beats that.

Every log it writes has remarks "[SIMULATION]", so --cleanup removes exactly those.
"""
import math
import random
from datetime import timedelta
from unittest import mock

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from evac_app.models import EvacuationCenter, EvacuationLog
from analytics_app.services.congestion import (
    CongestionParams,
    compute_congestion_risk,
    compute_congestion_risk_bulk,
    fetch_latest_logs,
)

TAG = "[SIMULATION]"
SCENARIOS = ["surge", "steady", "emptying", "sparse"]


def _scenario_flows(name, capacity, steps, rng):
    """Return a list of (individuals_in, individuals_out) per step."""
    flows = []
    if name in ("surge", "sparse"):
        # S-curve arrivals up to ~110% of capacity
        peak, k, mid = capacity * 1.1, 0.5, steps * 0.45
        prev = 0.0
        for i in range(1, steps + 1):
            cum = peak / (1 + math.exp(-k * (i - mid)))
            arrivals = max(0, round((cum - prev) * rng.uniform(0.8, 1.2)))
            prev = cum
            flows.append((arrivals, 0))
    elif name == "steady":
        per_step = max(1, round(capacity * 0.06))
        flows = [(max(0, round(per_step * rng.uniform(0.7, 1.3))), 0) for _ in range(steps)]
    elif name == "emptying":
        fill_steps = max(1, steps // 3)
        per_in = max(1, round(capacity * 0.7 / fill_steps))
        per_out = max(1, round(capacity * 0.7 / max(1, steps - fill_steps)))
        for i in range(steps):
            if i < fill_steps:
                flows.append((round(per_in * rng.uniform(0.8, 1.2)), 0))
            else:
                flows.append((0, round(per_out * rng.uniform(0.8, 1.2))))
    return flows


class Command(BaseCommand):
    help = "DEV ONLY: replay a simulated evacuation at a center and grade the congestion forecast."

    def add_arguments(self, parser):
        parser.add_argument("--center", type=int, help="Evacuation center id")
        parser.add_argument("--scenario", choices=SCENARIOS, default="surge")
        parser.add_argument("--hours", type=int, default=12, help="Length of the simulated event")
        parser.add_argument("--interval", type=int, default=30, help="Minutes between logs")
        parser.add_argument("--horizon", type=int, default=60, help="Forecast horizon in minutes")
        parser.add_argument("--seed", type=int, default=7, help="Random seed (same seed = same run)")
        parser.add_argument("--keep", action="store_true",
                            help="Keep the simulated logs afterwards (to look at them in the UI)")
        parser.add_argument("--cleanup", action="store_true",
                            help="Only delete simulated logs (of --center, or all if omitted)")
        parser.add_argument("--force", action="store_true", help="Allow running with DEBUG=False")

    # ------------------------------------------------------------------ #
    def handle(self, *args, **o):
        if not settings.DEBUG and not o["force"]:
            raise CommandError("Refusing to run with DEBUG=False (production?). Add --force if this is a dev server.")

        if o["cleanup"]:
            return self._cleanup(o["center"])

        if not o["center"]:
            raise CommandError("--center is required")
        center = EvacuationCenter.objects.select_related("barangay").filter(pk=o["center"]).first()
        if not center:
            raise CommandError(f"Center {o['center']} not found")
        capacity = int(center.individual_capacity_max or 0)
        if capacity <= 0:
            raise CommandError("This center has no individual_capacity_max set")

        real_logs = EvacuationLog.objects.filter(center=center).exclude(remarks=TAG).count()
        if real_logs:
            raise CommandError(
                f"Center already has {real_logs} real log(s). Pick a center with none, so the test "
                "doesn't mix with real data."
            )
        self._cleanup(center.id, quiet=True)   # remove leftovers from an earlier run

        steps = max(2, o["hours"] * 60 // o["interval"])
        rng = random.Random(o["seed"])
        flows = _scenario_flows(o["scenario"], capacity, steps, rng)

        now = timezone.now().replace(microsecond=0)
        start = now - timedelta(minutes=steps * o["interval"])
        times = [start + timedelta(minutes=(i + 1) * o["interval"]) for i in range(steps)]

        # True occupancy after each step, according to the scenario
        truth, total = [], 0
        for i_in, i_out in flows:
            total = max(0, total + i_in - i_out)
            truth.append(total)

        def actual_at(t):
            value = 0
            for ts, v in zip(times, truth):
                if ts <= t:
                    value = v
            return value

        params = CongestionParams(horizon_minutes=o["horizon"])
        horizon = timedelta(minutes=o["horizon"])
        rows = []
        pending_in = pending_out = 0

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"\n{center.name} (id {center.id}) | capacity {capacity} | scenario '{o['scenario']}' | "
            f"{steps} steps x {o['interval']} min | horizon {o['horizon']} min\n"
        ))
        self.stdout.write(f"{'time':>5}  {'now':>5}  {'pred':>5}  {'actual':>6}  {'error':>5}  "
                          f"{'risk':<9} {'model':<8}")

        for i, (t, (i_in, i_out)) in enumerate(zip(times, flows)):
            pending_in += i_in
            pending_out += i_out
            # "sparse": staff only log every 3rd step (people still arrive in between)
            if o["scenario"] == "sparse" and (i + 1) % 3 and i != steps - 1:
                continue

            with transaction.atomic():
                EvacuationLog.objects.create(
                    center=center, date_recorded=t,
                    individuals_in=pending_in, individuals_out=pending_out,
                    children_count=round(pending_in * 0.25), senior_count=round(pending_in * 0.08),
                    children_out=round(pending_out * 0.25), senior_out=round(pending_out * 0.08),
                    remarks=TAG,
                )
            pending_in = pending_out = 0

            # Ask the model as if it were time t (only logs up to t exist yet)
            with mock.patch("django.utils.timezone.now", return_value=t):
                r = compute_congestion_risk(center=center, EvacuationLogModel=EvacuationLog, params=params)

            target = t + horizon
            actual = actual_at(target) if target <= times[-1] else None
            err = None if actual is None else r["predicted_total"] - actual
            rows.append((r["current_total"], r["predicted_total"], actual, r["risk_level"]))
            self.stdout.write(
                f"{t:%H:%M}  {r['current_total']:>5}  {r['predicted_total']:>5}  "
                f"{'-' if actual is None else actual:>6}  {'' if err is None else f'{err:+d}':>5}  "
                f"{r['risk_level']:<9} {r['model']:<8}"
            )

        self._report(rows, capacity)
        self._neighbors(center, params)

        if o["keep"]:
            self.stdout.write(self.style.WARNING(
                f"\nLogs kept. Remove them later with: python manage.py simulate_congestion --cleanup --center {center.id}"
            ))
        else:
            self._cleanup(center.id, quiet=True)
            self.stdout.write("\nSimulated logs removed (use --keep to look at them in the UI).")

    # ------------------------------------------------------------------ #
    def _report(self, rows, capacity):
        scored = [r for r in rows if r[2] is not None]
        if not scored:
            self.stdout.write(self.style.WARNING("\nNot enough steps to score (make --hours longer)."))
            return
        mae_model = sum(abs(p - a) for _, p, a, _ in scored) / len(scored)
        mae_base = sum(abs(c - a) for c, _, a, _ in scored) / len(scored)

        # Early warning: did it say HIGH/CRITICAL before the center actually hit 85%?
        warned = [r[3] in ("HIGH", "CRITICAL") for r in scored]
        crowded = [r[2] >= 0.85 * capacity for r in scored]
        hits = sum(w and c for w, c in zip(warned, crowded))
        misses = sum((not w) and c for w, c in zip(warned, crowded))
        false_alarms = sum(w and (not c) for w, c in zip(warned, crowded))

        self.stdout.write(self.style.MIGRATE_HEADING(f"\nScore over {len(scored)} prediction(s)"))
        self.stdout.write(f"  Model MAE:              {mae_model:6.1f} people")
        self.stdout.write(f"  'No change' MAE:        {mae_base:6.1f} people")
        if mae_base > 0:
            better = (1 - mae_model / mae_base) * 100
            style = self.style.SUCCESS if better > 0 else self.style.ERROR
            self.stdout.write(style(f"  Model vs baseline:      {better:+.0f}% "
                                    f"({'better' if better > 0 else 'worse'})"))
        self.stdout.write(f"  HIGH/CRITICAL warnings: {hits} correct, {misses} missed, {false_alarms} false alarm(s) "
                          f"(crowded = actual >= 85% of capacity)")

    def _neighbors(self, center, params):
        """Other centers in the same municipality should now show prior predictions."""
        if not center.municipality_id:
            return
        qs = (EvacuationCenter.objects
              .filter(municipality_id=center.municipality_id, individual_capacity_max__gt=0)
              .exclude(pk=center.pk).select_related("barangay")[:5])
        centers, latest = fetch_latest_logs(qs, EvacuationLog)
        if not centers:
            return
        res = compute_congestion_risk_bulk(centers=centers, latest_by_center=latest,
                                           EvacuationLogModel=EvacuationLog, params=params)
        self.stdout.write(self.style.MIGRATE_HEADING("\nOther centers in the same municipality (right now)"))
        for c in centers:
            r = res[c.id]
            if "error" in r:
                continue
            self.stdout.write(f"  {c.name[:32]:<32} now {r['current_total']:>4}  pred {r['predicted_total']:>4}  "
                              f"{r['risk_level']:<9} {r['model']}")

    def _cleanup(self, center_id=None, quiet=False):
        qs = EvacuationLog.objects.filter(remarks=TAG)
        if center_id:
            qs = qs.filter(center_id=center_id)
        center_ids = set(qs.values_list("center_id", flat=True))
        with transaction.atomic():
            n, _ = qs.delete()
        for cid in center_ids:
            EvacuationLog.recalculate_center(cid)
        if not quiet:
            self.stdout.write(self.style.SUCCESS(f"Deleted {n} simulated log(s)."))