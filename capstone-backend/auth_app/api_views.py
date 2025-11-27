from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import CustomUser, HazardPhoto
from .serializers import RegisterSerializer
from .serializers import UserProfileSerializer, HazardReportSerializer

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

