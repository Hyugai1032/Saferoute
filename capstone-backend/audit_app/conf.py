"""
Audit log settings. Every value can be overridden in settings.py with the same name.
They are read on each call (not at import time) so tests can override them.
"""
from django.conf import settings

# Models whose create / update / delete are recorded. Labels that don't exist are
# skipped with a warning, so a typo never stops the server from starting.
DEFAULT_TRACKED_MODELS = [
    "auth_app.CustomUser",
    "auth_app.Municipality",
    "auth_app.Barangay",
    "auth_app.HazardReport",
    "auth_app.HazardPhoto",
    "auth_app.GisLayer",
    "evac_app.EvacuationCenter",
    "evac_app.EvacuationLog",
]

# Fields never compared (they change on every save and carry no audit value).
DEFAULT_EXCLUDE_FIELDS = {"updated_at", "last_login", "last_login_at"}

# Field names (or parts of names) whose values are never stored, only "changed".
DEFAULT_REDACT_FIELDS = {"password", "code_hash", "secret", "token", "api_key"}


def _get(name, default):
    return getattr(settings, name, default)


def tracked_models():
    return list(_get("AUDIT_TRACKED_MODELS", DEFAULT_TRACKED_MODELS))


def exclude_fields():
    return set(DEFAULT_EXCLUDE_FIELDS) | set(_get("AUDIT_EXCLUDE_FIELDS", ()))


def redact_fields():
    return set(DEFAULT_REDACT_FIELDS) | set(_get("AUDIT_REDACT_FIELDS", ()))


def max_value_chars():
    """Longer text values are cut; longer JSON values are replaced by a size note."""
    return int(_get("AUDIT_MAX_VALUE_CHARS", 300))


def login_paths():
    """Extra login URLs, for a login view that is not a SimpleJWT TokenObtainPairView."""
    return set(_get("AUDIT_LOGIN_PATHS", ()))


def sensitive_read_patterns():
    """Successful GETs whose path matches one of these regexes are logged as EXPORT."""
    return list(_get("AUDIT_SENSITIVE_READ_PATTERNS", [r"/export/?$"]))


def exclude_path_prefixes():
    return tuple(_get("AUDIT_EXCLUDE_PATH_PREFIXES", ("/static/", "/media/", "/favicon.ico")))


def proxy_count():
    """
    Number of reverse proxies in front of Django (Railway = 1). The client IP is read
    from X-Forwarded-For counting this many entries from the right, so a client can't
    fake its IP by sending its own X-Forwarded-For header. Use 0 to ignore the header.
    """
    return int(_get("AUDIT_PROXY_COUNT", 1))


def log_outside_requests():
    """Record changes made outside a web request (shell, management commands)."""
    return bool(_get("AUDIT_LOG_OUTSIDE_REQUESTS", True))


def route_patterns():
    """POSTs to paths matching these regexes are logged as ROUTE."""
    return list(_get("AUDIT_ROUTE_PATTERNS", [r"/route/ors/?$", r"/route/suggest-center/?$"]))


def retention_days():
    """How long ordinary entries (changes, logins, denials, exports) are kept."""
    return int(_get("AUDIT_RETENTION_DAYS", 30))


def route_retention_days():
    """Routing entries are high-volume, so they are kept for less time."""
    return int(_get("AUDIT_ROUTE_RETENTION_DAYS", 14))


def viewer_roles():
    return set(_get("AUDIT_VIEWER_ROLES", {"PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN"}))


def all_scope_roles():
    """Roles that see every municipality's entries; other viewer roles see only their own."""
    return set(_get("AUDIT_ALL_SCOPE_ROLES", {"PROVINCIAL_ADMIN"}))
