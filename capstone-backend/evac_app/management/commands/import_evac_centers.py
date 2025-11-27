import csv
import re
import pandas as pd
from django.core.management.base import BaseCommand
from evac_app.models import EvacuationCenter
from auth_app.models import Municipality, Barangay  # <-- import Barangay
from evac_app.utils.csv_helpers import dms_to_decimal


class Command(BaseCommand):
    help = "Import evacuation centers from CSV or XLSX"

    def add_arguments(self, parser):
        parser.add_argument("file", type=str)

    def handle(self, *args, **options):
        path = options["file"]

        # ---------------------------------------------
        # LOAD FILE (CSV or XLSX)
        # ---------------------------------------------
        if path.lower().endswith(".xlsx"):
            df = pd.read_excel(path)
            df = df.where(pd.notnull(df), None)
            rows = df.to_dict(orient="records")
        else:
            with open(path, encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))

        last_province = None
        last_municipality = None
        last_barangay = None

        for row in rows:
            # Normalize keys safely
            def val(col):
                return (row.get(col) or "").strip()

            # ---------------------------------------------
            # Province
            # ---------------------------------------------
            province = val("Province")
            if province:
                last_province = province
            else:
                province = last_province

            # ---------------------------------------------
            # Municipality
            # ---------------------------------------------
            municipality_name = val("Municipality")
            if municipality_name:
                last_municipality = municipality_name
            else:
                municipality_name = last_municipality

            # ---------------------------------------------
            # Barangay
            # ---------------------------------------------
            barangay_name = val("Barangay")
            if barangay_name:
                last_barangay = barangay_name
            else:
                barangay_name = last_barangay

            # ---------------------------------------------
            # Ensure municipality exists
            # ---------------------------------------------
            municipality_obj, _ = Municipality.objects.get_or_create(
                name=municipality_name
            )

            # ---------------------------------------------
            # Ensure barangay exists (linked to municipality)
            # ---------------------------------------------
            barangay_obj = None
            if barangay_name:
                barangay_obj, _ = Barangay.objects.get_or_create(
                    name=barangay_name,
                    municipality_id=municipality_obj
                )

            # ---------------------------------------------
            # Coordinates (DMS parsing)
            # ---------------------------------------------
            coord_raw = val("Coordinates (Latitude and Longitude)")
            latitude = longitude = None

            if coord_raw:
                parts = re.split(r"[,\s]+", coord_raw)
                if len(parts) >= 2:
                    latitude = dms_to_decimal(parts[0])
                    longitude = dms_to_decimal(parts[1])
                elif len(parts) == 1:
                    latitude = dms_to_decimal(parts[0])

            # ---------------------------------------------
            # Status
            # ---------------------------------------------
            status_raw = val("Status").lower()
            status = "PERMANENT" if status_raw == "permanent" else "TEMPORARY"

            # ---------------------------------------------
            # COVID usage
            # ---------------------------------------------
            used_covid = val("Used for COVID? (Yes/No)").lower() == "yes"

            # ---------------------------------------------
            # Resolve name column from several possible names
            # ---------------------------------------------
            name = (
                val("Name of Facility")
                or val("Name")
                or val("Facility Name")
                or val("EC Name")
                or val("Evacuation Center")
            )

            # ---------------------------------------------
            # Safely cast numeric values
            # ---------------------------------------------
            def to_int(x):
                try:
                    return int(float(x))
                except:
                    return 0

            families = to_int(row.get("Families"))
            individuals = to_int(row.get("Individuals"))

            # ---------------------------------------------
            # Create or update evacuation center
            # ---------------------------------------------
            EvacuationCenter.objects.update_or_create(
                name=name,
                municipality=municipality_obj,
                defaults={
                    "barangay": barangay_obj,  # <-- use the FK object now
                    "fund_source": row.get("Fund Source") or "",
                    "family_capacity_max": families,
                    "individual_capacity_max": individuals,
                    "used_for_covid": used_covid,
                    "latitude": latitude,
                    "longitude": longitude,
                    "flood_susceptibility": row.get("Flood Susceptibility") or "",
                    "landslide_susceptibility": row.get("Landslide Susceptibility") or "",
                    "status": status,
                    "remarks": row.get("Remarks") or "",
                },
            )

        self.stdout.write(self.style.SUCCESS("Evacuation centers imported successfully!"))
