"""
Backup and restore logic, shared by the API views and the create_backup command.

Format: a gzipped Django fixture (the same thing `manage.py dumpdata` writes). That
means a backup can also be restored by hand with `manage.py loaddata <file>.json.gz`
if the website itself is down, and it does not need the `mysqldump` program, which
Railway's Python container does not have.

What is included: every model of the apps in BACKUP_APP_LABELS (users, municipalities,
barangays, hazard reports, evacuation centers, logs, evacuees, donations, congestion
snapshots, groups...).

What is NOT included, on purpose:
- audit_app (system logs): append-only history, must survive a restore so you can
  still see who restored what and when.
- backup_app: the list of backups itself (otherwise restoring an old backup would
  forget every newer backup).
- auth.Permission / contenttypes: rebuilt by `migrate`; referenced by natural keys.
- sessions, admin log entries: temporary / not needed.
- Uploaded files (hazard photos) are stored in the bucket, not in the database; the
  backup keeps their file paths, not the image files.
"""
import datetime
import gzip
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection, models, transaction
from django.utils import timezone

from .models import Backup

DEFAULT_APP_LABELS = ["auth", "auth_app", "evac_app", "analytics_app"]
DEFAULT_EXCLUDED_MODELS = ["auth.permission"]

# A gzipped upload can expand a lot; refuse anything that unpacks past this.
MAX_UNCOMPRESSED_BYTES = getattr(settings, "BACKUP_MAX_UNCOMPRESSED_MB", 1024) * 1024 * 1024
MAX_UPLOAD_BYTES = getattr(settings, "BACKUP_MAX_UPLOAD_MB", 200) * 1024 * 1024


class BackupError(Exception):
    """Something the admin should be told about (bad file, missing file...)."""


def app_labels():
    return list(getattr(settings, "BACKUP_APP_LABELS", DEFAULT_APP_LABELS))


def excluded_models():
    return {m.lower() for m in getattr(settings, "BACKUP_EXCLUDED_MODELS", DEFAULT_EXCLUDED_MODELS)}


def restorable_models(include_auto_created=False):
    """Models whose tables a restore empties and refills."""
    labels, excluded = set(app_labels()), excluded_models()
    for model in apps.get_models(include_auto_created=include_auto_created):
        meta = model._meta
        if meta.app_label not in labels or meta.label_lower in excluded:
            continue
        if meta.proxy or not meta.managed:
            continue
        yield model


def _display_name(user):
    if user is None:
        return "System (scheduled)"
    full = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
    return (full or getattr(user, "email", "") or f"User #{user.pk}")[:201]


def _log(event, user=None, **details):
    """Write an entry to the System Logs. Never lets logging break a backup."""
    try:
        from audit_app.models import AuditLog
        from audit_app.recorder import log_event
        log_event(AuditLog.Action.OTHER, details={"event": event, **details}, user=user)
    except Exception:
        pass


# ---------------------------------------------------------------- reading files

def _open_fixture(path):
    path = str(path)
    if path.endswith(".gz"):
        return gzip.open(path, "rb")
    return open(path, "rb")


def read_fixture(path):
    """Load and check a fixture file. Returns the list of objects."""
    allowed = {m._meta.label_lower for m in restorable_models()}
    try:
        with _open_fixture(path) as fh:
            raw = fh.read(MAX_UNCOMPRESSED_BYTES + 1)
    except (OSError, EOFError, gzip.BadGzipFile):
        raise BackupError("The file is not a valid SafeRoute+ backup (could not be unpacked).")
    if len(raw) > MAX_UNCOMPRESSED_BYTES:
        raise BackupError("The backup file is too large to restore.")
    try:
        objects = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise BackupError("The file is not a valid SafeRoute+ backup (not readable JSON).")

    if not isinstance(objects, list):
        raise BackupError("The file is not a valid SafeRoute+ backup (unexpected format).")
    for obj in objects:
        if not isinstance(obj, dict) or not isinstance(obj.get("fields"), dict):
            raise BackupError("The file is not a valid SafeRoute+ backup (unexpected format).")
        label = str(obj.get("model", "")).lower()
        if label not in allowed:
            raise BackupError(f"The backup contains data this system does not restore: {label!r}.")
    return objects


