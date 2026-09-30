"""
csv_helpers.py  (utils/csv_helpers.py)

Reads the "Evacuation Centers" inventory from CSV or XLSX and turns each
facility into one clean dict.

Handles both known layouts:
  A) Puerto Galera style: one row per facility, coordinates in ONE cell,
     either decimal (13.49419, 120.89965) or DMS (13°28'56"N 120°56'16"E).
  B) Victoria style: each facility spans TWO rows, "Lat: 13 08.278" on the
     first row and "Long: 121 11.075" on the second, with merged cells and
     letter-spaced / stacked province + municipality text.

Public API:
    read_csv_rows(file_obj)   -> list[dict]   (canonical keys, see HEADER_RULES)
    read_xlsx_rows(file_obj)  -> list[dict]
    parse_row(raw)            -> dict         (typed values, ready for the model)
"""

import csv
import re
from io import StringIO

from openpyxl import load_workbook

DEFAULT_PROVINCE = "Oriental Mindoro"

# --------------------------------------------------------------------------
# Text helpers
# --------------------------------------------------------------------------

_SYMBOLS = str.maketrans({
    "\u2032": "'", "\u2019": "'", "\u2018": "'",   # ′ ’ ‘
    "\u2033": '"', "\u201d": '"', "\u201c": '"',   # ″ ” “
    "\u00ba": "\u00b0", "\u02da": "\u00b0",        # º ˚ -> °
})


def normalize_header(h) -> str:
    if h is None:
        return ""
    h = str(h).replace("\ufeff", "")
    h = h.replace("\n", " ").replace("\r", " ")
    h = h.replace('"', "").replace("'", "")
    return re.sub(r"\s+", " ", h.strip().lower())


def clean_text(value) -> str:
    """
    Collapse whitespace and un-space letter-spaced text:
        'V  I  C  T  O  R  I  A'  -> 'VICTORIA'
        'O\\nR\\nI\\nE\\nN...'        -> 'ORIENTAL...'
    (word gaps in letter-spaced text are kept only if separated by 3+ spaces)
    """
    if value is None:
        return ""
    s = str(value).replace("\u00a0", " ").strip()
    if not s:
        return ""
    tokens = s.split()
    if len(tokens) >= 3 and all(len(t) == 1 for t in tokens):
        words = re.split(r"[ \t]{3,}", s)
        return " ".join("".join(w.split()) for w in words)
    return " ".join(tokens)


def _title_if_upper(s: str) -> str:
    if s and s.isupper():
        return " ".join(w.capitalize() for w in s.split(" "))
    return s


def clean_place(value) -> str:
    """Municipality / barangay: clean + 'VICTORIA' -> 'Victoria'."""
    return _title_if_upper(clean_text(value))


def clean_province(value) -> str:
    """'ORIENTAL-MINDORO' / 'ORIENTAL - MINDORO' -> 'Oriental Mindoro'."""
    s = clean_text(value)
    s = re.sub(r"\s*-\s*", " ", s)
    return _title_if_upper(s)


# --------------------------------------------------------------------------
# Header matching (works on compact text so "Municipali\nty" still matches)
# --------------------------------------------------------------------------

HEADER_RULES = [
    ("nameoffacility", "name of facility"),
    ("evacuationcenter", "name of facility"),
    ("facility", "name of facility"),
    ("coordinates", "coordinates"),
    ("latitudeandlongitude", "coordinates"),
    ("fund", "fund source"),
    ("covid", "used for covid?"),
    ("flood", "flood susceptibility"),
    ("landslide", "landslide susceptibility"),
    ("status", "status"),
    ("remarks", "remarks"),
    ("famil", "families"),
    ("individual", "individuals"),
    ("province", "province"),
    ("municipality", "municipality"),
    ("barangay", "barangay"),
    ("latitude", "latitude"),
    ("longitude", "longitude"),
]

_CHILD_WORDS = {"province", "municipality", "barangay", "families", "individuals"}


def _compact(h) -> str:
    return re.sub(r"[^a-z0-9]", "", normalize_header(h))


def match_header(h):
    c = _compact(h)
    if not c:
        return None
    for needle, canon in HEADER_RULES:
        if needle in c:
            return canon
    return None


# --------------------------------------------------------------------------
# Coordinates
# --------------------------------------------------------------------------

