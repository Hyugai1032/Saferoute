import os
import requests
from datetime import timedelta
from django.utils import timezone
from django.apps import apps
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models 
from django.db.models import F
from django.core.mail import send_mail
from rest_framework import generics, permissions, viewsets, filters, status
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import AnonymousUser
from .models import CustomUser, HazardPhoto, Municipality, Barangay, GisLayer, HazardReport, EmailOTP
from .serializers import RegisterSerializer
from .serializers import (UserProfileSerializer, 
                          HazardReportSerializer, 
                          MunicipalitySerializer, 
                          BarangaySerializer,
                          UserListSerializer, 
                          UserDetailSerializer, 
                          UserCreateSerializer, 
                          UserUpdateSerializer,
                          UserProfileSerializer,
                          MeUpdateSerializer,
                          GisLayerSerializer,
                          EvacCenterPinSerializer,
                          HazardPinSerializer,
                          HazardReportAdminUpdateSerializer,
                          NearbyHazardAlertSerializer)
from evac_app.serializers import EvacuationCenterSerializer
from .permissions import (
    IsProvincialAdmin, 
    IsMunicipalAdminOrHigher, 
    IsStaffOrHigher,
    IsOwnerOrAdmin,
    GisLayerRolePermission
)
from analytics_app.services.congestion import compute_congestion_risk, CongestionParams

EvacuationCenter = apps.get_model("evac_app", "EvacuationCenter")
EvacuationLog = apps.get_model("evac_app", "EvacuationLog")


def verify_recaptcha(token, remote_ip=None):
    """
    Verifies a Google reCAPTCHA v2 token against Google's siteverify endpoint.
    Returns (True, None) on success, or (False, error_detail) on failure.
    """
    secret_key = getattr(settings, "RECAPTCHA_SECRET_KEY", None)

    # Allow disabling captcha in local/dev environments explicitly via settings.
    if getattr(settings, "RECAPTCHA_DISABLED", False):
        return True, None

    if not secret_key:
        return False, "Captcha is not configured on the server."

    if not token:
        return False, "Captcha verification is required."

    try:
        resp = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": secret_key,
                "response": token,
                **({"remoteip": remote_ip} if remote_ip else {}),
            },
            timeout=10,
        )
        result = resp.json()
    except requests.RequestException:
        return False, "Could not reach captcha verification service."
    except ValueError:
        return False, "Unexpected response from captcha verification service."

    if not result.get("success"):
        return False, "Captcha verification failed. Please try again."

    return True, None

OTP_EXPIRY_MINUTES = 10
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5
# Window after verification during which the user must finish submitting the register form.
OTP_VERIFIED_WINDOW_MINUTES = 15


