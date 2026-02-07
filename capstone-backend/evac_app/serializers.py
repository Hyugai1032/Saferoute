# capstone-backend/evac_app/serializers.py
from rest_framework import serializers
from .models import EvacuationCenter

class EvacuationCenterSerializer(serializers.ModelSerializer):
    municipality_name = serializers.CharField(
        source="municipality.name",
        read_only=True
    )
    barangay_name = serializers.CharField(
        source="barangay.name",
        read_only=True
    )

    class Meta:
        model = EvacuationCenter
        fields = [
            'id',
            'province',
            'municipality',
            "municipality_name",
            'name',
            'barangay',
            "barangay_name",
            'fund_source',
            'family_capacity_max',
            'individual_capacity_max',
            'used_for_covid',
            'latitude',
            'longitude',
            'flood_susceptibility',
            'landslide_susceptibility',
            'status',
            'remarks',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
