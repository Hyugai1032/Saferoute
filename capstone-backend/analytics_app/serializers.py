from rest_framework import serializers

class PredictionSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    TAVG = serializers.FloatField()
    WDSP = serializers.FloatField()
    wind_u = serializers.FloatField()
    wind_v = serializers.FloatField()
    PRCP = serializers.FloatField()
    RH = serializers.FloatField()
    pressure = serializers.FloatField()
    cloud_cover = serializers.FloatField()
    dew_point = serializers.FloatField()