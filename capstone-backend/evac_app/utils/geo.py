from ipware import get_client_ip
import requests
from django.core.cache import cache


def get_request_ip(request):
    client_ip, is_routable = get_client_ip(request)
    return client_ip  # None if it couldn't be determined

ORIENTAL_MINDORO_HINTS = {
    "oriental mindoro", "calapan", "mimaropa",
    "puerto galera", "victoria", "naujan", "pinamalayan",
    "pola", "socorro", "bongabong", "roxas", "mansalay",
    "bulalacao", "gloria", "baco", "san teodoro",
}

def lookup_ip_region(ip: str) -> dict | None:
    if not ip:
        return None

    cache_key = f"geoip:{ip}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,country,countryCode,region,regionName,city"},
            timeout=2,
        )
        data = resp.json()
        if data.get("status") != "success":
            return None
        cache.set(cache_key, data, timeout=60 * 60 * 24)  # cache 1 day
        return data
    except requests.RequestException:
        return None


def ip_likely_in_oriental_mindoro(ip: str) -> bool | None:
    """
    Returns True/False if we can make a determination, or None if
    the lookup was inconclusive (e.g. lookup failed, private/local IP,
    or ambiguous region). Callers should treat None as 'don't block'.
    """
    data = lookup_ip_region(ip)
    if not data:
        return None
    if data.get("countryCode") != "PH":
        return False

    haystack = f"{data.get('regionName','')} {data.get('city','')}".lower()
    return any(hint in haystack for hint in ORIENTAL_MINDORO_HINTS)