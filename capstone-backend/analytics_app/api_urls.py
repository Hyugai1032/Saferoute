from django.urls import path
from .api_views import (predict_weather_view, CenterCongestionRiskView, AnalyticsStatsView)

urlpatterns = [
    path('weather/predict/', predict_weather_view, name='predict_weather'),
    path("centers/<int:center_id>/congestion-risk/", CenterCongestionRiskView.as_view()),
    path('stats/', AnalyticsStatsView.as_view(), name='analytics_stats'),
    # Other URLs...
]