def send_otp_email(email, code):
    send_mail(
        subject="Your SafeRoute verification code",
        message=(
            f"Your verification code is: {code}\n\n"
            f"This code expires in {OTP_EXPIRY_MINUTES} minutes. "
            "If you didn't request this, you can safely ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )


class SendRegisterOTPView(APIView):
    """Issues a one-time email verification code for the registration flow."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"email": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email__iexact=email).exists():
            return Response(
                {"email": "An account with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing = (
            EmailOTP.objects
            .filter(email__iexact=email, purpose="REGISTER")
            .order_by("-created_at")
            .first()
        )
        if existing:
            wait_left = (
                existing.created_at + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS) - timezone.now()
            ).total_seconds()
            if wait_left > 0:
                return Response(
                    {"detail": f"Please wait {int(wait_left)}s before requesting another code."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        code = EmailOTP.generate_code()
        otp = EmailOTP(
            email=email,
            purpose="REGISTER",
            expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        )
        otp.set_code(code)
        otp.save()

        try:
            send_otp_email(email, code)
        except Exception:
            otp.delete()
            return Response(
                {"detail": "Failed to send verification email. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response({
            "detail": "Verification code sent.",
            "expires_in": OTP_EXPIRY_MINUTES * 60,
        })


class VerifyRegisterOTPView(APIView):
    """Checks a code submitted for the registration flow and marks the email verified."""
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        code = (request.data.get("otp_code") or "").strip()

        if not email or not code:
            return Response(
                {"detail": "Email and verification code are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp = (
            EmailOTP.objects
            .filter(email__iexact=email, purpose="REGISTER")
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return Response(
                {"otp_code": "No verification code found for this email. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp.is_verified:
            return Response({"detail": "Email already verified."})

        if otp.is_expired():
            return Response(
                {"otp_code": "This code has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp.attempts >= OTP_MAX_ATTEMPTS:
            return Response(
                {"otp_code": "Too many incorrect attempts. Please request a new code."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not otp.check_code(code):
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            remaining = OTP_MAX_ATTEMPTS - otp.attempts
            return Response(
                {"otp_code": f"Incorrect code. {remaining} attempt(s) remaining."},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp.is_verified = True
        otp.verified_at = timezone.now()
        otp.save(update_fields=["is_verified", "verified_at"])

        return Response({"detail": "Email verified."})

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        captcha_token = request.data.get("captcha_token")
        is_valid, error = verify_recaptcha(captcha_token, remote_ip=request.META.get("REMOTE_ADDR"))
        if not is_valid:
            return Response({"captcha_token": error}, status=status.HTTP_400_BAD_REQUEST)

        email = (request.data.get("email") or "").strip().lower()
        otp = (
            EmailOTP.objects
            .filter(email__iexact=email, purpose="REGISTER", is_verified=True)
            .order_by("-created_at")
            .first()
        )

        if not otp:
            return Response(
                {"email": "Please verify your email with the code sent to you before registering."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > otp.verified_at + timedelta(minutes=OTP_VERIFIED_WINDOW_MINUTES):
            return Response(
                {"email": "Your email verification has expired. Please verify your email again."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # OTP is single-use; remove it now that registration is complete.
        otp.delete()

        return Response({
            "message": "User created successfully",
            "user_id": user.id,
            "role": user.role
        })

def send_password_reset_otp_email(email, code):
    send_mail(
        subject="Your SafeRoute password reset code",
        message=(
            f"Your password reset code is: {code}\n\n"
            f"This code expires in {OTP_EXPIRY_MINUTES} minutes. "
            "If you didn't request this, you can safely ignore this email — "
            "your password will not be changed."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

class SendPasswordResetOTPView(APIView):
    """
    Issues a one-time code for the password-reset flow.
 
    Deliberately returns the SAME generic success response whether or not an
    account exists for the given email, so the endpoint can't be used to
    enumerate registered accounts. The OTP row (and cooldown/rate-limit) is
    only ever created when a matching account exists.
    """
    permission_classes = [AllowAny]
 
    GENERIC_RESPONSE = {
        "detail": "If an account exists for this email, a verification code has been sent.",
        "expires_in": OTP_EXPIRY_MINUTES * 60,
    }
 
    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"email": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
 
        user = CustomUser.objects.filter(email__iexact=email).first()
 
        # No account -> pretend everything is fine, don't create an OTP, don't send mail.
        if not user:
            return Response(self.GENERIC_RESPONSE)
 
        existing = (
            EmailOTP.objects
            .filter(email__iexact=email, purpose="RESET_PASSWORD")
            .order_by("-created_at")
            .first()
        )
        if existing:
            wait_left = (
                existing.created_at + timedelta(seconds=OTP_RESEND_COOLDOWN_SECONDS) - timezone.now()
            ).total_seconds()
            if wait_left > 0:
                # NOTE: this 429 only ever fires for real accounts, which is a very
                # minor enumeration signal (an attacker could infer existence by
                # spamming requests and checking for 429 vs 200). Acceptable for
                # most apps; switch to always-200 + silent no-op if you need to
                # fully close that gap.
                return Response(
                    {"detail": f"Please wait {int(wait_left)}s before requesting another code."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
 
        code = EmailOTP.generate_code()
        otp = EmailOTP(
            email=email,
            purpose="RESET_PASSWORD",
            expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        )
        otp.set_code(code)
        otp.save()
 
        try:
            send_password_reset_otp_email(email, code)
        except Exception:
            otp.delete()
            return Response(
                {"detail": "Failed to send verification email. Please try again."},
                status=status.HTTP_502_BAD_GATEWAY
            )
 
        return Response(self.GENERIC_RESPONSE)
 
 
class ResetPasswordView(APIView):
    """
    Verifies the OTP and sets the new password in a single call.
    Mirrors VerifyRegisterOTPView's attempt/expiry/lockout logic, then
    applies the new password immediately on success.
    """
    permission_classes = [AllowAny]
 
    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        code = (request.data.get("otp_code") or "").strip()
        new_password = request.data.get("new_password")
 
        if not email or not code or not new_password:
            return Response(
                {"detail": "Email, verification code, and new password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        # Enforce your project's password rules (length, common-password check, etc.)
        try:
            validate_password(new_password)
        except DjangoValidationError as e:
            return Response({"new_password": e.messages}, status=status.HTTP_400_BAD_REQUEST)
 
        otp = (
            EmailOTP.objects
            .filter(email__iexact=email, purpose="RESET_PASSWORD")
            .order_by("-created_at")
            .first()
        )
 
        if not otp:
            return Response(
                {"otp_code": "No verification code found for this email. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        if otp.is_expired():
            return Response(
                {"otp_code": "This code has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        if otp.attempts >= OTP_MAX_ATTEMPTS:
            return Response(
                {"otp_code": "Too many incorrect attempts. Please request a new code."},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        if not otp.check_code(code):
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            remaining = OTP_MAX_ATTEMPTS - otp.attempts
            return Response(
                {"otp_code": f"Incorrect code. {remaining} attempt(s) remaining."},
                status=status.HTTP_400_BAD_REQUEST
            )
 
        user = CustomUser.objects.filter(email__iexact=email).first()
        if not user:
            # OTP was only ever created for an existing account, so this shouldn't
            # happen in practice (e.g. account deleted mid-flow) — guard anyway.
            otp.delete()
            return Response({"detail": "Unable to reset password."}, status=status.HTTP_400_BAD_REQUEST)
 
        user.set_password(new_password)
        user.save(update_fields=["password"])
 
        # OTP is single-use
        otp.delete()
 
        # Optional but recommended: if you're using JWT (SimpleJWT etc.), blacklist
        # this user's outstanding refresh tokens here so old sessions can't
        # continue using a password that's just been changed.
 
        return Response({"detail": "Password has been reset successfully."})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HazardReportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self, request):
        user = request.user
        qs = HazardReport.objects.all().order_by("-id")

        # Municipal admin: only their municipality
        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(municipality_id=user.municipality_id)

        # Evacuation center staff / response team: usually same municipality scope
        if user.role in ["EVAC_CENTER_STAFF", "RESPONSE_TEAM"]:
            if not user.municipality_id:
                return qs.none()
            return qs.filter(municipality_id=user.municipality_id)

        # Provincial admin can see all
        return qs

    def get(self, request):
        status_param = request.query_params.get("status")
        severity_param = request.query_params.get("severity")
        mine = request.query_params.get("mine")

        qs = self.get_queryset(request)

        if status_param and status_param.lower() != "all":
            qs = qs.filter(status=status_param)

        if severity_param and severity_param.lower() != "all":
            qs = qs.filter(severity__iexact=severity_param)

        if mine in ["1", "true", "True"]:
            qs = qs.filter(reporter=request.user)

        serializer = HazardReportSerializer(qs, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = HazardReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        # Lock municipality for municipal admin / staff
        if user.role in ["MUNICIPAL_ADMIN", "EVAC_CENTER_STAFF", "RESPONSE_TEAM"]:
            if not user.municipality:
                return Response(
                    {"municipality": "Your account has no municipality assigned."},
                    status=400
                )
            mun = user.municipality
        else:
            mun = getattr(user, "municipality", None) or serializer.validated_data.get("municipality")

        if not mun:
            return Response({"municipality": "Municipality is required."}, status=400)

        report = serializer.save(
            reporter=user,
            municipality=mun,
            status="REPORTED"
        )
        return Response(
            HazardReportSerializer(report, context={"request": request}).data,
            status=201
        )     

class HazardReportDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self, request):
        user = request.user
        qs = HazardReport.objects.all()

        if user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                return qs.none()
            return qs.filter(municipality_id=user.municipality_id)

        if user.role in ["EVAC_CENTER_STAFF", "RESPONSE_TEAM"]:
            if not user.municipality_id:
                return qs.none()
            return qs.filter(municipality_id=user.municipality_id)

        return qs

    def get_object(self, request, pk):
        try:
            return self.get_queryset(request).get(pk=pk)
        except HazardReport.DoesNotExist:
            raise NotFound("Hazard report not found.")

    def get(self, request, pk):
        report = self.get_object(request, pk)
        return Response(HazardReportSerializer(report, context={"request": request}).data)

    def patch(self, request, pk):
        report = self.get_object(request, pk)

        role = getattr(request.user, "role", None)
        if role not in ["PROVINCIAL_ADMIN", "MUNICIPAL_ADMIN", "EVAC_CENTER_STAFF", "RESPONSE_TEAM"]:
            raise PermissionDenied("You are not allowed to update hazard reports.")

        serializer = HazardReportAdminUpdateSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        if "status" in serializer.validated_data:
            updated.reviewed_by = request.user
            updated.reviewed_at = timezone.now()

            new_status = serializer.validated_data["status"]

            if new_status == "APPROVED":
                updated.validated_at = timezone.now()
                updated.dismissed_at = None

            elif new_status == "DISMISSED":
                updated.dismissed_at = timezone.now()
                updated.validated_at = None

            elif new_status == "REPORTED":
                updated.validated_at = None
                updated.dismissed_at = None

            updated.save(update_fields=[
                "reviewed_by",
                "reviewed_at",
                "validated_at",
                "dismissed_at",
            ])
            
        return Response(
            HazardReportSerializer(updated, context={"request": request}).data,
            status=200
        )   
    
class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipality.objects.all().order_by('name')
    serializer_class = MunicipalitySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    
    @action(detail=True, methods=['get'])
    def barangays(self, request, pk=None):
        municipality = self.get_object()
        barangays = Barangay.objects.filter(municipality=municipality).order_by('name')
        serializer = BarangaySerializer(barangays, many=True)
        return Response(serializer.data)

class BarangayViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Barangay.objects.all().order_by('name')
    serializer_class = BarangaySerializer
    permission_classes = [AllowAny]
    pagination_class = None
    
    def get_queryset(self):
        queryset = Barangay.objects.all().order_by('name')
        municipality_id = self.request.query_params.get('municipality', None)
        if municipality_id is not None:
            queryset = queryset.filter(municipality_id=municipality_id)
        return queryset
    
class UserViewSet(viewsets.ModelViewSet):
    """
    User Management CRUD
    
    Endpoints:
    - GET    /api/users/           → List users (filtered by role permissions)
    - POST   /api/users/           → Create user (Admin only)
    - GET    /api/users/{id}/      → Get user details
    - PATCH  /api/users/{id}/      → Update user
    - DELETE /api/users/{id}/      → Delete user (Provincial Admin only)
    - GET    /api/users/me/        → Get current user profile
    - PATCH  /api/users/me/        → Update current user profile
    - GET    /api/users/stats/     → Get user statistics
    """
    queryset = CustomUser.objects.select_related('municipality', 'assigned_center').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'municipality', 'is_active']
    search_fields = ['email', 'first_name', 'last_name', 'contact_number']
    ordering_fields = ['created_at', 'email', 'role', 'first_name']
    ordering = ['-created_at']

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            # Only admins can create users
            permission_classes = [IsMunicipalAdminOrHigher]
        elif self.action == 'destroy':
            # Only provincial admin can delete
            permission_classes = [IsProvincialAdmin]
        elif self.action in ['list', 'stats']:
            # Staff and above can view list
            permission_classes = [IsStaffOrHigher]
        elif self.action in ['me']:
            # Any authenticated user can access their own profile
            permission_classes = [IsAuthenticated]
        else:
            # retrieve, update, partial_update
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer   # ✅ admin updating other users
        elif self.action == 'me' and self.request.method == 'PATCH':
            return MeUpdateSerializer     # ✅ self-update only
        return UserDetailSerializer


    def get_queryset(self):
        """Filter queryset based on user's role and municipality"""
        user = self.request.user
        queryset = super().get_queryset()

        if user.role == 'PROVINCIAL_ADMIN':
            # Provincial admin sees all users
            return queryset
        elif user.role == 'MUNICIPAL_ADMIN':
            # Municipal admin sees users in their municipality only
            return queryset.filter(municipality=user.municipality)
        elif user.role in ['RESPONSE_TEAM', 'EVAC_CENTER_STAFF']:
            # Staff sees users in their municipality
            return queryset.filter(municipality=user.municipality)
        else:
            # Citizens can only see themselves
            return queryset.filter(id=user.id)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        if request.method == 'GET':
            serializer = UserDetailSerializer(request.user)
            return Response(serializer.data)

        serializer = MeUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserDetailSerializer(request.user).data)


    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics for dashboard"""
        user = request.user
        
        # Base queryset based on user's access level
        if user.role == 'PROVINCIAL_ADMIN':
            queryset = CustomUser.objects.all()
        else:
            queryset = CustomUser.objects.filter(municipality=user.municipality)

        stats = {
            'total_users': queryset.count(),
            'active_users': queryset.filter(is_active=True).count(),
            'by_role': {
                'citizen': queryset.filter(role='CITIZEN').count(),
                'provincial_admin': queryset.filter(role='PROVINCIAL_ADMIN').count(),
                'municipal_admin': queryset.filter(role='MUNICIPAL_ADMIN').count(),
                'response_team': queryset.filter(role='RESPONSE_TEAM').count(),
                'evac_center_staff': queryset.filter(role='EVAC_CENTER_STAFF').count(),
            },
        }
        
        # Add municipality breakdown for provincial admin
        if user.role == 'PROVINCIAL_ADMIN':
            stats['by_municipality'] = list(
                CustomUser.objects
                .values('municipality__name')
                .annotate(count=models.Count('id'))
                .order_by('-count')
            )
        
        return Response(stats)
    
    def perform_update(self, serializer):
        actor = self.request.user
        target = self.get_object()

        # values being changed (fall back to existing)
        new_municipality = serializer.validated_data.get("municipality", target.municipality)
        new_role = serializer.validated_data.get("role", target.role)
        new_center = serializer.validated_data.get("assigned_center", target.assigned_center)

        # --- MUNICIPAL ADMIN restrictions ---
        if actor.role == "MUNICIPAL_ADMIN":
            # can only edit users in their municipality
            if target.municipality_id != actor.municipality_id:
                raise PermissionDenied("You can only manage users in your municipality.")

            # cannot move user to another municipality
            if new_municipality and new_municipality.id != actor.municipality_id:
                raise PermissionDenied("You cannot assign users to another municipality.")

            # cannot assign center outside their municipality
            if new_center and hasattr(new_center, "municipality_id"):
                if new_center.municipality_id != actor.municipality_id:
                    raise PermissionDenied("You can only assign centers within your municipality.")

            # (optional) cannot promote users to provincial admin
            if "role" in serializer.validated_data and new_role == "PROVINCIAL_ADMIN":
                raise PermissionDenied("You cannot assign PROVINCIAL_ADMIN role.")

        # --- STAFF restrictions (optional safety) ---
        if actor.role in ["RESPONSE_TEAM", "EVAC_CENTER_STAFF"]:
            raise PermissionDenied("You do not have permission to update other users.")

        serializer.save()


class GisLayerViewSet(viewsets.ModelViewSet):
    serializer_class = GisLayerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = GisLayer.objects.select_related("municipality").order_by("-updated_at")

        user = self.request.user or AnonymousUser()
        if user.is_authenticated and user.role == "MUNICIPAL_ADMIN":
            user_mun = getattr(user, "municipality", None)
            if user_mun:
                qs = qs.filter(municipality_id=user_mun.id)
            else:
                qs = qs.none()

        municipality_id = self.request.query_params.get("municipality_id")
        if municipality_id:
            qs = qs.filter(municipality_id=municipality_id)

        # optional: search by name
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(name__icontains=q)

        return qs

    @action(detail=False, methods=["get"], url_path="latest")
    def latest(self, request):
        """
        GET /api/gis-layers/latest/
        GET /api/gis-layers/latest/?municipality_id=5
        """
        qs = self.get_queryset()
        layer = qs.first()
        if not layer:
            return Response({"detail": "No GIS layers found."}, status=404)
        return Response(self.get_serializer(layer).data)

def get_center_prediction(center, window=60, horizon=60):
    result = compute_congestion_risk(
        center=center,
        EvacuationLogModel=EvacuationLog,
        params=CongestionParams(
            window_minutes=window,
            horizon_minutes=horizon
        ),
    )

    if "error" in result:
        return {
            "predicted_congestion_percent": None,
            "predicted_status": "UNAVAILABLE",
            "prediction_note": result.get("error"),
        }

    predicted = (
        result.get("predicted_congestion_percent")
        or result.get("predicted_percent")
        or result.get("risk_percent")
        or result.get("congestion_percent")
        or 0
    )

    predicted = round(float(predicted), 1)

    if predicted >= 90:
        status = "LIKELY_FULL"
    elif predicted >= 70:
        status = "MAY_BECOME_CROWDED"
    else:
        status = "LIKELY_AVAILABLE"

    return {
        "predicted_congestion_percent": predicted,
        "predicted_status": status,
        "prediction_window_minutes": horizon,
    }

class MapOverviewView(APIView):
    """
    GET /api/map/overview/?recent_hours=48&municipality_id=3
    Returns center pins + recent hazard pins.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        recent_hours = int(request.query_params.get("recent_hours", 48))
        user = request.user or AnonymousUser()
        requested_municipality_id = request.query_params.get("municipality_id")

        centers_qs = EvacuationCenter.objects.all()
        since = timezone.now() - timedelta(hours=recent_hours)
        hazards_qs = HazardReport.objects.filter(
            validated_at__gte=since,
            status="APPROVED"
        )

        # Only apply role-based restrictions to authenticated users
        if user.is_authenticated and user.role == "MUNICIPAL_ADMIN":
            if not user.municipality_id:
                centers_qs = centers_qs.none()
                hazards_qs = hazards_qs.none()
            else:
                centers_qs = centers_qs.filter(
                    municipality_id=user.municipality_id
                )
                hazards_qs = hazards_qs.filter(
                    municipality_id=user.municipality_id
                )

        elif user.is_authenticated and user.role in [
            "EVAC_CENTER_STAFF",
            "RESPONSE_TEAM"
        ]:
            if not user.municipality_id:
                centers_qs = centers_qs.none()
                hazards_qs = hazards_qs.none()
            else:
                centers_qs = centers_qs.filter(
                    municipality_id=user.municipality_id
                )
                hazards_qs = hazards_qs.filter(
                    municipality_id=user.municipality_id
                )

        elif requested_municipality_id and (
            not user.is_authenticated
            or user.role not in [
                "MUNICIPAL_ADMIN",
                "EVAC_CENTER_STAFF",
                "RESPONSE_TEAM"
            ]
        ):
            # Authenticated broader roles and anonymous users
            # may use the municipality filter.
            centers_qs = centers_qs.filter(
                municipality_id=requested_municipality_id
            )
            hazards_qs = hazards_qs.filter(
                municipality_id=requested_municipality_id
            )

        centers_data = EvacuationCenterSerializer(
            centers_qs,
            many=True,
            context={"request": request},
        ).data

        center_objects = {c.id: c for c in centers_qs}

        window = int(
            request.query_params.get("prediction_window", 60)
        )
        horizon = int(
            request.query_params.get("prediction_horizon", 60)
        )

        for center_data in centers_data:
            center_obj = center_objects.get(center_data["id"])
            if not center_obj:
                continue

            try:
                center_data.update(
                    get_center_prediction(
                        center_obj,
                        window=window,
                        horizon=horizon
                    )
                )
            except Exception:
                center_data.update({
                    "predicted_congestion_percent": None,
                    "predicted_status": "UNAVAILABLE",
                    "prediction_note": "Prediction failed for this center.",
                })

        return Response({
            "centers": centers_data,
            "hazards": HazardPinSerializer(
                hazards_qs,
                many=True
            ).data,
        })
    
def circle_to_polygon(lng, lat, radius_m=150, points=24):
    """
    Approximate a circle as a polygon around (lng,lat).
    GeoJSON expects [lng, lat].
    """
    import math
    # rough conversion
    lat_r = radius_m / 111_320.0
    lng_r = radius_m / (111_320.0 * math.cos(math.radians(lat)) + 1e-9)

    coords = []
    for i in range(points):
        ang = 2 * math.pi * i / points
        coords.append([lng + lng_r * math.cos(ang), lat + lat_r * math.sin(ang)])
    coords.append(coords[0])  # close ring
    return coords

import math

def haversine_km(lat1, lng1, lat2, lng2):
    lat1 = float(lat1)
    lng1 = float(lng1)
    lat2 = float(lat2)
    lng2 = float(lng2)

    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlng / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def get_latest_center_occupancy(center):
    log = (
        EvacuationLog.objects
        .filter(center_id=center.id)
        .order_by("-date_recorded", "-id")
        .first()
    )

    if not log:
        return {
            "current_total": 0,
            "current_families": 0,
            "congestion_percent": 0.0,
        }

    capacity = int(center.family_capacity_max or 0) + int(center.individual_capacity_max or 0)
    current_total = int(log.total_current or 0)
    current_families = int(log.total_current_families or 0)

    congestion_percent = round((current_total / capacity) * 100, 1) if capacity > 0 else 0.0

    return {
        "current_total": current_total,
        "current_families": current_families,
        "congestion_percent": congestion_percent,
    }

class ORSRouteView(APIView):
    """
    POST /api/route/ors/

    Body:
    {
      "from": {"lat": 13.12, "lng": 121.12},
      "to":   {"lat": 13.22, "lng": 121.25},
      "avoid_hazards": true,
      "recent_hours": 48,
      "hazard_radius_m": 150
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        ors_key = settings.ORS_API_KEY
        if not ors_key:
            return Response({"detail": "ORS_API_KEY is not set on the server."}, status=500)

        body = request.data or {}
        try:
            f = body["from"]
            t = body["to"]
            from_lat = float(f["lat"])
            from_lng = float(f["lng"])
            to_lat = float(t["lat"])
            to_lng = float(t["lng"])
        except Exception:
            return Response({"detail": "Body must include from{lat,lng} and to{lat,lng}."}, status=400)

        avoid_hazards = bool(body.get("avoid_hazards", False))
        recent_hours = int(body.get("recent_hours", 48))
        hazard_radius_m = int(body.get("hazard_radius_m", 150))

        ors_url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
        headers = {
            "Authorization": ors_key,  # ORS uses Authorization header :contentReference[oaicite:1]{index=1}
            "Content-Type": "application/json",
            "Accept": "application/geo+json",
        }

        payload = {
            # ORS coordinates order is [lng, lat]
            "coordinates": [[from_lng, from_lat], [to_lng, to_lat]],
        }

        # Optional hazard avoidance via avoid_polygons (GeoJSON) :contentReference[oaicite:2]{index=2}
        if avoid_hazards:
            since = timezone.now() - timedelta(hours=recent_hours)
            hz = (HazardReport.objects
                  .filter(validated_at__gte=since, status = "APPROVED")
                  .exclude(latitude__isnull=True)
                  .exclude(longitude__isnull=True))

            rings = []
            for h in hz:
                lat = float(h.latitude)
                lng = float(h.longitude)
                rings.append(circle_to_polygon(lng, lat, radius_m=hazard_radius_m, points=28))

            if rings:
                # MultiPolygon: [ [ [lng,lat] ring ] , ... ]
                multipoly = {
                    "type": "MultiPolygon",
                    "coordinates": [[[ring] for ring in rings]][0]  # each polygon has one ring
                }
                payload["options"] = {"avoid_polygons": multipoly}

        try:
            r = requests.post(ors_url, json=payload, headers=headers, timeout=25)
        except requests.RequestException:
            return Response({"detail": "ORS request failed (network/timeout)."}, status=502)

        if r.status_code != 200:
            return Response({"detail": "ORS error", "status": r.status_code, "body": r.text[:500]}, status=502)

        data = r.json()

        # ORS GeoJSON response contains features[0].properties.summary + geometry
        try:
            feat = data["features"][0]
            summary = feat["properties"]["summary"]
            geometry = feat["geometry"]  # LineString GeoJSON
        except Exception:
            return Response({"detail": "Unexpected ORS response format."}, status=502)

        return Response({
            "distance_m": summary.get("distance"),
            "duration_s": summary.get("duration"),
            "geometry": geometry,
            "used_hazard_avoidance": avoid_hazards,
        })
    
class NearbyHazardAlertsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        if not lat or not lng:
            return Response(
                {"detail": "lat and lng are required."},
                status=400
            )

        try:
            user_lat = float(lat)
            user_lng = float(lng)
            radius_km = float(request.query_params.get("radius_km", 3))
            recent_hours = int(request.query_params.get("recent_hours", 24))
        except ValueError:
            return Response(
                {"detail": "lat, lng, radius_km, and recent_hours must be valid numbers."},
                status=400
            )

        recent_cutoff = timezone.now() - timedelta(hours=recent_hours)

        hazards = HazardReport.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            status="APPROVED",
            validated_at__gte=recent_cutoff,
        )

        nearby_hazards = []

        for hazard in hazards:
            distance = haversine_km(
                user_lat,
                user_lng,
                hazard.latitude,
                hazard.longitude
            )

            if distance <= radius_km:
                hazard.distance_km = distance
                nearby_hazards.append(hazard)

        nearby_hazards.sort(key=lambda h: h.distance_km)

        serializer = NearbyHazardAlertSerializer(nearby_hazards, many=True)
        return Response(serializer.data)

class SuggestNearestAvailableCenterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ors_key = settings.ORS_API_KEY
        if not ors_key:
            return Response({"detail": "ORS_API_KEY is not set."}, status=500)

        body = request.data or {}

        try:
            origin = body["from"]
            from_lat = float(origin["lat"])
            from_lng = float(origin["lng"])
        except Exception:
            return Response({"detail": "Missing from.lat/lng"}, status=400)

        max_congestion = float(body.get("max_congestion_percent", 90))
        candidate_limit = int(body.get("candidate_limit", 6))
        avoid_hazards = bool(body.get("avoid_hazards", True))

        # --- FILTER CENTERS ---
        centers = (
            EvacuationCenter.objects
            .exclude(latitude__isnull=True)
            .exclude(longitude__isnull=True)
            .annotate(total_capacity=F('family_capacity_max') + F('individual_capacity_max'))
            .filter(total_capacity__gt=0)  # 🔥 EXCLUDE 0/0
        )

        candidates = []
        for c in centers:
            occ = get_latest_center_occupancy(c)

            if occ["congestion_percent"] >= max_congestion:
                continue

            candidates.append({
                "center": c,
                "lat": float(c.latitude),
                "lng": float(c.longitude),
                "congestion": occ["congestion_percent"],
                "distance": haversine_km(from_lat, from_lng, float(c.latitude), float(c.longitude))
            })

        if not candidates:
            return Response({"detail": "No available centers"}, status=404)

        # --- PREFILTER NEAREST ---
        candidates.sort(key=lambda x: x["distance"])
        candidates = candidates[:candidate_limit]

        # --- ROUTE USING ORS ---
        ors_url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
        headers = {
            "Authorization": ors_key,
            "Content-Type": "application/json"
        }

        results = []

        for item in candidates:
            payload = {
                "coordinates": [
                    [from_lng, from_lat],
                    [item["lng"], item["lat"]],
                ],
                "radiuses": [2000, 2000]
            }

            try:
                r = requests.post(ors_url, json=payload, headers=headers, timeout=20)
                if r.status_code != 200:
                    continue

                data = r.json()
                feat = data["features"][0]
                summary = feat["properties"]["summary"]

                duration = summary["duration"]
                distance = summary["distance"]

                eta_min = duration / 60

                # 🔥 KEY CHANGE: ETA + congestion scoring
                score = (eta_min * 0.8) + (item["congestion"] * 0.2)

                results.append({
                    "center": item["center"],
                    "geometry": feat["geometry"],
                    "distance_m": distance,
                    "duration_s": duration,
                    "score": score
                })

            except Exception:
                continue

        if not results:
            return Response({"detail": "No routable centers"}, status=404)

        results.sort(key=lambda x: x["score"])
        best = results[0]

        return Response({
            "center": EvacuationCenterSerializer(best["center"]).data,
            "distance_m": best["distance_m"],
            "duration_s": best["duration_s"],
            "geometry": best["geometry"],
            "score": best["score"]
        })


# users/api_views.py (example)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        data = {
            "id": u.id,
            "email": u.email,
            "first_name": getattr(u, "first_name", ""),
            "last_name": getattr(u, "last_name", ""),
            "role": getattr(u, "role", ""),
            "municipality": getattr(getattr(u, "municipality", None), "name", None),
            "assigned_center_id": getattr(u, "assigned_center_id", None),
            "assigned_center_name": getattr(getattr(u, "assigned_center", None), "name", None),
        }
        return Response(data)

class UpdateMeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        u = request.user
        # whitelist fields you allow editing
        for field in ["first_name", "last_name"]:
            if field in request.data:
                setattr(u, field, request.data.get(field))
        u.save()
        return Response({"detail": "Profile updated."}, status=status.HTTP_200_OK)