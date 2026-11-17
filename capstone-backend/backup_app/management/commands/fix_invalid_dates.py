"""
Find and repair invalid dates (e.g. MySQL "zero dates" 0000-00-00 00:00:00) that
stop backups from working.

    python manage.py fix_invalid_dates          # only lists the problem rows
    python manage.py fix_invalid_dates --fix    # repairs them

How a bad value is repaired:
- field allows empty (null=True)       -> set to empty (NULL)
- otherwise, e.g. updated_at           -> copied from another valid date on the same
                                          row (created_at first), else the current time
"""
import datetime

from django.core.management.base import BaseCommand
from django.db import models, transaction
from django.utils import timezone

from backup_app.services import find_invalid_dates

PREFERRED_SOURCES = ("created_at", "date_registered", "date_recorded", "updated_at")


def _replacement(problem):
    field = problem["field"]
    if field.null:
        return None, "empty"
    model, pk = problem["model"], problem["pk"]
    candidates = [f for f in model._meta.concrete_fields
                  if isinstance(f, type(field)) and f is not field]
    candidates.sort(key=lambda f: PREFERRED_SOURCES.index(f.name) if f.name in PREFERRED_SOURCES else 99)
    if candidates:
        row = model._base_manager.filter(pk=pk).values(*[f.attname for f in candidates]).first() or {}
        for f in candidates:
            value = row.get(f.attname)
            if isinstance(value, (datetime.date, datetime.time)):
                return value, f"copied from {f.name}"
    now = timezone.now()
    if isinstance(field, models.DateTimeField):
        return now, "current time"
    if isinstance(field, models.DateField):
        return now.date(), "today"
    return now.time().replace(microsecond=0), "current time"


class Command(BaseCommand):
    help = "List (and with --fix, repair) invalid dates that stop backups from working."

    def add_arguments(self, parser):
        parser.add_argument("--fix", action="store_true", help="Repair the rows (default: only list them).")

    def handle(self, *args, **opts):
        problems = find_invalid_dates()
        if not problems:
            self.stdout.write(self.style.SUCCESS("No invalid dates found."))
            return

        with transaction.atomic():
            for p in problems:
                new_value, how = _replacement(p)
                line = f"{p['label']} #{p['pk']}  {p['field'].name} = {p['value']!r}  ->  {new_value} ({how})"
                if opts["fix"]:
                    p["model"]._base_manager.filter(pk=p["pk"]).update(**{p["field"].attname: new_value})
                self.stdout.write(line)

        if opts["fix"]:
            self.stdout.write(self.style.SUCCESS(f"Repaired {len(problems)} value(s). Backups should work now."))
        else:
            self.stdout.write(self.style.WARNING(
                f"{len(problems)} invalid value(s) found. Run again with --fix to repair them."))