_LABELS = re.compile(r"(?i)\b(latitude|longitude|lat|long|lon|lng)\b\s*[:=]?")
_NUM = r"-?\d+(?:\.\d+)?"


def parse_coordinate(value):
    """
    Any of: 13.49419 | "13.49419" | "Lat: 13 08.278" | "Long:  121 11.075"
            | 13°28'56"N | 13°28'56.4"N | 120 56 16 E
    Degrees + decimal minutes and degrees-minutes-seconds are both supported.
    """
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).translate(_SYMBOLS)
    s = _LABELS.sub(" ", s)
    hemi = re.search(r"(?<![A-Za-z])([NSEW])(?![A-Za-z])", s, re.I)
    nums = re.findall(_NUM, s)
    if not nums:
        return None

    deg = float(nums[0])
    mins = float(nums[1]) if len(nums) > 1 else 0.0
    secs = float(nums[2]) if len(nums) > 2 else 0.0
    if mins >= 60 or secs >= 60:
        return None

    dec = abs(deg) + mins / 60.0 + secs / 3600.0
    negative = nums[0].startswith("-") or (hemi and hemi.group(1).upper() in "SW")
    return -dec if negative else dec


def split_lat_lon(value):
    """Split one coordinate cell into (lat, lon). Either may be None."""
    if value is None or value == "":
        return None, None
    if isinstance(value, (int, float)):
        return float(value), None

    s = str(value).translate(_SYMBOLS).strip()
    if not s:
        return None, None

    m = re.search(r"(?i)\b(long(?:itude)?|lon|lng)\b", s)
    if m and m.start() == 0:                      # "Long: 121 11.075" only
        return None, parse_coordinate(s)
    if m:                                         # "Lat: .. Long: .."
        a, b = s[:m.start()], s[m.start():]
    elif re.search(r"[,;\n]", s):                 # "13.49, 120.89"
        a, b = re.split(r"[,;\n]", s, maxsplit=1)
    else:
        m2 = re.search(r"(?<=[NSns])\s+(?=-?\d)", s)   # 13°28'56"N 120°56'16"E
        if m2:
            a, b = s[:m2.start()], s[m2.end():]
        else:
            nums = re.findall(_NUM, s)
            if len(nums) == 2 and all("." in n for n in nums):
                a, b = nums                        # "13.49 120.89"
            else:
                a, b = s, ""                       # latitude only

    lat = parse_coordinate(a)
    lon = parse_coordinate(b) if b.strip() else None
    return lat, lon


def _in_range(v, lo, hi):
    return v if v is not None and lo <= v <= hi else None


# --------------------------------------------------------------------------
# Field parsers
# --------------------------------------------------------------------------

def parse_int(value) -> int:
    """'8 fam' -> 8, '5 fam per room' -> 5, 25 -> 25, '' -> 0"""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    m = re.search(r"\d+", str(value))
    return int(m.group()) if m else 0


def parse_susceptibility(value) -> str:
    s = str(value or "").strip().upper()
    if "HIGH" in s:
        return "HIGH"
    if "MOD" in s or "MED" in s:
        return "MEDIUM"
    return "LOW"


def parse_status(value) -> str:
    return "PERMANENT" if "PERM" in str(value or "").upper() else "TEMPORARY"


def parse_yes(value) -> bool:
    return str(value or "").strip().lower() in {"yes", "true", "1", "y"}


def parse_row(raw: dict) -> dict:
    """Canonical raw dict (from the readers) -> typed values for the model."""
    lat = _in_range(parse_coordinate(raw.get("latitude")), -90, 90)
    lon = _in_range(parse_coordinate(raw.get("longitude")), -180, 180)
    return {
        "source_row": raw.get("_row"),
        "province": clean_province(raw.get("province")) or DEFAULT_PROVINCE,
        "municipality": clean_place(raw.get("municipality")),
        "barangay": clean_place(raw.get("barangay")),
        "facility_name": clean_text(raw.get("name of facility")),
        "fund_source": clean_text(raw.get("fund source")),
        "family_capacity": parse_int(raw.get("families")),
        "individual_capacity": parse_int(raw.get("individuals")),
        "used_for_covid": parse_yes(raw.get("used for covid?")),
        "latitude": lat,
        "longitude": lon,
        "flood_susceptibility": parse_susceptibility(raw.get("flood susceptibility")),
        "landslide_susceptibility": parse_susceptibility(raw.get("landslide susceptibility")),
        "status": parse_status(raw.get("status")),
        "remarks": clean_text(raw.get("remarks")),
    }


