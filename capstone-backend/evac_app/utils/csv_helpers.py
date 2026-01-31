"""
csv_helpers.py - FINAL VERSION with proper coordinate handling
Place this in your utils folder
"""

import re
from openpyxl import load_workbook
import csv
from io import StringIO


def dms_to_decimal(dms_str):
    """Convert DMS coordinates to decimal format"""
    if not dms_str or not isinstance(dms_str, str):
        return None
    dms_str = str(dms_str).strip()
    
    # Try numeric decimal first
    try:
        return float(dms_str)
    except ValueError:
        pass
    
    # Handle "Lat: 13 08.278" format (common in your Excel)
    if "lat" in dms_str.lower() or "long" in dms_str.lower():
        # Extract just the number part
        match = re.search(r'([-+]?\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)', dms_str)
        if match:
            degrees = float(match.group(1))
            minutes = float(match.group(2))
            return degrees + (minutes / 60.0)
    
    # DMS regex pattern for full format
    pattern = r"""(?P<deg>-?\d+)[°\s]+
                  (?P<min>\d+)[\'\s]+
                  (?P<sec>\d+(?:\.\d+)?)[\"\s]*
                  (?P<dir>[NSEW])?"""
    match = re.match(pattern, dms_str, re.VERBOSE | re.IGNORECASE)
    
    if match:
        deg = float(match.group("deg"))
        minutes = float(match.group("min"))
        seconds = float(match.group("sec"))
        direction = match.group("dir")
        
        decimal = deg + (minutes / 60.0) + (seconds / 3600.0)
        
        if direction and direction.upper() in ["S", "W"]:
            decimal = -decimal
        
        return decimal
    
    # Fallback: try splitting by spaces
    try:
        parts = re.split(r'[,\s]+', dms_str)
        if len(parts) >= 1:
            return float(parts[0])
    except Exception:
        pass
    
    return None


def read_csv_rows(file_obj):
    """
    Read CSV file and return list of dictionaries
    """
    if hasattr(file_obj, 'read'):
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
    else:
        content = str(file_obj)
    
    f = StringIO(content)
    reader = csv.DictReader(f)
    
    rows = []
    for row in reader:
        normalized_row = {k.lower().strip(): v for k, v in row.items()}
        rows.append(normalized_row)
    
    return rows


