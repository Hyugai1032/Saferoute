from django.urls import path
from .api_views import (predict_weather_view, CenterCongestionRiskView, AnalyticsStatsView, AffectedPopulationReportView)

urlpatterns = [
    path('weather/predict/', predict_weather_view, name='predict_weather'),
    path("centers/<int:center_id>/congestion-risk/", CenterCongestionRiskView.as_view()),
    path('stats/', AnalyticsStatsView.as_view(), name='analytics_stats'),
    path("reports/affected-population/", AffectedPopulationReportView.as_view(), name="affected_population_report"),
    # Other URLs...
]