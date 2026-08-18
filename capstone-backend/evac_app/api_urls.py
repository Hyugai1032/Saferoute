# capstone-backend/evac_app/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import EvacUploadAPIView, EvacuationCenterViewSet, EvacuationLogViewSet, EvacuationCenterListViewSet, EvacueeViewSet, DonationNeedViewSet, DonationViewSet, DonationDistributionViewSet, EvacuationReasonViewSet

router = DefaultRouter()
router.register(r'evac-centers', EvacuationCenterViewSet, basename='evac-center')
router.register(r"evacuation-centers", EvacuationCenterListViewSet, basename="evacuation-centers")
router.register(r"evacuation-logs", EvacuationLogViewSet, basename="evacuation-logs")
router.register(r"evacuees", EvacueeViewSet, basename="evacuees")
router.register(r'evacuation-reasons', EvacuationReasonViewSet, basename='evacuation-reasons')
router.register(r"donation-needs", DonationNeedViewSet, basename="donation-needs")
router.register(r"donations", DonationViewSet, basename="donations")
router.register(
    r"donation-distributions",
    DonationDistributionViewSet,
    basename="donation-distributions"
)
router.register(
    r"evac-center-dropdown",
    EvacuationCenterListViewSet,
    basename="evac-center-dropdown"
)

urlpatterns = [
    # custom routes FIRST
    path('evac-centers/upload/', EvacUploadAPIView.as_view(), name='evac-upload'),
    
    # then router
    path('', include(router.urls)),
]
