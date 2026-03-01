import re
from rest_framework import viewsets, status, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum, Max
from .models import EvacuationCenter, EvacuationLog
from .serializers import EvacuationCenterSerializer, EvacuationLogSerializer, EvacuationCenterListSerializer
from .utils.csv_helpers import read_csv_rows, read_xlsx_rows, dms_to_decimal
from django.db import transaction
from auth_app.models import Municipality, Barangay


class EvacuationCenterViewSet(viewsets.ModelViewSet):
    queryset = EvacuationCenter.objects.all().order_by('-created_at')
    serializer_class = EvacuationCenterSerializer

    # Enable filtering
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Exact-match filters
    filterset_fields = {
        'municipality': ['exact'],
        'barangay': ['exact'],
        'status': ['exact'],
        'flood_susceptibility': ['exact'],
        'landslide_susceptibility': ['exact'],
        'used_for_covid': ['exact'],
    }

    # Optional search (text)
    search_fields = [
        'name',
        'remarks',
        'fund_source',
    ]

    # Optional ordering
    ordering_fields = [
        'name',
        'family_capacity_max',
        'individual_capacity_max',
        'created_at',
    ]



class EvacUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def clean_text(self, text):
        """
        Remove extra spaces from text like 'V  I  C  T  O  R  I  A' -> 'VICTORIA'
        """
        if not text:
            return ""
        
        text = str(text).strip()
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        return text

    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES["file"]
        name = file.name.lower()

        # Detect file format
        try:
            if name.endswith(".csv"):
                rows = read_csv_rows(file)
            elif name.endswith(".xlsx"):
                rows = read_xlsx_rows(file)
            else:
                return Response(
                    {"error": "Invalid file type. Use CSV or XLSX."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {"error": f"Failed to read file: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not rows:
            return Response(
                {"error": "No valid rows found in file."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        print(f"\n{'='*80}")
        print(f"📁 Processing file: {file.name}")
        print(f"📊 Total rows to process: {len(rows)}")
        print(f"{'='*80}\n")

        inserted = 0
        updated = 0
        skipped = 0
        errors = []

        with transaction.atomic():
            for idx, r in enumerate(rows, start=1):
                try:
                    # Extract and CLEAN values (remove extra spaces!)
                    province = self.clean_text(r.get("province", "")) or "Oriental Mindoro"
                    municipality_name = self.clean_text(r.get("municipality", ""))
                    barangay_name = self.clean_text(r.get("barangay", ""))
                    facility_name = self.clean_text(r.get("name of facility", ""))

                    # Skip if missing required fields
                    if not municipality_name or not facility_name:
                        skipped += 1
                        errors.append(f"Row {idx}: Missing municipality or facility name")
                        continue

                    if idx <= 3:  # Debug first 3 rows
                        print(f"✓ Processing: {facility_name} @ {municipality_name}/{barangay_name or 'N/A'}")

                    # Get or create Municipality
                    municipality, _ = Municipality.objects.get_or_create(
                        name=municipality_name,
                        defaults={"province": province}
                    )

                    # Get or create Barangay
                    barangay = None
                    if barangay_name:
                        barangay, _ = Barangay.objects.get_or_create(
                            name=barangay_name,
                            municipality=municipality
                        )

                    # Parse coordinates
                    coord_str = str(r.get("coordinates \n(latitude and longitude)", "") or 
                                   r.get("coordinates (latitude and longitude)", "") or
                                   r.get("coordinates", "")).strip()
                    lat = lon = None
                    
                    if coord_str:
                        try:
                            if "," in coord_str:
                                parts = coord_str.split(",")
                                if len(parts) >= 2:
                                    lat = dms_to_decimal(parts[0].strip())
                                    lon = dms_to_decimal(parts[1].strip())
                            else:
                                lat = dms_to_decimal(coord_str)
                        except Exception:
                            pass

                    # Parse capacities (handle "8 fam", "5 fam per room", etc.)
                    families_str = str(r.get("families", "")).strip()
                    individuals_str = str(r.get("individuals", "")).strip()
                    
                    try:
                        family_capacity = int(re.search(r'\d+', families_str).group()) if families_str and re.search(r'\d+', families_str) else 0
                    except:
                        family_capacity = 0
                    
                    try:
                        individual_capacity = int(re.search(r'\d+', individuals_str).group()) if individuals_str and re.search(r'\d+', individuals_str) else 0
                    except:
                        individual_capacity = 0

                    # Parse COVID usage
                    covid_str = str(r.get("used for covid?", "") or 
                                   r.get("used for covid", "")).strip().lower()
                    used_for_covid = covid_str in ["yes", "true", "1", "y"]

                    # Parse susceptibilities (normalize to uppercase)
                    flood_susc = str(r.get("flood susceptibility", "") or 
                                    r.get("flood susceptibility\n", "")).strip().upper()
                    if flood_susc not in ['LOW', 'MEDIUM', 'HIGH']:
                        flood_susc = 'LOW'
                    
                    landslide_susc = str(r.get("landslide susceptibility", "") or
                                        r.get("landslide susceptibility\n", "")).strip().upper()
                    if landslide_susc not in ['LOW', 'MEDIUM', 'HIGH']:
                        landslide_susc = 'LOW'

                    # Parse status
                    status_val = str(r.get("status", "") or 
                                    r.get("status\n", "")).strip().upper()
                    if status_val not in ['PERMANENT', 'TEMPORARY']:
                        status_val = 'TEMPORARY'

                    # Get fund source and remarks
                    fund_source = self.clean_text(r.get("fund source", ""))
                    remarks = self.clean_text(r.get("remarks", ""))

                    # Build data dictionary
                    data = {
                        "province": province,
                        "municipality": municipality,
                        "barangay": barangay,
                        "fund_source": fund_source,
                        "family_capacity_max": family_capacity,
                        "individual_capacity_max": individual_capacity,
                        "used_for_covid": used_for_covid,
                        "latitude": lat,
                        "longitude": lon,
                        "flood_susceptibility": flood_susc,
                        "landslide_susceptibility": landslide_susc,
                        "status": status_val,
                        "remarks": remarks,
                    }

                    # Create or update
                    ec, created = EvacuationCenter.objects.update_or_create(
                        name=facility_name,
                        municipality=municipality,
                        defaults=data
                    )
                    
                    if created:
                        inserted += 1
                        if inserted <= 3:
                            print(f"  ✅ Created: {facility_name}")
                    else:
                        updated += 1
                        if updated <= 3:
                            print(f"  🔄 Updated: {facility_name}")

                except Exception as e:
                    skipped += 1
                    error_msg = f"Row {idx}: {str(e)}"
                    errors.append(error_msg)
                    if skipped <= 3:
                        print(f"  ❌ Error: {str(e)}")
                    continue

        print(f"\n{'='*80}")
        print(f"📊 UPLOAD SUMMARY")
        print(f"{'='*80}")
        print(f"✅ Inserted: {inserted}")
        print(f"🔄 Updated: {updated}")
        print(f"⚠️  Skipped: {skipped}")
        print(f"❌ Total Errors: {len(errors)}")
        print(f"{'='*80}\n")

        response_data = {
            "message": "Upload completed successfully.",
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "total": inserted + updated,
        }

        if errors:
            response_data["errors"] = errors[:20]
            response_data["total_errors"] = len(errors)
            if len(errors) > 20:
                response_data["note"] = "Showing first 20 errors only"

        return Response(response_data, status=status.HTTP_200_OK)

from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import EvacuationLog
from .serializers import EvacuationLogSerializer


class EvacuationLogViewSet(viewsets.ModelViewSet):
    serializer_class = EvacuationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["center"]
    search_fields = ["remarks", "center__name"]
    ordering_fields = ["date_recorded", "id"]
    ordering = ["-date_recorded", "-id"]

    def get_queryset(self):
        user = self.request.user
        qs = EvacuationLog.objects.select_related("center", "reporting_staff").all()

        # Staff: only their assigned center (ignore any ?center param)
        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return qs.none()
            return qs.filter(center_id=user.assigned_center_id)

        # Municipal admin: centers in their municipality
        if user.role == "MUNICIPAL_ADMIN":
            return qs.filter(center__municipality=user.municipality)

        # Others: allow optional center filter via DjangoFilterBackend (no manual filter needed)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        center = serializer.validated_data.get("center")

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                raise PermissionDenied("Staff has no assigned center.")
            if center.id != user.assigned_center_id:
                raise PermissionDenied("You can only log for your assigned center.")

        if user.role in ["MUNICIPAL_ADMIN", "RESPONSE_TEAM"]:
            if center.municipality_id != user.municipality_id:
                raise PermissionDenied("You can only log for centers in your municipality.")

        serializer.save(reporting_staff=user)

    @action(detail=False, methods=["get"])
    def latest_by_center(self, request):
        center_id = request.query_params.get("center")
        if not center_id:
            return Response({"detail": "center query param is required"}, status=400)

        agg = (
            EvacuationLog.objects
            .filter(center_id=center_id)
            .aggregate(
                ind_in=Sum("individuals_in"),
                ind_out=Sum("individuals_out"),
                last=Max("date_recorded"),
            )
        )

        total_current = (agg["ind_in"] or 0) - (agg["ind_out"] or 0)
        if total_current < 0:
            total_current = 0

        return Response({
            "center": int(center_id),
            "total_current": total_current,
            "date_recorded": agg["last"],
        })    
    @action(detail=False, methods=["get"])
    def staff_summary(self, request):
        user = request.user

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return Response({"detail": "No assigned center."}, status=400)
            center_id = user.assigned_center_id
        else:
            center_id = request.query_params.get("center")
            if not center_id:
                return Response({"detail": "center query param is required"}, status=400)

        agg = (
            EvacuationLog.objects
            .filter(center_id=center_id)
            .aggregate(
                ind_in=Sum("individuals_in"),
                ind_out=Sum("individuals_out"),
                children=Sum("children_count"),
                seniors=Sum("senior_count"),
                pwd=Sum("pwd_count"),
                pregnant=Sum("pregnant_count"),
                lactating=Sum("lactating_count"),
                last=Max("date_recorded"),
            )
        )

        total_current = (agg["ind_in"] or 0) - (agg["ind_out"] or 0)
        if total_current < 0:
            total_current = 0

        breakdown = {
            "children_count": agg["children"] or 0,
            "senior_count": agg["seniors"] or 0,
            "pwd_count": agg["pwd"] or 0,
            "pregnant_count": agg["pregnant"] or 0,
            "lactating_count": agg["lactating"] or 0,
        }

        return Response({
            "center": int(center_id),
            "latest": {
                "date_recorded": agg["last"],
                "total_current": total_current,
            },
            "breakdown": breakdown,
            "total_current": total_current,
        })    
class EvacuationCenterListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EvacuationCenter.objects.select_related("municipality").all().order_by("name")
    serializer_class = EvacuationCenterListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["municipality"]  # ✅ so frontend can filter by municipality
    pagination_class = None