def read_xlsx_rows(file):
    """
    Read XLSX file - handles merged cells and complex header structure
    """
    import openpyxl
    
    wb = openpyxl.load_workbook(file, data_only=True)
    sheet = wb.active
    
    print(f"\n{'='*80}")
    print(f"📊 Reading Excel file: {sheet.title}")
    print(f"📏 Sheet dimensions: {sheet.max_row} rows x {sheet.max_column} columns")
    print(f"{'='*80}")
    
    # Get ALL rows first
    all_rows = list(sheet.iter_rows(values_only=True))
    
    # Find header row by looking for key columns
    header_row_idx = None
    header = None
    
    for idx, row in enumerate(all_rows[:20], start=1):  # Check first 20 rows
        # Convert to lowercase strings
        row_lower = [str(cell).lower().strip() if cell else "" for cell in row]
        
        # Look for characteristic header keywords
        has_municipality = any('municipality' in cell for cell in row_lower)
        has_barangay = any('barangay' in cell for cell in row_lower)
        has_facility_or_name = any('facility' in cell or 'name' in cell for cell in row_lower)
        
        if has_municipality and (has_barangay or has_facility_or_name):
            print(f"✅ Found header at row {idx}")
            header_row_idx = idx
            header = row  # Keep original case
            break
    
    if not header_row_idx:
        print("❌ ERROR: Could not find header row!")
        return []
    
    # Map column indices to names
    column_map = {}
    
    # Check if there's a row above the header that might contain column labels
    if header_row_idx > 1:
        row_above = all_rows[header_row_idx - 2]  # -2 because we're 1-indexed
    else:
        row_above = None
    
    # Build column mapping
    for col_idx, cell_value in enumerate(header):
        if cell_value and str(cell_value).strip():
            col_name = str(cell_value).lower().strip()
            column_map[col_idx] = col_name
        elif row_above and row_above[col_idx]:
            # Use value from row above if current cell is empty
            col_name = str(row_above[col_idx]).lower().strip()
            column_map[col_idx] = col_name
        else:
            column_map[col_idx] = f"col_{col_idx}"  # Fallback name
    
    print(f"\n📋 Column mapping:")
    for idx, name in list(column_map.items())[:12]:  # Show first 12 columns
        print(f"  Column {idx}: '{name}'")
    
    # Now process data rows
    rows = []
    current_province = None
    current_municipality = None
    current_barangay = None
    pending_lat = None  # Store latitude waiting for longitude
    
    for row_idx in range(header_row_idx, len(all_rows)):
        row_values = all_rows[row_idx]
        
        # Skip completely empty rows
        if all(v is None or str(v).strip() == '' for v in row_values):
            continue
        
        # Build row dictionary using column map
        row_dict = {}
        for col_idx, value in enumerate(row_values):
            col_name = column_map.get(col_idx, f"col_{col_idx}")
            if value is not None and str(value).strip():
                row_dict[col_name] = value
        
        # Handle merged cells - carry forward values
        province_val = str(row_dict.get('province', '')).strip() if row_dict.get('province') else ''
        municipality_val = str(row_dict.get('municipality', '')).strip() if row_dict.get('municipality') else ''
        barangay_val = str(row_dict.get('barangay', '')).strip() if row_dict.get('barangay') else ''
        
        if province_val and province_val not in ['Province', 'PROVINCE']:
            current_province = province_val
        elif current_province:
            row_dict['province'] = current_province
        
        if municipality_val and municipality_val not in ['Municipality', 'MUNICIPALITY']:
            current_municipality = municipality_val
        elif current_municipality:
            row_dict['municipality'] = current_municipality
        
        if barangay_val and barangay_val not in ['Barangay', 'BARANGAY']:
            current_barangay = barangay_val
        elif current_barangay:
            row_dict['barangay'] = current_barangay
        
        # Get facility name - try multiple possible column names
        facility = None
        for possible_name in ['name of facility', 'facility name', 'facility', 'name', 'evacuation center']:
            if possible_name in row_dict:
                facility = str(row_dict[possible_name]).strip()
                if facility and facility not in ['Name of Facility', 'NAME OF FACILITY', 'Facility']:
                    row_dict['name of facility'] = facility  # Standardize the key
                    break
        
        # Handle coordinates - THIS IS THE KEY FIX
        coord_text = str(row_dict.get('coordinates \n(latitude and longitude)', '') or 
                        row_dict.get('coordinates (latitude and longitude)', '') or 
                        row_dict.get('coordinates', '') or '').strip()
        
        if coord_text:
            if 'lat' in coord_text.lower():
                # This is a latitude row - store it and skip adding this row
                pending_lat = coord_text
                continue  # Don't add this row to results yet
            elif 'long' in coord_text.lower() and pending_lat:
                # This is a longitude row - combine with previous latitude
                if rows:  # If we have rows already
                    # Add combined coordinates to the LAST row (the facility row)
                    combined = f"{pending_lat}, {coord_text}"
                    rows[-1]['coordinates (latitude and longitude)'] = combined
                pending_lat = None  # Clear pending
                continue  # Don't add this row either
        
        # Only add rows with facility names
        if facility and facility not in ['Name of Facility', 'NAME OF FACILITY', 'Facility', 'Name']:
            rows.append(row_dict)
    
    print(f"\n{'='*80}")
    print(f"✅ Successfully processed {len(rows)} evacuation centers")
    print(f"{'='*80}\n")
    
    return rows