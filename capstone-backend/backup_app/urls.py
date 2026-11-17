from django.urls import path

from .views import (
    BackupDetailView,
    BackupDownloadView,
    BackupListCreateView,
    BackupRestoreView,
    BackupUploadView,
)

urlpatterns = [
    path("backups/", BackupListCreateView.as_view(), name="backup-list"),
    path("backups/upload/", BackupUploadView.as_view(), name="backup-upload"),
    path("backups/<int:pk>/", BackupDetailView.as_view(), name="backup-detail"),
    path("backups/<int:pk>/download/", BackupDownloadView.as_view(), name="backup-download"),
    path("backups/<int:pk>/restore/", BackupRestoreView.as_view(), name="backup-restore"),
]
