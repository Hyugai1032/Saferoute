from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    UserProfileView,
    RegisterView,
    MunicipalityViewSet,
    BarangayViewSet,
    UserViewSet,
    GisLayerViewSet
)

from .views import HazardReportView   # ✅ IMPORTANT

#from .api_views import UserProfileView, HazardReportView, RegisterView, MunicipalityViewSet, BarangayViewSet, UserViewSet
# from .views import HazardPendingList, HazardCreate
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'municipalities', MunicipalityViewSet, basename='municipality')
router.register(r'barangays', BarangayViewSet, basename='barangay')
router.register(r"gis-layers", GisLayerViewSet, basename="gis-layers")

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('hazards/', HazardReportView.as_view()),
    path('hazards/<int:pk>/', HazardReportView.as_view()),
    path('', include(router.urls)),
    # path("hazards/pending", HazardPendingList.as_view()),
]