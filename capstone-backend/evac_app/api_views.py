# capstone-backend/evac_app/api_views.py
import re
import tempfile
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import EvacuationCenter
from .serializers import EvacuationCenterSerializer
from .utils.csv_helpers import read_csv_rows, read_xlsx_rows, dms_to_decimal
from django.db import transaction
from auth_app.models import Municipality, Barangay
import pandas as pd

class EvacuationCenterViewSet(viewsets.ModelViewSet):
    queryset = EvacuationCenter.objects.all().order_by('-created_at')
    serializer_class = EvacuationCenterSerializer


class EvacUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=400)

        file = request.FILES["file"]
        name = file.name.lower()

        # --- Detect CSV or XLSX format automatically ---
        if name.endswith(".csv"):
            rows = read_csv_rows(file)
        elif name.endswith(".xlsx"):
            rows = read_xlsx_rows(file)
        else:
            return Response({"error": "Invalid file type. Use CSV or XLSX."}, status=400)

        if not rows:
            return Response({"error": "No valid rows found"}, status=400)

        inserted = 0
        updated = 0

        for r in rows:
            # Normalize keys (from Excel)
            province = str(r.get("province", "")).strip()
            municipality_name = str(r.get("municipality", "")).strip()
            barangay_name = str(r.get("barangay", "")).strip()
            facility_name = str(r.get("name of facility", "")).strip() or str(r.get("facility", "")).strip()

            if not municipality_name or not facility_name:
                continue

            # --- Resolve municipality ---
            municipality, _ = Municipality.objects.get_or_create(
                name=municipality_name,
                defaults={"province": province or "Oriental Mindoro"}
            )

            # --- Resolve barangay ---
            barangay = None
            if barangay_name:
                barangay, _ = Barangay.objects.get_or_create(
                    name=barangay_name,
                    municipality=municipality
                )

            # --- Parse coordinates ---
            coord = r.get("coordinates (latitude and longitude)") or r.get("coordinates")
            lat = lon = None
            if coord:
                try:
                    lat_str, lon_str = map(str.strip, coord.split(","))
                    lat = dms_to_decimal(lat_str)
                    lon = dms_to_decimal(lon_str)
                except:
                    lat = lon = None

            # Build evacuation center object
            data = {
                "name": facility_name,
                "municipality": municipality,
                "barangay": barangay,
                "fund_source": r.get("fund source", ""),
                "family_capacity_max": int(r.get("families") or 0),
                "individual_capacity_max": int(r.get("individuals") or 0),
                "used_for_covid": str(r.get("used for covid?")).strip().lower() == "yes",
                "latitude": lat,
                "longitude": lon,
                "flood_susceptibility": (r.get("flood susceptibility") or "Low").capitalize(),
                "landslide_susceptibility": (r.get("landslide susceptibility") or "Low").capitalize(),
                "status": (r.get("status") or "TEMPORARY").upper(),
                "remarks": r.get("remarks", ""),
            }

            ec, created = EvacuationCenter.objects.update_or_create(
                name=facility_name,
                municipality=municipality,
                defaults=data
            )
            if created:
                inserted += 1
            else:
                updated += 1

        return Response({
            "message": "Upload completed successfully.",
            "inserted": inserted,
            "updated": updated,
            "total": inserted + updated,
        })


