"""
Builds AuditLog rows and hands them to the current request's buffer (or writes them
directly when there is no request, e.g. a management command).
"""
import ipaddress
import logging

from django.db import transaction

from . import conf, context
from .models import AuditLog
from .values import display_name, label_for

logger = logging.getLogger(__name__)


def resource_fields(instance):
    """resource_type / resource_id / resource_label / municipality_id for a model instance."""
    if instance is None:
        return {}
    model = type(instance)
    mun_id = getattr(instance, "municipality_id", None)
    if mun_id is None and model.__name__ == "Municipality":
        mun_id = instance.pk
    return {
        "resource_type": model.__name__[:64],
        "resource_id": str(instance.pk)[:64] if instance.pk is not None else "",
        "resource_label": label_for(instance),
        "municipality_id": mun_id,
    }


def set_actor(entry, user):
    """Copy who did it onto the entry (snapshot, so it survives account deletion)."""
    if user is None or not getattr(user, "is_authenticated", False):
        return
    entry.actor_id = user.pk
    entry.actor_email = (getattr(user, "email", "") or "")[:191]
    entry.actor_name = display_name(user)[:201]
    entry.actor_role = (getattr(user, "role", "") or "")[:30]
    if entry.municipality_id is None:
        entry.municipality_id = getattr(user, "municipality_id", None)


def client_ip(request):
    meta = request.META
    candidate = None
    count = conf.proxy_count()
    forwarded = meta.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded and count > 0:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if parts:
            candidate = parts[-count] if len(parts) >= count else parts[0]
    candidate = candidate or meta.get("REMOTE_ADDR")
    try:
        return str(ipaddress.ip_address(candidate)) if candidate else None
    except ValueError:
        return None


def fill_request_info(entry, request, ctx, status_code, user):
    if entry.actor_id is None:
        set_actor(entry, user)
    entry.method = (request.method or "")[:8]
    entry.path = request.path[:255]
    entry.status_code = status_code
    entry.ip_address = client_ip(request)
    entry.user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:255]
    entry.request_id = ctx.request_id


def record(action, instance=None, details=None, using=None, user=None, **extra):
    """
    Queue one entry. It is only kept if the surrounding database transaction commits,
    so a change that gets rolled back never shows up in the log.
    """
    entry = AuditLog(action=action, details=details or None, **resource_fields(instance), **extra)
    if user is not None:
        set_actor(entry, user)
    ctx = context.get_context()

    def deliver():
        if ctx is not None:
            ctx.entries.append(entry)
        elif conf.log_outside_requests():
            try:
                entry.save()
            except Exception:
                logger.exception("Could not write audit log entry")

    transaction.on_commit(deliver, using=using)
    return entry


def log_event(action, request=None, instance=None, details=None, user=None):
    """
    Public helper for events that aren't plain model saves, e.g.:

        from audit_app.recorder import log_event
        from audit_app.models import AuditLog
        log_event(AuditLog.Action.OTHER, details={"event": "otp_sent", "email": email})

    Inside a request it joins that request's batch; outside one it is written directly.
    """
    entry = AuditLog(action=action, details=details or None, **resource_fields(instance))
    if user is not None:
        set_actor(entry, user)
    ctx = context.get_context()
    if ctx is not None:
        ctx.entries.append(entry)
    elif conf.log_outside_requests():
        entry.save()
    return entry
