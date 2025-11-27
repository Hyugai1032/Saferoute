from django.urls import path
from .api_views import UserProfileView, HazardReportView, RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('hazards/', HazardReportView.as_view(), name='hazard_report')
]