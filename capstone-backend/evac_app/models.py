from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from django.db.models import Max
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

    children_count = models.IntegerField(default=0)
    senior_count = models.IntegerField(default=0)
    pwd_count = models.IntegerField(default=0)
    pregnant_count = models.IntegerField(default=0)
    lactating_count = models.IntegerField(default=0)

    vulnerable_individuals = models.IntegerField(default=0)

    total_current = models.IntegerField(default=0)
    total_current_families = models.IntegerField(default=0)

    remarks = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-date_recorded", "-id"]
        indexes = [models.Index(fields=["center", "date_recorded"])]

    def __str__(self):
        return f"Log for {self.center.name} on {self.date_recorded}"

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.center_id is None:
            return super().save(*args, **kwargs)

        previous = (
            EvacuationLog.objects
            .select_for_update()
            .filter(center_id=self.center_id)
            .exclude(pk=self.pk)
            .order_by("-date_recorded", "-id")
            .first()
        )

        prev_ind = previous.total_current if previous else 0
        prev_fam = previous.total_current_families if previous else 0

        ind_delta = int(self.individuals_in or 0) - int(self.individuals_out or 0)
        fam_delta = int(self.families_in or 0) - int(self.families_out or 0)

        new_ind = max(0, prev_ind + ind_delta)
        new_fam = max(0, prev_fam + fam_delta)

        # ✅ compute vulnerable from breakdown
        self.vulnerable_individuals = (
            int(self.children_count or 0) +
            int(self.senior_count or 0) +
            int(self.pwd_count or 0) +
            int(self.pregnant_count or 0) +
            int(self.lactating_count or 0)
        )

        self.total_current = new_ind
        self.total_current_families = new_fam

        return super().save(*args, **kwargs)