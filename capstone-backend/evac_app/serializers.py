# capstone-backend/evac_app/serializers.py
from rest_framework import serializers
from .models import EvacuationCenter, EvacuationLog

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

class EvacuationLogSerializer(serializers.ModelSerializer):
    center_name = serializers.CharField(source="center.name", read_only=True)
    reporting_staff_name = serializers.CharField(source="reporting_staff.email", read_only=True)

    class Meta:
        model = EvacuationLog
        fields = [
            "id",
            "center", "center_name",
            "reporting_staff", "reporting_staff_name",
            "date_recorded",
            "families_in", "individuals_in",
            "families_out", "individuals_out",
            "vulnerable_individuals",
            "total_current",
            "remarks",
        ]
        read_only_fields = ["reporting_staff", "total_current"]

    def validate(self, attrs):
        numeric_fields = [
            "families_in", "individuals_in",
            "families_out", "individuals_out",
            "vulnerable_individuals",
        ]
        for f in numeric_fields:
            if attrs.get(f, 0) is None:
                attrs[f] = 0
            if attrs.get(f, 0) < 0:
                raise serializers.ValidationError({f: "Must be 0 or greater."})

        return attrs
