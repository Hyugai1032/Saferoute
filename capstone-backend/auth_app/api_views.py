from django.db import models 
from rest_framework import generics, permissions, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import CustomUser, HazardPhoto, Municipality, Barangay
from .serializers import RegisterSerializer
from .serializers import (UserProfileSerializer, 
                          HazardReportSerializer, 
                          MunicipalitySerializer, 
                          BarangaySerializer,
                          UserListSerializer, 
                          UserDetailSerializer, 
                          UserCreateSerializer, 
                          UserUpdateSerializer,
                          MeUpdateSerializer)

from .permissions import (
    IsProvincialAdmin, 
    IsMunicipalAdminOrHigher, 
    IsStaffOrHigher,
    IsOwnerOrAdmin
)

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "User created successfully",
            "user_id": user.id,
            "role": user.role
        })

    
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    

class HazardReportView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = HazardReportSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            mun = getattr(user, "municipality", None) or serializer.validated_data.get("municipality")
            if not mun:
                return Response({"municipality": "Municipality is required."}, status=400)

            report = serializer.save(
                reporter=user,
                municipality=mun,
                status="REPORTED"
            )
            return Response(HazardReportSerializer(report).data, status=201)

        return Response(serializer.errors, status=400)        
class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipality.objects.all().order_by('name')
    serializer_class = MunicipalitySerializer
    permission_classes = [AllowAny]
    
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
    queryset = CustomUser.objects.select_related('municipality').all()
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

