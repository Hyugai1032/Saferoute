"""
Scheduled backups.

    python manage.py create_backup              # one backup, keep the newest 14 scheduled ones
    python manage.py create_backup --keep 30

On Railway: add a Cron schedule to a service that runs this command
(e.g. "0 18 * * *" = 2:00 AM Philippine time every day).
"""
from django.core.management.base import BaseCommand

from backup_app.models import Backup
from backup_app.services import create_backup, prune_backups


class Command(BaseCommand):
    help = "Create a database backup and delete old scheduled backups."

    def add_arguments(self, parser):
        parser.add_argument("--keep", type=int, default=14,
                            help="How many scheduled backups to keep (default 14).")
        parser.add_argument("--note", default="", help="Optional note.")

    def handle(self, *args, **opts):
        backup = create_backup(None, Backup.Kind.SCHEDULED, opts["note"] or "Scheduled backup")
        removed = prune_backups(Backup.Kind.SCHEDULED, max(opts["keep"], 1))
        self.stdout.write(self.style.SUCCESS(
            f"Created {backup.file_name} ({backup.record_count} records). "
            f"Removed {removed} old scheduled backup(s)."
        ))
