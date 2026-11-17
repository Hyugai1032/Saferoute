from django.contrib import admin

from .models import Backup


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    list_display = ("id", "file_name", "kind", "record_count", "size_bytes", "created_at", "created_by_name")
    list_filter = ("kind",)
    readonly_fields = [f.name for f in Backup._meta.fields]
