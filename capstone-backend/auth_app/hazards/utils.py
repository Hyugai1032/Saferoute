import math


def haversine_km(lat1, lng1, lat2, lng2):
    """
    Calculates distance between two coordinates in kilometers.
    """
    radius_earth_km = 6371

    lat1 = math.radians(float(lat1))
    lng1 = math.radians(float(lng1))
    lat2 = math.radians(float(lat2))
    lng2 = math.radians(float(lng2))

    dlat = lat2 - lat1
    dlng = lng2 - lng1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))
    return radius_earth_km * c