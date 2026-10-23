"""
Per-request buffer. Model signals add entries here instead of writing them one by one;
the middleware writes the whole buffer in a single INSERT once the response is ready.
That keeps logging to one query per request and lets every entry carry the request's
final status code and the user DRF authenticated (which is only known after the view runs).
"""
import contextvars
import uuid
from dataclasses import dataclass, field


@dataclass
class AuditContext:
    request: object
    request_id: str
    entries: list = field(default_factory=list)


_current = contextvars.ContextVar("audit_context", default=None)


def get_context():
    return _current.get()


def start(request):
    ctx = AuditContext(request=request, request_id=uuid.uuid4().hex)
    token = _current.set(ctx)
    return ctx, token


def end(token):
    _current.reset(token)
