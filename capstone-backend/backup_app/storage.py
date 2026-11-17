"""
Where backup files are kept.

- Railway bucket connected (AWS_STORAGE_BUCKET_NAME set): the bucket, under "backups/".
  The bucket is private and files are only ever streamed through the API, never linked.
- Otherwise (local dev): a "backups" folder next to manage.py. It is deliberately NOT
  inside MEDIA_ROOT, so backups are never served as public media files.

Note: Railway's own disk is wiped on every deploy, so production needs the bucket.
"""
from django.conf import settings
from django.core.files.storage import FileSystemStorage


def backup_storage():
    if getattr(settings, "AWS_STORAGE_BUCKET_NAME", None):
        from storages.backends.s3 import S3Storage
        return S3Storage(location="backups", file_overwrite=False)
    return FileSystemStorage(location=settings.BASE_DIR / "backups")
