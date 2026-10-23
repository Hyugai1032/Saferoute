from django.urls import path

from .views import AuditLogExportView, AuditLogListView, AuditLogMetaView

urlpatterns = [
    path("audit-logs/", AuditLogListView.as_view(), name="audit-log-list"),
    path("audit-logs/export/", AuditLogExportView.as_view(), name="audit-log-export"),
    path("audit-logs/meta/", AuditLogMetaView.as_view(), name="audit-log-meta"),
]
