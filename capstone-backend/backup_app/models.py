from django.db import models
from django.utils import timezone

from .storage import backup_storage


class Backup(models.Model):
    """
    One backup file (gzipped Django fixture) plus what is known about it.

    No foreign key to the user: a restore replaces the users table, so the creator is
    kept as a plain id + name snapshot (same idea as audit_app.AuditLog).
    This table and the audit log are never touched by a restore, so the list of
    backups and the history of who restored what survive every restore.
    """

    class Kind(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        SCHEDULED = "SCHEDULED", "Scheduled"
        PRE_RESTORE = "PRE_RESTORE", "Safety copy (before restore)"
        UPLOADED = "UPLOADED", "Uploaded"

    file = models.FileField(storage=backup_storage, upload_to="", max_length=255)
    file_name = models.CharField(max_length=255)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.MANUAL, db_index=True)
    note = models.CharField(max_length=255, blank=True, default="")

    size_bytes = models.PositiveBigIntegerField(default=0)
    record_count = models.PositiveIntegerField(default=0)
    model_counts = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_by_id = models.PositiveBigIntegerField(null=True, blank=True)
    created_by_name = models.CharField(max_length=201, blank=True, default="")

    last_restored_at = models.DateTimeField(null=True, blank=True)
    last_restored_by_name = models.CharField(max_length=201, blank=True, default="")
    restore_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.file_name} ({self.get_kind_display()})"
