"""
Remove audit entries older than the retention period, in small batches so the table
is never locked for long.

    python manage.py purge_audit_logs      # ordinary entries: AUDIT_RETENTION_DAYS (30),
                                           # route requests: AUDIT_ROUTE_RETENTION_DAYS (14)
    python manage.py purge_audit_logs --days 60 --route-days 7
    python manage.py purge_audit_logs --archive logs_2025.csv.gz   # save rows before deleting
    python manage.py purge_audit_logs --dry-run

Run it on a schedule (e.g. a Railway cron service, once a week).
"""
import csv
import datetime
import gzip
import json
import os

from django.db.models import Q
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from audit_app import conf
from audit_app.models import AuditLog

FIELDS = [
    "id", "timestamp", "action", "actor_id", "actor_email", "actor_name", "actor_role",
    "municipality_id", "resource_type", "resource_id", "resource_label", "details",
    "method", "path", "status_code", "ip_address", "user_agent", "request_id",
]


class Command(BaseCommand):
    help = "Delete audit log entries older than the retention period."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=None,
                            help="Keep ordinary entries this many days (default: AUDIT_RETENTION_DAYS).")
        parser.add_argument("--route-days", type=int, default=None,
                            help="Keep route requests this many days (default: AUDIT_ROUTE_RETENTION_DAYS).")
        parser.add_argument("--archive", default=None,
                            help="Append deleted rows to this .csv.gz file first.")
        parser.add_argument("--batch", type=int, default=5000)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, days=None, route_days=None, archive=None, batch=5000, dry_run=False, **opts):
        days = conf.retention_days() if days is None else days
        route_days = conf.route_retention_days() if route_days is None else route_days
        if days < 1 or route_days < 1:
            raise CommandError("--days and --route-days must be at least 1.")
        now = timezone.now()
        cutoff = now - datetime.timedelta(days=days)
        route_cutoff = now - datetime.timedelta(days=route_days)
        route = AuditLog.Action.ROUTE
        old = AuditLog.objects.filter(
            Q(timestamp__lt=cutoff) | Q(action=route, timestamp__lt=route_cutoff)
        )

        if dry_run:
            self.stdout.write(f"{old.count():,} entries would be removed (older than {cutoff:%Y-%m-%d}, route requests older than {route_cutoff:%Y-%m-%d}).")
            return

        writer = handle = None
        if archive:
            new_file = not os.path.exists(archive)
            handle = gzip.open(archive, "at", newline="", encoding="utf-8")
            writer = csv.writer(handle)
            if new_file:
                writer.writerow(FIELDS)

        total = 0
        try:
            while True:
                ids = list(old.order_by("id").values_list("id", flat=True)[:batch])
                if not ids:
                    break
                if writer:
                    for row in AuditLog.objects.filter(id__in=ids).order_by("id").values_list(*FIELDS):
                        row = list(row)
                        row[FIELDS.index("details")] = json.dumps(row[FIELDS.index("details")], default=str)
                        writer.writerow(row)
                # QuerySet.delete: one DELETE per batch (AuditLog has no relations to cascade).
                deleted, _ = AuditLog.objects.filter(id__in=ids).delete()
                total += deleted
        finally:
            if handle:
                handle.close()

        self.stdout.write(self.style.SUCCESS(
            f"Removed {total:,} audit entries (older than {cutoff:%Y-%m-%d}, route requests older than {route_cutoff:%Y-%m-%d})"
            + (f" (archived to {archive})" if archive else "") + "."
        ))
