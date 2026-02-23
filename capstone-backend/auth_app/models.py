from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.db import models
from django.utils import timezone
from django.conf import settings

class Municipality(models.Model):
    name = models.CharField(max_length=150)
    province = models.CharField(max_length=150, null=True, blank=True, default="Oriental Mindoro")
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class Barangay(models.Model):
    name = models.CharField(max_length=150)
    population = models.IntegerField(default=0)
    households = models.IntegerField(default=0)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    municipality = models.ForeignKey("Municipality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    
    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "PROVINCIAL_ADMIN")  # or any admin role

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):

    ROLE_CHOICES = [
        ('CITIZEN', 'Citizen'),
        ('PROVINCIAL_ADMIN', 'Provincial Admin'),
        ('MUNICIPAL_ADMIN', 'Municipal Admin'),
        ('RESPONSE_TEAM', 'Response Team'),
        ('EVAC_CENTER_STAFF', 'Evacuation Center Staff'),
    ]

    email = models.EmailField(max_length=191, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    contact_number = models.CharField(max_length=11, blank=True, null=True)

    municipality = models.ForeignKey(
        "Municipality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default="CITIZEN"
    )

    last_login_at = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    assigned_center = models.ForeignKey(
        "evac_app.EvacuationCenter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_staff",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)

    USERNAME_FIELD = "email"        # <— login field
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} — {self.first_name} {self.last_name}"

HAZARD_TYPE_CHOICES = [
    ('FLOOD', 'Flood'),
    ('LANDSLIDE', 'Landslide'),
    ('FIRE', 'Fire'),
    ('TREE', 'Fallen Tree'),
    ('ROAD_DAMAGE', 'Road Damage'),
    ('BUILDING_DAMAGE', 'Building Damage'),
    ('UTILITY', 'Utility Hazard'),
    ('OTHER', 'Other'),
]

SEVERITY_CHOICES = [
    ('LOW', 'Low'),
    ('MEDIUM', 'Medium'),
    ('HIGH', 'High'),
    ('CRITICAL', 'Critical'),
]

STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('DISMISSED', 'Dismissed'),
]

class HazardReport(models.Model):
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hazard_reports"
    )

    hazard_type = models.CharField(
        max_length=30,
        choices=HAZARD_TYPE_CHOICES
    )

    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    description = models.TextField()

    latitude = models.FloatField()
    longitude = models.FloatField()

    municipality = models.ForeignKey(
        Municipality,
        on_delete=models.CASCADE
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_hazard_reports"
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    # --- relationships ---
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    municipality = models.ForeignKey("Municipality", on_delete=models.CASCADE)

    # --- core hazard fields ---
    hazard_type = models.CharField(max_length=30, choices=HAZARD_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='MEDIUM')

    # --- basic info ---
    title = models.CharField(max_length=150, default="")
    description = models.TextField(null=True, blank=True)

    # --- location ---
    address = models.CharField(max_length=255, default="")
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)

    # --- contact info ---
    contact_name = models.CharField(max_length=100, default="")
    contact_phone = models.CharField(max_length=20, default="")

    # --- report workflow ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REPORTED')
    reported_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.hazard_type} - {self.title}"
    
class HazardPhoto(models.Model):
    hazard = models.ForeignKey(HazardReport, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='hazard_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for Report #{self.hazard.id}"


class AnalyticsEvent(models.Model):
    event_type = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True)
    context_json = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} on {self.created_at}"

class GisLayer(models.Model):
    name = models.CharField(max_length=100)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    geojson_data = models.JSONField()  # Assuming LONGTEXT for large data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.municipality.name})"