"""Turning model field values into small, JSON-safe, comparable values."""
import datetime
import decimal
import functools
import json
import uuid

from django.db.models.fields.files import FieldFile

from . import conf

HIDDEN = "[hidden]"


def normalize(value):
    """A JSON-safe form of a field value, also used to decide whether it changed."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, decimal.Decimal):
        if not value.is_finite():
            return str(value)
        # 13.1200000 and 13.12 are the same value: compare and store them the same way.
        return format(value.normalize(), "f")
    if isinstance(value, (datetime.datetime, datetime.date, datetime.time)):
        return value.isoformat()
    if isinstance(value, datetime.timedelta):
        return value.total_seconds()
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, FieldFile):
        return value.name or None
    if isinstance(value, (bytes, bytearray, memoryview)):
        return f"<binary, {len(bytes(value)):,} bytes>"
    if isinstance(value, (dict, list, tuple)):
        return json.loads(json.dumps(value, default=str))
    return str(value)


def compact(value):
    """Keep stored values small: cut long text, replace big JSON with a size note."""
    limit = conf.max_value_chars()
    if isinstance(value, str) and len(value) > limit:
        return f"{value[:limit]}… (+{len(value) - limit:,} chars)"
    if isinstance(value, (dict, list)):
        text = json.dumps(value, default=str)
        if len(text) > limit:
            kind = "object" if isinstance(value, dict) else "list"
            return f"<{kind}, {len(text):,} chars>"
    return value


def is_redacted(field_name):
    name = field_name.lower()
    return any(part in name for part in conf.redact_fields())


@functools.lru_cache(maxsize=None)
def _audit_fields_cached(model, exclude_key):
    exclude = set(exclude_key)
    return tuple(
        f for f in model._meta.concrete_fields
        if not f.primary_key and f.name not in exclude and f.attname not in exclude
    )


def audit_fields(model, instance=None, update_fields=None):
    """
    Concrete fields worth comparing for this save. Skips the primary key, excluded
    fields, fields not loaded on this instance (deferred), and, when save() was called
    with update_fields, everything outside that list.
    """
    fields = _audit_fields_cached(model, tuple(sorted(conf.exclude_fields())))
    if update_fields is not None:
        wanted = set(update_fields)
        fields = tuple(f for f in fields if f.name in wanted or f.attname in wanted)
    if instance is not None:
        deferred = instance.get_deferred_fields()
        if deferred:
            fields = tuple(f for f in fields if f.attname not in deferred)
    return fields


def display_name(user):
    full = f"{getattr(user, 'first_name', '') or ''} {getattr(user, 'last_name', '') or ''}".strip()
    return full or getattr(user, "email", "") or str(user)


def label_for(obj):
    try:
        return str(obj)[:255]
    except Exception:
        return f"{type(obj).__name__} #{getattr(obj, 'pk', '?')}"
