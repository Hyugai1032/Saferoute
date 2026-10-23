from django.db import models
from django.utils import timezone


class AuditLog(models.Model):
    """
    One row per recorded event: a create / update / delete of a tracked model, or a
    security event (login, failed login, permission denied, data export).

    Kept deliberately narrow:
    - No foreign keys. Actor and municipality are plain ids plus name snapshots, so
      deleting a user never rewrites thousands of log rows and the history keeps
      saying who did it.
    - `details` holds only what changed: {"field": [old, new]} for updates, the
      initial values for creates, the final values for deletes.
    - Rows are append-only. save() refuses updates and delete() refuses deletes; old
      rows are removed only by the purge_audit_logs command.
    """

    class Action(models.TextChoices):
        CREATE = "CREATE", "Created"
        UPDATE = "UPDATE", "Updated"
        DELETE = "DELETE", "Deleted"
        LOGIN = "LOGIN", "Logged in"
        LOGIN_FAILED = "LOGIN_FAILED", "Failed login"
        PERMISSION_DENIED = "PERMISSION_DENIED", "Permission denied"
        EXPORT = "EXPORT", "Exported data"
        OTHER = "OTHER", "Other"

    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    action = models.CharField(max_length=20, choices=Action.choices, db_index=True)

    # Who (snapshot; actor_id stays even if the account is deleted)
    actor_id = models.PositiveBigIntegerField(null=True, blank=True, db_index=True)
    actor_email = models.CharField(max_length=191, blank=True, default="")
    actor_name = models.CharField(max_length=201, blank=True, default="")
    actor_role = models.CharField(max_length=30, blank=True, default="")

    # Used to scope what municipal admins can see
    municipality_id = models.PositiveIntegerField(null=True, blank=True, db_index=True)

    # What
    resource_type = models.CharField(max_length=64, blank=True, default="")
    resource_id = models.CharField(max_length=64, blank=True, default="")
    resource_label = models.CharField(max_length=255, blank=True, default="")
    details = models.JSONField(null=True, blank=True)

    # Request context
    method = models.CharField(max_length=8, blank=True, default="")
    path = models.CharField(max_length=255, blank=True, default="")
    status_code = models.PositiveSmallIntegerField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default="")
    request_id = models.CharField(max_length=32, blank=True, default="", db_index=True)

    class Meta:
        ordering = ["-id"]
        indexes = [
            models.Index(fields=["resource_type", "resource_id"], name="audit_resource_idx"),
        ]

    def __str__(self):
        who = self.actor_email or "system"
        what = f"{self.resource_type} #{self.resource_id}" if self.resource_type else self.path
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {who} {self.action} {what}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise PermissionError("Audit log entries are append-only and cannot be edited.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("Audit log entries cannot be deleted individually.")
