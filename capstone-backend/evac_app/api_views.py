import re
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum, Max, ProtectedError, OuterRef, Subquery
from django.utils import timezone
from .models import EvacuationCenter, EvacuationLog, Evacuee, DonationDistribution, Donation, DonationNeed, EvacuationReason
from .serializers import EvacuationCenterSerializer, EvacuationLogSerializer, EvacuationCenterListSerializer, EvacueeSerializer, DonationNeedSerializer, DonationSerializer, DonationDistributionSerializer, EvacuationReasonSerializer
from .utils.csv_helpers import read_csv_rows, read_xlsx_rows, parse_row
from .utils.geo import get_request_ip, ip_likely_in_oriental_mindoro
from django.db import transaction
from auth_app.models import Municipality, Barangay
from auth_app.permissions import IsStaffOrHigher, IsMunicipalAdminOrHigher


import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Donation, DonationNeed


@api_view(['POST'])
@permission_classes([AllowAny])
def public_pledge_donation(request):
    data = request.data

    client_ip = get_request_ip(request)
    in_region = ip_likely_in_oriental_mindoro(client_ip)

    # Hard block only when we're confident it's NOT PH/Mindoro.
    # `None` (inconclusive) is treated as "allow, but flag".
    if in_region is False:
        return Response(
            {"error": "Pledges are currently limited to donors within Oriental Mindoro."},
            status=status.HTTP_403_FORBIDDEN
        )

    ref_code = f"PLG-{random.randint(1000, 9999)}"

    try:
        need_obj = DonationNeed.objects.filter(id=data.get('need_id')).first()

        pledge = DonationPledge.objects.create(
            need=need_obj,
            donor_name=data.get('donor_name'),
            contact_number=data.get('contact_number'),
            quantity=data.get('quantity', 1),
            dropoff_date=data.get('dropoff_date'),
            notes=data.get('notes', ''),
            reference_code=ref_code,
            status='PENDING',
            source_ip=client_ip,                # add this field for audit trail
            ip_region_flagged=(in_region is None),  # flag inconclusive ones for staff review
        )

        return Response({
            "message": "Pledge recorded successfully",
            "reference_code": pledge.reference_code
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EvacuationCenterViewSet(viewsets.ModelViewSet):
    serializer_class = EvacuationCenterSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = {
        "municipality": ["exact"],
        "barangay": ["exact"],
        "status": ["exact"],
        "flood_susceptibility": ["exact"],
        "landslide_susceptibility": ["exact"],
        "used_for_covid": ["exact"],
    }

    search_fields = [
        "name",
        "remarks",
        "fund_source",
    ]

    ordering_fields = [
        "name",
        "family_capacity_max",
        "individual_capacity_max",
        "created_at",
    ]

    def get_queryset(self):
        user = self.request.user

        latest_log = (
            EvacuationLog.objects
            .filter(center_id=OuterRef("pk"))
            .order_by("-date_recorded", "-id")
        )

        qs = (
            EvacuationCenter.objects
            .select_related("municipality", "barangay")
            .annotate(
                latest_total_current=Subquery(latest_log.values("total_current")[:1]),
                latest_total_current_families=Subquery(latest_log.values("total_current_families")[:1]),
            )
            .order_by("-created_at")
        )

        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(municipality_id=user.municipality_id)

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return qs.none()
            return qs.filter(id=user.assigned_center_id)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        municipality = serializer.validated_data.get("municipality")

        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                raise PermissionDenied("Your account has no municipality assigned.")
            if municipality.id != user.municipality_id:
                raise PermissionDenied("You can only create centers in your municipality.")

        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        municipality = serializer.validated_data.get("municipality", instance.municipality)

        if user.role == "MUNICIPAL_ADMIN":
            if instance.municipality_id != user.municipality_id:
                raise PermissionDenied("You cannot edit centers outside your municipality.")
            if municipality.id != user.municipality_id:
                raise PermissionDenied("You cannot move a center to another municipality.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role == "MUNICIPAL_ADMIN" and instance.municipality_id != user.municipality_id:
            raise PermissionDenied("You cannot delete centers outside your municipality.")

        instance.delete()



TOL = 1e-6  # coordinate match tolerance when telling same-named facilities apart
 
 
class EvacUploadAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
 
    def post(self, request):
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
 
        file = request.FILES["file"]
        name = file.name.lower()
 
        try:
            if name.endswith(".csv"):
                rows = read_csv_rows(file)
            elif name.endswith(".xlsx"):
                rows = read_xlsx_rows(file)
            else:
                return Response({"error": "Invalid file type. Use CSV or XLSX."},
                                status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to read file: {e}"},
                            status=status.HTTP_400_BAD_REQUEST)
 
        if not rows:
            return Response({"error": "No valid rows found in file."},
                            status=status.HTTP_400_BAD_REQUEST)
 
        inserted = updated = skipped = 0
        errors = []
        seen = set()  # (facility, municipality, barangay) already handled in THIS upload
 
        for raw in rows:
            p = parse_row(raw)
            label = f"Row {p['source_row']}"  # real spreadsheet row number
            try:
                if not p["municipality"] or not p["facility_name"]:
                    skipped += 1
                    errors.append(f"{label}: Missing municipality or facility name")
                    continue
 
                # savepoint per row: one bad row no longer poisons the whole upload
                with transaction.atomic():
                    municipality = (
                        Municipality.objects.filter(name__iexact=p["municipality"]).first()
                        or Municipality.objects.create(name=p["municipality"], province=p["province"])
                    )
 
                    barangay = None
                    if p["barangay"]:
                        barangay = (
                            Barangay.objects.filter(name__iexact=p["barangay"], municipality=municipality).first()
                            or Barangay.objects.create(name=p["barangay"], municipality=municipality)
                        )
 
                    defaults = {
                        "province": p["province"],
                        "fund_source": p["fund_source"],
                        "family_capacity_max": p["family_capacity"],
                        "individual_capacity_max": p["individual_capacity"],
                        "used_for_covid": p["used_for_covid"],
                        "latitude": p["latitude"],
                        "longitude": p["longitude"],
                        "flood_susceptibility": p["flood_susceptibility"],
                        "landslide_susceptibility": p["landslide_susceptibility"],
                        "status": p["status"],
                        "shelter_category": "OUTSIDE_EC" if any(
                            k in p["facility_name"].upper()
                            for k in ["RESIDENCE", "HOUSE", "HOME", "PRIVATE"]
                        ) else "INSIDE_EC",
                        "remarks": p["remarks"],
                    }
 
                    # Same name + municipality + barangay can legitimately repeat
                    # (e.g. several "CATHOLIC CHURCH" / "BARANGAY HALL" in one barangay).
                    # First occurrence matches by name; repeats are told apart by coordinates.
                    key = (p["facility_name"].lower(), municipality.id, barangay.id if barangay else None)
                    qs = EvacuationCenter.objects.filter(
                        name__iexact=p["facility_name"],
                        municipality=municipality,
                        barangay=barangay,
                    )
                    if key in seen and p["latitude"] is not None and p["longitude"] is not None:
                        qs = qs.filter(
                            latitude__range=(p["latitude"] - TOL, p["latitude"] + TOL),
                            longitude__range=(p["longitude"] - TOL, p["longitude"] + TOL),
                        )
                    seen.add(key)
 
                    ec = qs.order_by("id").first()
                    if ec:
                        for field, value in defaults.items():
                            setattr(ec, field, value)
                        ec.save()
                        updated += 1
                    else:
                        EvacuationCenter.objects.create(
                            name=p["facility_name"],
                            municipality=municipality,
                            barangay=barangay,
                            **defaults,
                        )
                        inserted += 1
 
            except Exception as e:
                skipped += 1
                errors.append(f"{label}: {e}")
 
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


from .models import EvacuationLog
from .serializers import EvacuationLogSerializer


class EvacuationReasonViewSet(viewsets.ModelViewSet):
    """
    Admin-managed list of evacuation reasons shown in the evacuee registration form.

    - list/retrieve: any staff role (so the evacuee form can populate its dropdown)
    - create/update/partial_update/destroy: Municipal Admin or Provincial Admin only

    Query params:
    - ?active_only=true  → list endpoint only returns reasons currently in use
                             (used by the staff-facing dropdown; the admin management
                             page omits this param so it can see/reactivate everything)
    """
    serializer_class = EvacuationReasonSerializer
    pagination_class = None

    def get_queryset(self):
        qs = EvacuationReason.objects.all().order_by("name")

        if self.action == "list":
            active_only = self.request.query_params.get("active_only")
            if active_only in ["1", "true", "True"]:
                qs = qs.filter(is_active=True)

        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsStaffOrHigher]
        else:
            permission_classes = [IsMunicipalAdminOrHigher]
        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        reason = self.get_object()
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        f"\"{reason.name}\" is still assigned to one or more evacuees and can't be deleted. "
                        "Deactivate it instead so it stops appearing as an option."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


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

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return qs.none()
            return qs.filter(center_id=user.assigned_center_id)

        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(center__municipality_id=user.municipality_id)

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

        allowed_logs = self.get_queryset().filter(center_id=center_id)
        if not allowed_logs.exists():
            return Response({"detail": "Not found."}, status=404)

        agg = allowed_logs.aggregate(
            ind_in=Sum("individuals_in"),
            ind_out=Sum("individuals_out"),
            fam_in=Sum("families_in"),
            fam_out=Sum("families_out"),
            last=Max("date_recorded"),
        )

        total_current = (agg["ind_in"] or 0) - (agg["ind_out"] or 0)
        if total_current < 0:
            total_current = 0

        total_current_families = (agg["fam_in"] or 0) - (agg["fam_out"] or 0)
        if total_current_families < 0:
            total_current_families = 0

        return Response({
            "center": int(center_id),
            "total_current": total_current,
            "total_current_families": total_current_families,
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

        allowed_logs = self.get_queryset().filter(center_id=center_id)
        if not allowed_logs.exists():
            return Response({"detail": "Not found."}, status=404)

        agg = allowed_logs.aggregate(
            ind_in=Sum("individuals_in"),
            ind_out=Sum("individuals_out"),
            fam_in=Sum("families_in"),
            fam_out=Sum("families_out"),
            children=Sum("children_count"),
            seniors=Sum("senior_count"),
            pwd=Sum("pwd_count"),
            pregnant=Sum("pregnant_count"),
            lactating=Sum("lactating_count"),
            last=Max("date_recorded"),
        )

        total_current = (agg["ind_in"] or 0) - (agg["ind_out"] or 0)
        if total_current < 0:
            total_current = 0

        total_current_families = (agg["fam_in"] or 0) - (agg["fam_out"] or 0)
        if total_current_families < 0:
            total_current_families = 0

        return Response({
            "center": int(center_id),
            "latest": {
                "date_recorded": agg["last"],
                "total_current": total_current,
                "total_current_families": total_current_families,
            },
            "breakdown": {
                "children_count": agg["children"] or 0,
                "senior_count": agg["seniors"] or 0,
                "pwd_count": agg["pwd"] or 0,
                "pregnant_count": agg["pregnant"] or 0,
                "lactating_count": agg["lactating"] or 0,
            },
            "total_current": total_current,
            "total_current_families": total_current_families,
        })
    
    
class EvacuationCenterListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EvacuationCenterListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["municipality"]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        qs = EvacuationCenter.objects.select_related("municipality").all().order_by("name")

        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(municipality_id=user.municipality_id)

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return qs.none()
            return qs.filter(id=user.assigned_center_id)

        return qs


class EvacueeViewSet(viewsets.ModelViewSet):
    serializer_class = EvacueeSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "center",
        "is_active",
        "sex",
        "is_family_head",
        "reason_for_evacuation",
        "is_child",
        "is_senior",
        "is_pwd",
        "is_pregnant",
        "is_lactating",
    ]

    search_fields = [
        "first_name",
        "middle_name",
        "last_name",
        "contact_number",
        "address",
        "family_head_name",
        "remarks",
        "center__name",
    ]

    ordering_fields = [
        "date_registered",
        "last_name",
        "first_name",
        "age",
    ]

    ordering = ["-date_registered"]

    def get_queryset(self):
        user = self.request.user
        qs = Evacuee.objects.select_related("center", "log").all()

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return qs.none()
            return qs.filter(center_id=user.assigned_center_id)

        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(center__municipality_id=user.municipality_id)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        center = serializer.validated_data.get("center")

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                raise PermissionDenied("Staff has no assigned center.")
            if center.id != user.assigned_center_id:
                raise PermissionDenied("You can only register evacuees for your assigned center.")

        if user.role in ["MUNICIPAL_ADMIN", "RESPONSE_TEAM"]:
            if center.municipality_id != user.municipality_id:
                raise PermissionDenied("You can only register evacuees in your municipality.")

        serializer.save()


class DonationNeedViewSet(viewsets.ModelViewSet):
    serializer_class = DonationNeedSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = [
        "center",
        "category",
        "priority",
        "status",
    ]

    search_fields = [
        "item_name",
        "remarks",
        "center__name",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "priority",
        "quantity_needed",
        "quantity_received",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = DonationNeed.objects.select_related("center", "requested_by").all()

        # 1. Check if the user is unauthenticated or anonymous (Public Landing Page)
        if not user or user.is_anonymous:
            return DonationNeed.objects.all() 

        # 2. Handle authenticated roles safely
        if getattr(user, 'role', None) == "EVAC_CENTER_STAFF":
            # Return needs specific to staff's assigned center (if applicable)
            return DonationNeed.objects.filter(center=user.assigned_center)
        # 3. Default fallback (Admins / Superusers)
        return DonationNeed.objects.all()




        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return qs.none()
            return qs.filter(center_id=user.assigned_center_id)

        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(center__municipality_id=user.municipality_id)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        center = serializer.validated_data.get("center")

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                raise PermissionDenied("Staff has no assigned center.")
            if center.id != user.assigned_center_id:
                raise PermissionDenied("You can only create donation needs for your assigned center.")

        if user.role in ["MUNICIPAL_ADMIN", "RESPONSE_TEAM"]:
            if center.municipality_id != user.municipality_id:
                raise PermissionDenied("You can only create donation needs in your municipality.")

        serializer.save(requested_by=user)

class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = [permissions.AllowAny] # 👈 ALLOW PUBLIC PLEDGES
    authentication_classes = []                 # 👈 IGNORE STALE/MISSING TOKENS FOR PUBLIC POST
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = [
        "center",
        "need",
        "category",
        "status",
    ]

    search_fields = [
        "donor_name",
        "donor_contact",
        "donor_address",
        "item_name",
        "remarks",
        "center__name",
    ]

    ordering_fields = [
        "created_at",
        "received_at",
        "quantity",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        user = getattr(self.request, 'user', None)
        qs = Donation.objects.select_related("center", "need", "received_by").all()

        # 1. Public / Guest users (Unauthenticated)
        if user is None or not getattr(user, 'is_authenticated', False):
            return qs

        # 2. Staff filtering
        if getattr(user, 'role', None) == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return qs.none()
            # Staff should not see pledged (not-yet-received) donations
            return qs.filter(center_id=user.assigned_center_id).exclude(status="PLEDGED")

        # 3. Municipal Admin filtering
        if getattr(user, 'role', None) == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(center__municipality_id=user.municipality_id)

        return qs

    def perform_create(self, serializer):
        user = getattr(self.request, 'user', None)
        center = serializer.validated_data.get("center")
        need = serializer.validated_data.get("need")
        status_value = serializer.validated_data.get("status", "PLEDGED") # Default to PLEDGED for public
        quantity = serializer.validated_data.get("quantity", 0)

        # Only enforce role permissions if an authenticated staff/admin is creating this record
        if user and getattr(user, 'is_authenticated', False):
            if getattr(user, 'role', None) == "EVAC_CENTER_STAFF":
                if not user.assigned_center_id:
                    raise PermissionDenied("Staff has no assigned center.")
                if center and center.id != user.assigned_center_id:
                    raise PermissionDenied("You can only record donations for your assigned center.")

            if getattr(user, 'role', None) in ["MUNICIPAL_ADMIN", "RESPONSE_TEAM"]:
                if center and center.municipality_id != user.municipality_id:
                    raise PermissionDenied("You can only record donations in your municipality.")

        is_received = status_value == "RECEIVED"
        donation = serializer.save(
            received_by=user if (user and getattr(user, 'is_authenticated', False) and is_received) else None,
            received_at=timezone.now() if is_received else None,
        )

        if need and is_received:
            need.quantity_received = int(need.quantity_received or 0) + int(quantity or 0)
            need.save()

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_status = old_instance.status
        old_quantity = old_instance.quantity
        old_need = old_instance.need

        donation = serializer.save()

        new_status = donation.status
        new_quantity = donation.quantity
        new_need = donation.need

        # If old received donation is edited, remove previous quantity first
        if old_need and old_status == "RECEIVED":
            old_need.quantity_received = max(
                0,
                int(old_need.quantity_received or 0) - int(old_quantity or 0)
            )
            old_need.save()

        # Then add the new quantity if it is now received
        if new_need and new_status == "RECEIVED":
            new_need.quantity_received = int(new_need.quantity_received or 0) + int(new_quantity or 0)
            new_need.save()

            
class DonationDistributionViewSet(viewsets.ModelViewSet):
    serializer_class = DonationDistributionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = [
        "center",
        "donation",
    ]

    search_fields = [
        "item_name",
        "distributed_to",
        "remarks",
        "center__name",
    ]

    ordering_fields = [
        "distributed_at",
        "quantity_distributed",
    ]

    ordering = ["-distributed_at"]

    def get_queryset(self):
        user = self.request.user
        qs = DonationDistribution.objects.select_related(
            "center",
            "donation",
            "distributed_by"
        ).all()

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                return qs.none()
            return qs.filter(center_id=user.assigned_center_id)

        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(center__municipality_id=user.municipality_id)

        return qs

    def perform_create(self, serializer):
        user = self.request.user
        center = serializer.validated_data.get("center")
        donation = serializer.validated_data.get("donation")

        if donation.center_id != center.id:
            raise serializers.ValidationError({
                "donation": "This donation does not belong to the selected center."
            })

        if user.role == "EVAC_CENTER_STAFF":
            if not user.assigned_center_id:
                raise PermissionDenied("Staff has no assigned center.")
            if center.id != user.assigned_center_id:
                raise PermissionDenied("You can only distribute donations from your assigned center.")

        if user.role in ["MUNICIPAL_ADMIN", "RESPONSE_TEAM"]:
            if center.municipality_id != user.municipality_id:
                raise PermissionDenied("You can only distribute donations in your municipality.")

        serializer.save(distributed_by=user)

@api_view(['POST'])
@permission_classes([AllowAny])
def public_pledge_donation(request):
    data = request.data

    client_ip = get_request_ip(request)
    in_region = ip_likely_in_oriental_mindoro(client_ip)

    # Hard block only when we're confident it's NOT PH/Mindoro.
    # `None` (inconclusive) is treated as "allow, but flag".
    if in_region is False:
        return Response(
            {"error": "Pledges are currently limited to donors within Oriental Mindoro."},
            status=status.HTTP_403_FORBIDDEN
        )

    ref_code = f"PLG-{random.randint(1000, 9999)}"

    try:
        need_obj = DonationNeed.objects.filter(id=data.get('need_id')).first()

        pledge = DonationPledge.objects.create(
            need=need_obj,
            donor_name=data.get('donor_name'),
            contact_number=data.get('contact_number'),
            quantity=data.get('quantity', 1),
            dropoff_date=data.get('dropoff_date'),
            notes=data.get('notes', ''),
            reference_code=ref_code,
            status='PENDING',
            source_ip=client_ip,                # add this field for audit trail
            ip_region_flagged=(in_region is None),  # flag inconclusive ones for staff review
        )

        return Response({
            "message": "Pledge recorded successfully",
            "reference_code": pledge.reference_code
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)