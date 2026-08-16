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

    SHELTER_CATEGORY_CHOICES = [
        ('INSIDE_EC', 'Inside Evacuation Center'),
        ('OUTSIDE_EC', 'Outside Evacuation Center'),
    ]

    shelter_category = models.CharField(
        max_length=20,
        choices=SHELTER_CATEGORY_CHOICES,
        default='INSIDE_EC'
    )

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

    DISASTER_CAUSE_CHOICES = [
        ("TYPHOON", "Typhoon"),
        ("FLOOD", "Flood"),
        ("LANDSLIDE", "Landslide"),
        ("EARTHQUAKE", "Earthquake"),
        ("FIRE", "Fire"),
        ("VOLCANIC_ACTIVITY", "Volcanic Activity"),
        ("OTHER", "Other"),
    ]

    disaster_cause = models.CharField(
        max_length=50,
        choices=DISASTER_CAUSE_CHOICES,
        default="OTHER"
    )

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
    
class Evacuee(models.Model):
    SEX_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    center = models.ForeignKey(
        EvacuationCenter,
        on_delete=models.CASCADE,
        related_name="evacuees"
    )

    log = models.ForeignKey(
        EvacuationLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evacuees"
    )

    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(default=0)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)

    contact_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    family_head_name = models.CharField(max_length=150, blank=True)
    is_family_head = models.BooleanField(default=False)

    reason_for_evacuation = models.CharField(
        max_length=50,
        choices=EvacuationLog.DISASTER_CAUSE_CHOICES,
        default="OTHER",
    )

    is_child = models.BooleanField(default=False)
    is_senior = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False)
    is_pregnant = models.BooleanField(default=False)
    is_lactating = models.BooleanField(default=False)

    date_registered = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
    

class DonationNeed(models.Model):
    CATEGORY_CHOICES = [
        ("FOOD", "Food"),
        ("WATER", "Water"),
        ("CLOTHING", "Clothing"),
        ("MEDICAL", "Medical"),
        ("HYGIENE", "Hygiene"),
        ("BEDDING", "Bedding"),
        ("BABY_SUPPLIES", "Baby Supplies"),
        ("OTHER", "Other"),
    ]

    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
        ("URGENT", "Urgent"),
    ]

    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("PARTIALLY_FULFILLED", "Partially Fulfilled"),
        ("FULFILLED", "Fulfilled"),
        ("CLOSED", "Closed"),
    ]

    center = models.ForeignKey(
        EvacuationCenter,
        on_delete=models.CASCADE,
        related_name="donation_needs"
    )

    item_name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    quantity_needed = models.PositiveIntegerField(default=0)
    quantity_received = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=50, default="pcs")

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="MEDIUM"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="OPEN"
    )

    remarks = models.TextField(blank=True)

    requested_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donation_needs_requested"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def remaining_quantity(self):
        remaining = int(self.quantity_needed or 0) - int(self.quantity_received or 0)
        return max(remaining, 0)

    def update_status(self):
        needed = int(self.quantity_needed or 0)
        received = int(self.quantity_received or 0)

        if received <= 0:
            self.status = "OPEN"
        elif received < needed:
            self.status = "PARTIALLY_FULFILLED"
        else:
            self.status = "FULFILLED"

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} needed at {self.center.name}"
    
class Donation(models.Model):
    STATUS_CHOICES = [
        ("PLEDGED", "Pledged"),
        ("RECEIVED", "Received"),
        ("CANCELLED", "Cancelled"),
    ]

    need = models.ForeignKey(
        DonationNeed,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations"
    )

    center = models.ForeignKey(
        EvacuationCenter,
        on_delete=models.CASCADE,
        related_name="donations"
    )

    donor_name = models.CharField(max_length=150)
    donor_contact = models.CharField(max_length=50, blank=True)
    donor_address = models.TextField(blank=True)

    item_name = models.CharField(max_length=150)
    category = models.CharField(max_length=30)
    quantity = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=50, default="pcs")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="RECEIVED"
    )

    received_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations_received"
    )

    received_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.item_name} from {self.donor_name}"
    
class DonationDistribution(models.Model):
    donation = models.ForeignKey(
        Donation,
        on_delete=models.CASCADE,
        related_name="distributions"
    )

    center = models.ForeignKey(
        EvacuationCenter,
        on_delete=models.CASCADE,
        related_name="donation_distributions"
    )

    item_name = models.CharField(max_length=150)
    quantity_distributed = models.PositiveIntegerField(default=0)
    unit = models.CharField(max_length=50, default="pcs")

    distributed_to = models.CharField(
        max_length=150,
        blank=True,
        help_text="Family head, evacuee name, group, or general distribution"
    )

    distributed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donation_distributions_made"
    )

    remarks = models.TextField(blank=True)
    distributed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity_distributed} {self.unit} {self.item_name} distributed"