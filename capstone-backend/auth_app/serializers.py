from rest_framework import serializers
from .models import CustomUser, HazardReport, HazardPhoto, Municipality, Barangay, GisLayer
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.apps import apps
EvacuationCenter = apps.get_model("evac_app", "EvacuationCenter")

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password', 'contact_number', 'municipality']

    def create(self, validated_data):
        password = validated_data.pop("password")
         # If your workflow is "wait for admin approval"
        validated_data.setdefault("status", "PENDING")

        user = CustomUser.objects.create_user(**validated_data)
        return user

    
class UserProfileSerializer(serializers.ModelSerializer):
    assigned_center_id = serializers.IntegerField(
        source="assigned_center.id",
        read_only=True
    )
    assigned_center_name = serializers.CharField(
        source="assigned_center.name",
        read_only=True
    )

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
            "contact_number",
            "assigned_center_id",
            "assigned_center_name",
        ]



class HazardPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HazardPhoto
        fields = ['id', 'image']


# auth_app/serializers.py
from rest_framework import serializers
from .models import HazardReport, HazardPhoto

class HazardReportSerializer(serializers.ModelSerializer):
    photos = HazardPhotoSerializer(many=True, read_only=True)
    uploaded_photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    reporter_email = serializers.CharField(source="reporter.email", read_only=True)
    municipality_name = serializers.CharField(source="municipality.name", read_only=True)

    class Meta:
        model = HazardReport
        fields = [
            "id",
            "reporter", "reporter_email",
            "municipality", "municipality_name",
            "hazard_type",
            "description",
            "latitude", "longitude",
            "address",
            "severity",
            "title",
            "contact_name", "contact_phone",
            "status",
            "reviewed_by", "reviewed_at",
            "validated_at", "dismissed_at",
            "created_at",
            "photos", "uploaded_photos",
        ]
        read_only_fields = [
            "id",
            "reporter",
            "municipality",
            "status",
            "reviewed_by", "reviewed_at",
            "validated_at", "dismissed_at",
            "created_at",
            "photos",
            "reporter_email",
            "municipality_name",
        ]

    def create(self, validated_data):
        photo_files = validated_data.pop("uploaded_photos", [])
        report = HazardReport.objects.create(**validated_data)

        for img in photo_files:
            HazardPhoto.objects.create(hazard=report, image=img)

        return report
    
class MunicipalitySerializer(serializers.ModelSerializer):
    """
    Serializer for Municipality model
    Returns municipality data for dropdowns and displays
    """
    class Meta:
        model = Municipality
        fields = ['id', 'name', 'province']
        read_only_fields = ['id']

class MunicipalityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = ["id", "name"]

class BarangaySerializer(serializers.ModelSerializer):
    """
    Serializer for Barangay model
    Returns barangay data with municipality reference
    """
    municipality_name = serializers.CharField(source='municipality.name', read_only=True)
    
    class Meta:
        model = Barangay
        fields = ['id', 'name', 'municipality', 'municipality_name']
        read_only_fields = ['id', 'municipality_name']

class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    municipality_name = serializers.CharField(source='municipality.name', read_only=True)
    assigned_center_name = serializers.CharField(source="assigned_center.name", read_only=True)
    assigned_center = serializers.IntegerField(source="assigned_center.id", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role',
                  'contact_number', 'municipality', 'municipality_name', 
                  'assigned_center', 'assigned_center_name',
                  'is_active', 'created_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users with password"""
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'password_confirm', 'first_name', 
                  'last_name', 'role', 'contact_number', 'municipality', 'is_active']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users (password optional)"""
    password = serializers.CharField(
        write_only=True, 
        required=False, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    assigned_center = serializers.PrimaryKeyRelatedField(
        queryset=EvacuationCenter.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'role',
                  'contact_number', 'municipality', 'is_active', "assigned_center"]
        
    def validate(self, attrs):
        """
        Optional: enforce rules:
        - Only allow assigned_center when role is EVAC_CENTER_STAFF
        - Staff must be in same municipality as the center (if your EvacuationCenter has municipality FK)
        """
        role = attrs.get("role", getattr(self.instance, "role", None))
        assigned_center = attrs.get("assigned_center", getattr(self.instance, "assigned_center", None))
        municipality = attrs.get("municipality", getattr(self.instance, "municipality", None))

        if role != "EVAC_CENTER_STAFF":
            # if changing role away from staff, auto-clear assigned center
            if "assigned_center" in attrs:
                # allow clearing explicitly
                pass
            else:
                # no assigned_center supplied; keep as-is or clear depending on your policy
                # I recommend clearing when not staff:
                attrs["assigned_center"] = None
        else:
            # role is staff, center can be set
            if assigned_center and municipality and hasattr(assigned_center, "municipality_id"):
                if assigned_center.municipality_id != municipality.id:
                    raise serializers.ValidationError({
                        "assigned_center": "Assigned center must be within the user's municipality."
                    })
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
    
class UserDetailSerializer(serializers.ModelSerializer):
    municipality_details = MunicipalitySerializer(source='municipality', read_only=True)
    assigned_center = serializers.PrimaryKeyRelatedField(
        queryset=EvacuationCenter.objects.all(),  
        required=False,
        allow_null=True
    )
    assigned_center_name = serializers.CharField(source="assigned_center.name", read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name', 'role',
            'contact_number', 'municipality', 'municipality_details',
            'assigned_center', 'assigned_center_name',  
            'is_active', 'is_staff', 'last_login_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_login_at', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
class MeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'contact_number']  # ✅ only safe fields


class GisLayerSerializer(serializers.ModelSerializer):
    municipality_name = serializers.CharField(source="municipality.name", read_only=True)

    class Meta:
        model = GisLayer
        fields = [
            "id",
            "name",
            "municipality",
            "municipality_name",
            "geojson_data",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "municipality_name"]

    def validate_geojson_data(self, value):
        """
        Minimal GeoJSON validation (good enough for Leaflet rendering).
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError("geojson_data must be a JSON object.")

        geo_type = value.get("type")
        if not geo_type:
            raise serializers.ValidationError("GeoJSON must have a root 'type' field.")

        allowed = {
            "FeatureCollection",
            "Feature",
            "Polygon",
            "MultiPolygon",
            "LineString",
            "MultiLineString",
            "Point",
            "MultiPoint",
            "GeometryCollection",
        }
        if geo_type not in allowed:
            raise serializers.ValidationError(f"Invalid GeoJSON type '{geo_type}'.")

        if geo_type == "FeatureCollection":
            feats = value.get("features")
            if not isinstance(feats, list):
                raise serializers.ValidationError("FeatureCollection must include 'features' as a list.")

        return value