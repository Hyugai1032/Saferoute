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

    current_total = serializers.SerializerMethodField()
    current_families = serializers.SerializerMethodField()
    congestion_percent = serializers.SerializerMethodField()

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
            'shelter_category',
            'remarks',
            'created_at',
            'updated_at',
            'current_total',
            'current_families',
            'congestion_percent',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def _latest_log(self, center):
        return (
            EvacuationLog.objects
            .filter(center_id=center.id)
            .order_by('-date_recorded', '-id')
            .first()
        )

    def get_current_total(self, center):
        log = self._latest_log(center)
        return int(log.total_current) if log else 0

    def get_current_families(self, center):
        log = self._latest_log(center)
        return int(log.total_current_families) if log else 0

    def get_congestion_percent(self, center):
        cap = int(center.family_capacity_max or 0) + int(center.individual_capacity_max or 0)
        if cap <= 0:
            return 0.0

        occ = self.get_current_total(center)
        return round((occ / cap) * 100, 1)

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
            
            # ✅ new breakdown
            "children_count",
            "senior_count",
            "pwd_count",
            "pregnant_count",
            "lactating_count",

            "vulnerable_individuals",
            "total_current",
            "total_current_families",  # ✅ new
            "remarks",
        ]
        read_only_fields = ["reporting_staff"]

    def validate(self, attrs):
        numeric_fields = [
        "families_in","individuals_in","families_out","individuals_out",
        "children_count","senior_count","pwd_count","pregnant_count","lactating_count"
        ]
        read_only_fields = ["reporting_staff", "total_current", "vulnerable_individuals"]
        for f in numeric_fields:
            if attrs.get(f, 0) is None:
                attrs[f] = 0
            if attrs.get(f, 0) < 0:
                raise serializers.ValidationError({f: "Must be 0 or greater."})

        return attrs
    
class EvacuationCenterListSerializer(serializers.ModelSerializer):
    municipality_name = serializers.CharField(source="municipality.name", read_only=True)

    class Meta:
        model = EvacuationCenter
        fields = ["id", "name", "municipality", "municipality_name", "shelter_category"]

class EvacCenterDropdownSerializer(serializers.ModelSerializer):
    municipality_name = serializers.CharField(source="municipality.name", read_only=True)

    class Meta:
        model = EvacuationCenter
        fields = ["id", "name", "municipality", "municipality_name"]
