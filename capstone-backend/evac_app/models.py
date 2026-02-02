from django.db import models
from django.utils import timezone
from django.conf import settings
from auth_app.models import Municipality, CustomUser, Barangay

# Create your models here.

class EvacuationCenter(models.Model):
    STATUS_CHOICES = [
        ('PERMANENT', 'Permanent'),
        ('TEMPORARY', 'Temporary'),
    ]

    SUSCEPTIBILITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    province = models.CharField(max_length=100, default='Oriental Mindoro')
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    barangay = models.ForeignKey(Barangay, on_delete=models.SET_NULL, null=True, blank=True)
    fund_source = models.CharField(max_length=255, null=True, blank=True)
    family_capacity_max = models.IntegerField(default=0)
    individual_capacity_max = models.IntegerField(default=0)
    used_for_covid = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    flood_susceptibility = models.CharField(max_length=10, choices=SUSCEPTIBILITY_CHOICES, default='LOW')
    landslide_susceptibility = models.CharField(max_length=10, choices=SUSCEPTIBILITY_CHOICES, default='LOW')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TEMPORARY')
    remarks = models.TextField(null=True, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EvacuationLog(models.Model):
    center = models.ForeignKey(EvacuationCenter, on_delete=models.CASCADE)
    reporting_staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    date_recorded = models.DateTimeField(default=timezone.now)
    families_in = models.IntegerField(default=0)
    individuals_in = models.IntegerField(default=0)
    families_out = models.IntegerField(default=0)
    individuals_out = models.IntegerField(default=0)
    vulnerable_individuals = models.IntegerField(default=0)
    total_current = models.IntegerField(default=0)  # Computed field
    remarks = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Compute total_current if needed (logic depends on your requirements, e.g., aggregate from previous logs, e.g., previous_log.total_current + in - out)
        # For simplicity, assuming it's updated externally or via signal; implement as needed
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Log for {self.center.name} on {self.date_recorded}"
