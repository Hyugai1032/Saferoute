from rest_framework import serializers
from .models import CustomUser, HazardReport, HazardPhoto
from django.conf import settings

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'password', 'role', 'contact_number', 'municipality']

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
        read_only_fields = ['photos', 'status', 'reported_at']

    def create(self, validated_data):
        photo_files = validated_data.pop('uploaded_photos', [])
        report = HazardReport.objects.create(**validated_data)

        for img in photo_files:
            HazardPhoto.objects.create(hazard=report, image=img)

        return report
