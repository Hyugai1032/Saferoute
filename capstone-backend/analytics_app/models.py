from django.db import models

# Create your models here.

class WeatherData(models.Model):
    datetime = models.DateTimeField()
    temperature_2m = models.FloatField(null=True)
    relative_humidity_2m = models.FloatField(null=True)
    wind_speed_10m = models.FloatField(null=True)
    wind_direction_10m = models.FloatField(null=True)
    precipitation = models.FloatField(null=True)
    pressure_msl = models.FloatField(null=True)
    cloud_cover = models.FloatField(null=True)
    city_count = models.IntegerField(default=1)  # For consistency with model

    class Meta:
        ordering = ['datetime']
        unique_together = ['datetime']  # Prevent duplicates
