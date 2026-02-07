from rest_framework import serializers
from .models import CustomUser, HazardReport, HazardPhoto, Municipality, Barangay
from django.conf import settings
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password', 'contact_number', 'municipality']

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser.objects.create_user(**validated_data, password=password)
        return user

    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role', 'contact_number']  # Add fields as needed


class HazardPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HazardPhoto
        fields = ['id', 'image']


class HazardReportSerializer(serializers.ModelSerializer):
    photos = HazardPhotoSerializer(many=True, read_only=True)
    uploaded_photos = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = HazardReport
        fields = [
            'id', 'user', 'municipality', 'hazard_type', 'title', 'description',
            'address', 'latitude', 'longitude', 'severity',
            'photos', 'uploaded_photos',
            'contact_name', 'contact_phone',
            'status', 'reported_at'
        ]
        read_only_fields = ['user', 'photos', 'status', 'reported_at']

    def create(self, validated_data):
        photo_files = validated_data.pop('uploaded_photos', [])

        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data['user'] = request.user

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
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role',
                  'contact_number', 'municipality', 'municipality_name', 
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

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'first_name', 'last_name', 'role',
                  'contact_number', 'municipality', 'is_active']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance
    
class UserDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views"""
    municipality_details = MunicipalitySerializer(source='municipality', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'role',
                  'contact_number', 'municipality', 'municipality_details',
                  'is_active', 'is_staff', 'last_login_at', 'created_at', 'updated_at']
        read_only_fields = ['id', 'last_login_at', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
class MeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'contact_number']  # ✅ only safe fields

    
