import logging

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Backup
from . import services
from .services import BackupError

CONFIRM_WORD = "RESTORE"
logger = logging.getLogger(__name__)


class IsBackupAdmin(BasePermission):
    """Backups contain every user's data, so only Provincial Admins (or superusers)."""
    message = "Only the Provincial Admin can manage backups."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated
            and (user.is_superuser or getattr(user, "role", None) == "PROVINCIAL_ADMIN")
        )


def _serialize(b):
    return {
        "id": b.id,
        "file_name": b.file_name,
        "kind": b.kind,
        "kind_label": b.get_kind_display(),
        "note": b.note,
        "size_bytes": b.size_bytes,
        "record_count": b.record_count,
        "model_counts": b.model_counts,
        "created_at": b.created_at,
        "created_by_name": b.created_by_name,
        "last_restored_at": b.last_restored_at,
        "last_restored_by_name": b.last_restored_by_name,
        "restore_count": b.restore_count,
    }


def _error(exc, code=status.HTTP_400_BAD_REQUEST):
    return Response({"detail": str(exc)}, status=code)


def _server_error(action, exc):
    """Print the full traceback in the server terminal and show the reason on the page."""
    logger.exception("%s failed", action)
    return Response(
        {"detail": f"{action} failed: {type(exc).__name__}: {exc}"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


class BackupListCreateView(APIView):
    """
    GET  /api/backups/         list backups + current row counts
    POST /api/backups/         {"note": "..."} create a backup now
    """
    permission_classes = [IsBackupAdmin]
    parser_classes = [JSONParser, FormParser]

    def get(self, request):
        try:
            backups = list(Backup.objects.all()[:200])
            counts = services.current_counts()
        except Exception as exc:
            return _server_error("Loading backups", exc)
        return Response({
            "results": [_serialize(b) for b in backups],
            "current_counts": counts,
            "storage": "bucket" if getattr(settings, "AWS_STORAGE_BUCKET_NAME", None) else "local",
        })

    def post(self, request):
        note = str(request.data.get("note", "") or "")
        try:
            backup = services.create_backup(request.user, Backup.Kind.MANUAL, note)
        except BackupError as exc:
            return _error(exc)
        except Exception as exc:
            return _server_error("Backup", exc)
        return Response(_serialize(backup), status=status.HTTP_201_CREATED)


class BackupUploadView(APIView):
    """POST /api/backups/upload/   multipart: file, note"""
    permission_classes = [IsBackupAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded = request.FILES.get("file")
        if not uploaded:
            return _error("Choose a backup file to upload.")
        try:
            backup = services.save_uploaded_backup(uploaded, request.user,
                                                   str(request.data.get("note", "") or ""))
        except BackupError as exc:
            return _error(exc)
        except Exception as exc:
            return _server_error("Upload", exc)
        return Response(_serialize(backup), status=status.HTTP_201_CREATED)


class BackupDetailView(APIView):
    """DELETE /api/backups/<id>/"""
    permission_classes = [IsBackupAdmin]

    def delete(self, request, pk):
        backup = get_object_or_404(Backup, pk=pk)
        try:
            services.delete_backup(backup, request.user)
        except Exception as exc:
            return _server_error("Delete", exc)
        return Response(status=status.HTTP_204_NO_CONTENT)


class BackupDownloadView(APIView):
    """GET /api/backups/<id>/download/   streams the file (never a public link)"""
    permission_classes = [IsBackupAdmin]

    def get(self, request, pk):
        backup = get_object_or_404(Backup, pk=pk)
        try:
            fh = backup.file.open("rb")
        except Exception:
            return _error("The backup file is missing from storage.", status.HTTP_404_NOT_FOUND)
        services._log("backup_downloaded", request.user, backup_id=backup.id, file=backup.file_name)
        return FileResponse(fh, as_attachment=True, filename=backup.file_name,
                            content_type="application/gzip")


class BackupRestoreView(APIView):
    """
    POST /api/backups/<id>/restore/   {"confirm": "RESTORE"}
    Replaces ALL current data with the backup. A safety copy is taken first.
    """
    permission_classes = [IsBackupAdmin]
    parser_classes = [JSONParser]

    def post(self, request, pk):
        backup = get_object_or_404(Backup, pk=pk)
        if str(request.data.get("confirm", "")).strip().upper() != CONFIRM_WORD:
            return _error(f'Type {CONFIRM_WORD} to confirm the restore.')
        try:
            safety = services.restore_backup(backup, request.user)
        except BackupError as exc:
            return _error(exc)
        except Exception as exc:  # loaddata/database error: transaction already rolled back
            logger.exception("Restore failed")
            return Response(
                {"detail": f"Restore failed and nothing was changed: {type(exc).__name__}: {exc}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        backup.refresh_from_db()
        return Response({
            "detail": "Restore complete.",
            "restored": _serialize(backup),
            "safety_backup": _serialize(safety),
        })