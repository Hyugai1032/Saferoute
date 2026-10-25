#evac_app/management/commands/recalculate_log_totals.py
from django.core.management.base import BaseCommand
from django.db import transaction

from evac_app.models import EvacuationLog


class Command(BaseCommand):
    help = (
        "Rebuild total_current, total_current_families and vulnerable_individuals for "
        "every evacuation log, replaying each center's logs oldest -> newest. Fixes "
        "totals left stale by earlier log deletes or edits. Safe to run more than once."
    )

    def add_arguments(self, parser):
        parser.add_argument("--center", type=int, help="Only this center id")
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Report how many logs would change without saving",
        )

    def handle(self, *args, **opts):
        center_ids = (
            [opts["center"]] if opts["center"]
            else list(
                EvacuationLog.objects.order_by().values_list("center_id", flat=True).distinct()
            )
        )

        total_changed = 0
        for cid in center_ids:
            with transaction.atomic():
                sid = transaction.savepoint()
                changed = EvacuationLog.recalculate_center(cid)
                if opts["dry_run"]:
                    transaction.savepoint_rollback(sid)
                else:
                    transaction.savepoint_commit(sid)
            if changed:
                self.stdout.write(f"Center {cid}: {changed} log(s) corrected")
            total_changed += changed

        verb = "would be corrected" if opts["dry_run"] else "corrected"
        self.stdout.write(self.style.SUCCESS(
            f"{total_changed} log(s) {verb} across {len(center_ids)} center(s)."
        ))