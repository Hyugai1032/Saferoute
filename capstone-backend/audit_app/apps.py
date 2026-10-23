from django.apps import AppConfig


class AuditAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "audit_app"
    verbose_name = "System audit log"

    def ready(self):
        from .signals import connect_tracked_models
        connect_tracked_models()
