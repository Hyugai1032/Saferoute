"""
Collects audit entries during a request and writes them in one INSERT at the end.

Besides the model changes queued by signals, it records these request-level events:
- LOGIN / LOGIN_FAILED   POST to a SimpleJWT TokenObtainPairView (or AUDIT_LOGIN_PATHS)
- PERMISSION_DENIED      any request answered with 403
- EXPORT                 successful GET matching AUDIT_SENSITIVE_READ_PATTERNS

Everything else (ordinary GETs, 401s from expired tokens, validation errors that
change nothing) is not logged, which keeps the table small.

Place it last in MIDDLEWARE.
"""
import json
import logging
import re

from django.contrib.auth import get_user_model

from . import conf, context
from .models import AuditLog
from .recorder import fill_request_info, set_actor

logger = logging.getLogger(__name__)

LOGIN_FAILURE_CODES = {400, 401, 403}


def _token_obtain_view():
    try:
        from rest_framework_simplejwt.views import TokenObtainPairView
        return TokenObtainPairView
    except ImportError:
        return None


def merge_entries(entries):
    """
    A view often saves the same record more than once (e.g. save(), then
    save(update_fields=["reviewed_at"])). Fold those into one entry per record:
    - UPDATE + UPDATE -> one UPDATE, keeping the first "before" and the last "after"
    - CREATE + UPDATE -> one CREATE with the final values
    """
    merged, by_record = [], {}
    for entry in entries:
        key = (entry.resource_type, entry.resource_id) if entry.resource_type else None
        first = by_record.get(key) if key else None
        if first is not None and entry.action == AuditLog.Action.UPDATE and first.action in (
            AuditLog.Action.CREATE, AuditLog.Action.UPDATE
        ):
            details = dict(first.details or {})
            for field, change in (entry.details or {}).items():
                if first.action == AuditLog.Action.CREATE:
                    details[field] = change[1]
                elif field in details:
                    details[field] = [details[field][0], change[1]]
                else:
                    details[field] = change
            if first.action == AuditLog.Action.UPDATE:
                details = {k: v for k, v in details.items() if v[0] != v[1] or v[0] == "[hidden]"}
            first.details = details or None
            first.resource_label = entry.resource_label
            continue
        if key and entry.action in (AuditLog.Action.CREATE, AuditLog.Action.UPDATE):
            by_record[key] = entry
        elif key:
            by_record.pop(key, None)  # a DELETE ends the record's story
        merged.append(entry)
    # An update that ended where it started (A -> B -> A) leaves nothing to show.
    return [e for e in merged if not (e.action == AuditLog.Action.UPDATE and not e.details)]


class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self._token_view = _token_obtain_view()
        self._sensitive = [re.compile(p) for p in conf.sensitive_read_patterns()]

    def __call__(self, request):
        if request.method == "OPTIONS" or request.path.startswith(conf.exclude_path_prefixes()):
            return self.get_response(request)

        ctx, token = context.start(request)
        try:
            response = self.get_response(request)
            try:
                self._finish(request, response, ctx)
            except Exception:
                # Logging must never break the actual request.
                logger.exception("Audit logging failed for %s %s", request.method, request.path)
            return response
        finally:
            context.end(token)

    # -- login detection -------------------------------------------------------

    def _is_login(self, request, view_class):
        if request.method != "POST":
            return False
        if request.path in conf.login_paths():
            return True
        return bool(
            view_class and self._token_view and isinstance(view_class, type)
            and issubclass(view_class, self._token_view)
        )

    def process_view(self, request, view_func, view_args, view_kwargs):
        view_class = getattr(view_func, "view_class", None) or getattr(view_func, "cls", None)
        request._audit_view_class = view_class
        if self._is_login(request, view_class):
            # Read the submitted email before the view consumes the body. Django keeps a
            # copy of the body, so DRF can still parse it afterwards.
            request._audit_login_email = self._submitted_email(request)
        return None

    @staticmethod
    def _submitted_email(request):
        field = getattr(get_user_model(), "USERNAME_FIELD", "email")
        try:
            content_type = request.content_type or ""
            if "json" in content_type:
                data = json.loads(request.body or b"{}")
            elif content_type in ("application/x-www-form-urlencoded", "multipart/form-data"):
                data = request.POST
            else:
                return ""
            value = data.get(field) or data.get("email") or data.get("username") or ""
            return str(value).strip().lower()[:191]
        except Exception:
            return ""

    # -- end of request --------------------------------------------------------

    @staticmethod
    def _request_user(request):
        """The authenticated user, or None. DRF copies the JWT user onto the Django request."""
        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False):
            return user
        return None

    def _finish(self, request, response, ctx):
        status = response.status_code
        entries = ctx.entries
        user = None
        view_class = getattr(request, "_audit_view_class", None)
        view_name = getattr(view_class, "__name__", "")

        if self._is_login(request, view_class):
            email = getattr(request, "_audit_login_email", "")
            if 200 <= status < 300:
                login_user = self._request_user(request)
                if login_user is None and email:
                    field = get_user_model().USERNAME_FIELD
                    login_user = get_user_model()._default_manager.filter(
                        **{f"{field}__iexact": email}
                    ).first()
                entry = AuditLog(action=AuditLog.Action.LOGIN)
                if login_user is not None:
                    set_actor(entry, login_user)
                    entry.resource_type = type(login_user).__name__
                    entry.resource_id = str(login_user.pk)
                    entry.resource_label = entry.actor_email
                entries.append(entry)
                user = login_user
            elif status in LOGIN_FAILURE_CODES:
                entries.append(AuditLog(
                    action=AuditLog.Action.LOGIN_FAILED,
                    details={"attempted_email": email} if email else None,
                ))
        elif status == 403:
            entries.append(AuditLog(
                action=AuditLog.Action.PERMISSION_DENIED,
                details={"view": view_name} if view_name else None,
            ))
        elif (
            request.method == "GET" and 200 <= status < 300
            and any(p.search(request.path) for p in self._sensitive)
        ):
            filters = {k: request.GET.get(k) for k in list(request.GET.keys())[:20]}
            entries.append(AuditLog(
                action=AuditLog.Action.EXPORT,
                details={"filters": filters} if filters else None,
            ))

        if not entries:
            return

        entries = merge_entries(entries)
        user = user or self._request_user(request)
        for entry in entries:
            fill_request_info(entry, request, ctx, status, user)
        AuditLog.objects.bulk_create(entries)
        response["X-Request-ID"] = ctx.request_id