# --------------------------------------------------------------------------
# Grid reader (shared by CSV and XLSX)
# --------------------------------------------------------------------------

_HIERARCHY = ["province", "municipality", "barangay"]


def _is_blank(v) -> bool:
    return v is None or str(v).strip() == ""


def _find_header(grid):
    """Return (header_idx, data_start, column_map) or None."""
    for idx, row in enumerate(grid[:40]):
        keys = {match_header(c) for c in row if not _is_blank(c)}
        if "name of facility" in keys and "coordinates" in keys:
            parent = row
            child = None
            data_start = idx + 1
            # Two-row header? (Province / Municipality / Barangay / Families / Individuals)
            if data_start < len(grid):
                nxt = grid[data_start]
                if any(_compact(c) in _CHILD_WORDS for c in nxt if not _is_blank(c)):
                    child = nxt
                    data_start += 1

            cmap = {}
            for i in range(max(len(parent), len(child) if child else 0)):
                p = parent[i] if i < len(parent) else None
                c = child[i] if child and i < len(child) else None
                key = (match_header(c) if not _is_blank(c) else None) \
                    or (match_header(p) if not _is_blank(p) else None) \
                    or normalize_header(c) or normalize_header(p)
                if key:
                    cmap[i] = key
            return idx, data_start, cmap
    return None


def _attach_coordinates(rec, text):
    lat, lon = split_lat_lon(text)
    if lat is not None and rec.get("latitude") is None:
        rec["latitude"] = lat
    if lon is not None and rec.get("longitude") is None:
        rec["longitude"] = lon


def _assemble(numbered_rows):
    """
    numbered_rows: iterable of (sheet_row_number, {canonical_key: value}).
    - carries Province / Municipality / Barangay down (merged cells)
    - resets lower levels when a higher level changes
    - a row without a facility name that has "Long: ..." is glued to the
      previous facility (two-row layout)
    """
    rows, current = [], None
    state = {k: None for k in _HIERARCHY}

    for rownum, raw in numbered_rows:
        row = {k: v for k, v in raw.items() if not _is_blank(v)}
        if not row:
            continue

        facility = clean_text(row.get("name of facility"))
        if normalize_header(facility) == "name of facility":   # repeated header row
            continue

        for i, level in enumerate(_HIERARCHY):
            val = clean_text(row.get(level))
            if val and normalize_header(val) != level:
                if val != state[level]:
                    state[level] = val
                    for lower in _HIERARCHY[i + 1:]:
                        state[lower] = None
            if state[level]:
                row[level] = state[level]
            else:
                row.pop(level, None)

        coord = row.get("coordinates")

        if facility:
            row["name of facility"] = facility
            row["_row"] = rownum
            rows.append(row)
            current = row
        elif current is None or not coord:
            continue

        if coord:
            _attach_coordinates(current, coord)

    return rows


def _read_grid(grid):
    found = _find_header(grid)
    if not found:
        return None
    _, data_start, cmap = found

    def gen():
        for offset, values in enumerate(grid[data_start:]):
            yield data_start + offset + 1, {
                cmap[i]: v for i, v in enumerate(values) if i in cmap and not _is_blank(v)
            }

    return _assemble(gen())


# --------------------------------------------------------------------------
# Public readers
# --------------------------------------------------------------------------

_HEADER_ERROR = ("Could not find the header row. It needs 'Name of Facility' "
                 "and 'Coordinates' columns within the first 40 rows.")


def read_xlsx_rows(file):
    wb = load_workbook(file, data_only=True)
    rows, found_any = [], False
    for ws in wb.worksheets:                      # every sheet with a valid header
        result = _read_grid(list(ws.iter_rows(values_only=True)))
        if result is not None:
            found_any = True
            rows.extend(result)
    if not found_any:
        raise ValueError(_HEADER_ERROR)
    return rows


def read_csv_rows(file_obj):
    if hasattr(file_obj, "read"):
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8-sig", errors="ignore")
    else:
        content = str(file_obj)

    grid = list(csv.reader(StringIO(content)))
    result = _read_grid(grid)
    if result is None:
        raise ValueError(_HEADER_ERROR)
    return result