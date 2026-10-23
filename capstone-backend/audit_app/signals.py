"""
Records create / update / delete of the models listed in AUDIT_TRACKED_MODELS.

Cost per save of a tracked model:
- create: nothing extra (values come from the instance in memory)
- update: one primary-key SELECT of only the fields being saved, to find what changed
- delete: nothing extra
Untracked models (most of the app) pay nothing.

Not covered by Django signals, so not logged: QuerySet.update(), bulk_create(),
bulk_update(), raw SQL, and many-to-many changes.
"""
import logging

from django.apps import apps
from django.db.models.signals import post_delete, post_save, pre_save

from . import conf
from .models import AuditLog
from .recorder import record
from .values import HIDDEN, audit_fields, compact, is_redacted, label_for, normalize

logger = logging.getLogger(__name__)

_OLD = "_audit_old_values"


def connect_tracked_models():
    for label in conf.tracked_models():
        try:
            model = apps.get_model(label)
        except (LookupError, ValueError):
            logger.warning("AUDIT_TRACKED_MODELS: model %r not found, skipping.", label)
            continue
        uid = f"audit_app:{label}"
        pre_save.connect(_pre_save, sender=model, dispatch_uid=f"{uid}:pre", weak=False)
        post_save.connect(_post_save, sender=model, dispatch_uid=f"{uid}:post", weak=False)
        post_delete.connect(_post_delete, sender=model, dispatch_uid=f"{uid}:delete", weak=False)


def _pre_save(sender, instance, raw=False, update_fields=None, using=None, **kwargs):
    instance.__dict__.pop(_OLD, None)
    if raw or instance._state.adding or instance.pk is None:
        return
    fields = audit_fields(sender, instance, update_fields)
    if not fields:
        return
    row = (
        sender._base_manager.using(using or instance._state.db)
        .filter(pk=instance.pk)
        .values(*[f.attname for f in fields])
        .first()
    )
    instance.__dict__[_OLD] = row


def _related_labels(field, ids):
    """Readable names for changed foreign keys: one small query, only when an FK changed."""
    ids = [i for i in ids if i is not None]
    if not ids:
        return {}
    try:
        objs = field.related_model._base_manager.filter(pk__in=ids)
        return {normalize(o.pk): f"{label_for(o)} (#{o.pk})" for o in objs}
    except Exception:
        return {}


def _snapshot(instance, fields):
    """Non-empty field values, for CREATE and DELETE entries."""
    data = {}
    for f in fields:
        value = normalize(getattr(instance, f.attname, None))
        if value in (None, "", [], {}):
            continue
        if is_redacted(f.name):
            data[f.name] = HIDDEN
            continue
        if f.is_relation and f.many_to_one and f.is_cached(instance):
            related = f.get_cached_value(instance)
            if related is not None:
                value = f"{label_for(related)} (#{related.pk})"
        data[f.name] = compact(value)
    return data


def _post_save(sender, instance, created, raw=False, update_fields=None, using=None, **kwargs):
    if raw:
        return
    old = instance.__dict__.pop(_OLD, None)
    fields = audit_fields(sender, instance, update_fields)

    if created:
        record(AuditLog.Action.CREATE, instance, _snapshot(instance, fields), using=using)
        return

    if old is None:
        return  # nothing to compare against (no tracked fields, or the row vanished)

    changes = {}
    for f in fields:
        before = normalize(old.get(f.attname))
        after = normalize(getattr(instance, f.attname, None))
        if before == after:
            continue
        if is_redacted(f.name):
            changes[f.name] = [HIDDEN, HIDDEN]
        elif f.is_relation and f.many_to_one:
            labels = _related_labels(f, [before, after])
            changes[f.name] = [labels.get(before, before), labels.get(after, after)]
        else:
            changes[f.name] = [compact(before), compact(after)]

    if changes:
        record(AuditLog.Action.UPDATE, instance, changes, using=using)


def _post_delete(sender, instance, using=None, **kwargs):
    fields = audit_fields(sender, instance)
    record(AuditLog.Action.DELETE, instance, _snapshot(instance, fields), using=using)