def _counts(objects):
    return dict(sorted(Counter(o["model"].lower() for o in objects).items()))


def current_counts():
    """Row counts of what a restore would replace, for the confirmation screen."""
    return {m._meta.label_lower: m._base_manager.count() for m in restorable_models()}


# ---------------------------------------------------------------- invalid dates

def _expected_type(field):
    if isinstance(field, models.DateTimeField):
        return datetime.datetime
    if isinstance(field, models.DateField):
        return datetime.date
    return datetime.time


def find_invalid_dates():
    """
    Rows whose date/time columns hold something that is not a real date, usually
    MySQL "zero dates" (0000-00-00 00:00:00). MySQL/MariaDB accept them when strict
    mode is off (XAMPP default, phpMyAdmin edits, SQL imports), but Python cannot
    read them, so they cannot be backed up.

    Note: no "IS NULL" filter on purpose; MySQL reports zero dates in NOT NULL
    columns as NULL, which would hide exactly the rows we are looking for.
    """
    problems = []
    for model in restorable_models():
        fields = [f for f in model._meta.concrete_fields
                  if isinstance(f, (models.DateField, models.TimeField))]
        for f in fields:
            expected = _expected_type(f)
            rows = model._base_manager.values_list("pk", f.attname).iterator()
            for pk, value in rows:
                if value is not None and not isinstance(value, expected):
                    problems.append({
                        "model": model, "label": model._meta.label,
                        "pk": pk, "field": f, "value": str(value),
                    })
    return problems


def describe_invalid_dates(problems, limit=5):
    lines = [f"{p['label']} #{p['pk']} {p['field'].name} = {p['value']!r}" for p in problems[:limit]]
    more = f" (and {len(problems) - limit} more)" if len(problems) > limit else ""
    return "; ".join(lines) + more


# ---------------------------------------------------------------- create

def _save_backup_file(local_path, file_name, kind, user, note, objects):
    backup = Backup(
        file_name=file_name,
        kind=kind,
        note=(note or "")[:255],
        size_bytes=os.path.getsize(local_path),
        record_count=len(objects),
        model_counts=_counts(objects),
        created_by_id=getattr(user, "pk", None),
        created_by_name=_display_name(user),
    )
    with open(local_path, "rb") as fh:
        backup.file.save(file_name, File(fh), save=False)
    # Storage may add a suffix if the name is taken; show the real stored name.
    backup.file_name = Path(backup.file.name).name[:255]
    backup.save()
    return backup


def create_backup(user=None, kind=Backup.Kind.MANUAL, note=""):
    stamp = timezone.now().strftime("%Y%m%d-%H%M%S")
    file_name = f"saferoute-{kind.lower().replace('_', '-')}-{stamp}.json.gz"
    tmp_dir = tempfile.mkdtemp(prefix="saferoute-backup-")
    try:
        local_path = os.path.join(tmp_dir, file_name)
        try:
            # Open the file ourselves as UTF-8. dumpdata's own `output=` option opens
            # .gz files without an encoding, which on Windows means cp1252: names
            # with ñ etc. then come out unreadable.
            with gzip.open(local_path, "wt", encoding="utf-8") as stream:
                call_command(
                    "dumpdata",
                    *app_labels(),
                    exclude=sorted(excluded_models()),
                    natural_foreign=True,      # permissions/content types by name, not by id
                    stdout=stream,
                    verbosity=0,
                )
        except CommandError:
            problems = find_invalid_dates()
            if problems:
                raise BackupError(
                    f"{len(problems)} record(s) have invalid dates and cannot be backed up: "
                    f"{describe_invalid_dates(problems)}. "
                    "Run: python manage.py fix_invalid_dates --fix"
                )
            raise
        objects = read_fixture(local_path)
        backup = _save_backup_file(local_path, file_name, kind, user, note, objects)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    _log("backup_created", user, backup_id=backup.id, file=backup.file_name,
         kind=kind, records=backup.record_count)
    return backup


