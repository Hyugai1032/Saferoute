from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only: nobody can add, edit or delete entries from the Django admin."""
    list_display = ("timestamp", "action", "actor_email", "resource_type", "resource_id",
                    "status_code", "ip_address")
    list_filter = ("action", "resource_type")
    search_fields = ("actor_email", "resource_label", "path", "request_id")
    ordering = ("-id",)
    show_full_result_count = False  # avoid COUNT(*) on a big table

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
