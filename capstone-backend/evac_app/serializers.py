# capstone-backend/evac_app/serializers.py
from rest_framework import serializers
from .models import EvacuationCenter

class EvacuationCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvacuationCenter
        fields = [
            'id',
            'province',
            'municipality',
            'name',
            'barangay',
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
