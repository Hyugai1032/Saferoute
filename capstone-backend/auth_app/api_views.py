from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import CustomUser, HazardPhoto, Municipality, Barangay
from .serializers import RegisterSerializer
from .serializers import UserProfileSerializer, HazardReportSerializer, MunicipalitySerializer, BarangaySerializer

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
    def post(self, request):
        serializer = HazardReportSerializer(data=request.data)

        if serializer.is_valid():
            report = serializer.save()
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

