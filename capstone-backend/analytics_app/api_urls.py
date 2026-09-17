from django.urls import path
from .api_views import (CenterCongestionRiskView, AnalyticsStatsView, AffectedPopulationReportView, BulkCongestionRiskView)

urlpatterns = [
    path("centers/<int:center_id>/congestion-risk/", CenterCongestionRiskView.as_view()),
    path("centers/congestion-risk-bulk/", BulkCongestionRiskView.as_view()),
    path('stats/', AnalyticsStatsView.as_view(), name='analytics_stats'),
    path("reports/affected-population/", AffectedPopulationReportView.as_view(), name="affected_population_report"),
    # Other URLs...
]