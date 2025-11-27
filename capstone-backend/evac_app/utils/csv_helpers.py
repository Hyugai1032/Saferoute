# capstone-backend/evac_app/utils/csv_helpers.py
import re
from openpyxl import load_workbook
import csv
from io import StringIO

def dms_to_decimal(dms_str):
    if not dms_str or not isinstance(dms_str, str):
        return None
    dms_str = dms_str.strip()
    # numeric decimal
    try:
        return float(dms_str)
    except ValueError:
        pass
    # DMS regex
    pattern = r"""(?P<deg>-?\d+)[°\s]+
                  (?P<min>\d+)[\'\s]+
                  (?P<sec>\d+(?:\.\d+)?)[\"\s]*
                  (?P<dir>[NSEW])?"""
    match = re.match(pattern, dms_str, re.VERBOSE | re.IGNORECASE)
    if not match:
        # try splitting by spaces/comma - fallback: attempt float from parts
        try:
            parts = re.split(r'[,\s]+', dms_str)
            if len(parts) >= 1:
                return float(parts[0])
        except Exception:
            return None
    deg = float(match.group("deg"))
    minutes = float(match.group("min"))
    seconds = float(match.group("sec"))
    direction = match.group("dir")
    decimal = deg + (minutes / 60.0) + (seconds / 3600.0)
    if direction and direction.upper() in ["S", "W"]:
        decimal = -decimal
    return decimal


def read_csv_rows(file_obj):
    """
    file_obj: file-like (text or binary) with CSV content
    returns list[dict]
    """
    # Ensure text for csv.DictReader
    if hasattr(file_obj, 'read'):
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
    else:
        content = str(file_obj)
    f = StringIO(content)
    reader = csv.DictReader(f)
    return [row for row in reader]


def read_xlsx_rows(file):
    import openpyxl
    wb = openpyxl.load_workbook(file, data_only=True)
    sheet = wb.active

    header = None
    rows = []

    for row in sheet.iter_rows(values_only=True):
        if not header:
            # Convert row to strings for matching
            lower = [str(c).strip().lower() if c else "" for c in row]

            # Check if this row is the real header
            if (
                "province" in lower
                and "municipality" in lower
                and "barangay" in lower
            ):
                header = lower
            else:
                continue  # skip title rows

        else:
            # Normal data rows
            # Create dict: header[i] -> row[i]
            r = {header[i]: row[i] for i in range(len(header))}
            rows.append(r)

    return rows

