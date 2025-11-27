from django.urls import path
from .api_views import predict_weather_view

urlpatterns = [
    path('weather/predict/', predict_weather_view, name='predict_weather'),
    # Other URLs...
]