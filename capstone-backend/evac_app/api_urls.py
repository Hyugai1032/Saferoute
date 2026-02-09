# capstone-backend/evac_app/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import EvacUploadAPIView, EvacuationCenterViewSet, EvacuationLogViewSet

router = DefaultRouter()
router.register(r'evac-centers', EvacuationCenterViewSet, basename='evac-center')
router.register(r"evacuation-logs", EvacuationLogViewSet, basename="evacuation-logs")

urlpatterns = [
    # custom routes FIRST
    path('evac-centers/upload/', EvacUploadAPIView.as_view(), name='evac-upload'),
    
    # then router
    path('', include(router.urls)),
]