def save_uploaded_backup(uploaded_file, user=None, note=""):
    """Store a backup file the admin uploaded (e.g. one downloaded earlier)."""
    name = Path(uploaded_file.name or "").name
    if not (name.endswith(".json.gz") or name.endswith(".json")):
        raise BackupError("Upload a .json.gz backup file downloaded from this page.")
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise BackupError("The file is too large.")

    suffix = ".json.gz" if name.endswith(".json.gz") else ".json"
    tmp_dir = tempfile.mkdtemp(prefix="saferoute-upload-")
    try:
        local_path = os.path.join(tmp_dir, "upload" + suffix)
        with open(local_path, "wb") as out:
            for chunk in uploaded_file.chunks():
                out.write(chunk)
        objects = read_fixture(local_path)  # reject bad files before storing them
        if not objects:
            raise BackupError("The backup file is empty.")
        stamp = timezone.now().strftime("%Y%m%d-%H%M%S")
        file_name = f"saferoute-uploaded-{stamp}{suffix}"
        backup = _save_backup_file(local_path, file_name, Backup.Kind.UPLOADED, user,
                                   note or f"Uploaded from {name}"[:255], objects)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    _log("backup_uploaded", user, backup_id=backup.id, original_name=name[:100],
         records=backup.record_count)
    return backup


# ---------------------------------------------------------------- restore

def _wipe_restorable_tables():
    """Empty every table the backup covers (including many-to-many link tables)."""
    tables = [m._meta.db_table for m in restorable_models(include_auto_created=True)]
    qn = connection.ops.quote_name
    # DELETE (not TRUNCATE): TRUNCATE commits on MySQL and would break the
    # all-or-nothing transaction below.
    with connection.constraint_checks_disabled():
        with connection.cursor() as cursor:
            for table in tables:
                cursor.execute(f"DELETE FROM {qn(table)}")


def restore_backup(backup, user=None):
    """
    Replace the current data with the contents of `backup`.

    1. A safety copy of the current data is saved first (kind PRE_RESTORE), so a
       wrong restore can itself be undone.
    2. The file is checked before anything is deleted.
    3. Delete + load run in one transaction: if anything fails, nothing changes.

    Returns the safety copy.
    """
    if not backup.file or not backup.file.storage.exists(backup.file.name):
        raise BackupError("The backup file is missing from storage.")

    suffix = ".json.gz" if backup.file_name.endswith(".gz") else ".json"
    tmp_dir = tempfile.mkdtemp(prefix="saferoute-restore-")
    try:
        local_path = os.path.join(tmp_dir, "restore" + suffix)
        with backup.file.open("rb") as src, open(local_path, "wb") as dst:
            shutil.copyfileobj(src, dst)
        read_fixture(local_path)

        safety = create_backup(
            user, kind=Backup.Kind.PRE_RESTORE,
            note=f"Automatic copy taken before restoring backup #{backup.id}",
        )

        with transaction.atomic():
            _wipe_restorable_tables()
            call_command("loaddata", local_path, verbosity=0)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    Backup.objects.filter(pk=backup.pk).update(
        last_restored_at=timezone.now(),
        last_restored_by_name=_display_name(user),
        restore_count=backup.restore_count + 1,
    )
    _log("backup_restored", user, backup_id=backup.id, file=backup.file_name,
         safety_backup_id=safety.id, records=backup.record_count)
    return safety


# ---------------------------------------------------------------- delete / prune

def delete_backup(backup, user=None):
    name, pk = backup.file_name, backup.pk
    if backup.file:
        try:
            backup.file.delete(save=False)
        except Exception:
            pass  # file already gone; still remove the row
    backup.delete()
    _log("backup_deleted", user, backup_id=pk, file=name)


def prune_backups(kind, keep):
    """Keep only the newest `keep` backups of one kind (used by scheduled backups)."""
    old = Backup.objects.filter(kind=kind).order_by("-created_at", "-id")[keep:]
    removed = 0
    for backup in list(old):
        delete_backup(backup)
        removed += 1
    return removed