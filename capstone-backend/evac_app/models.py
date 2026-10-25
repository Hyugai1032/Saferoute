from django.db import models, transaction
from django.utils import timezone
from django.conf import settings
from django.db.models import Max
from django.db.models.signals import post_delete
from django.dispatch import receiver
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


class EvacuationReason(models.Model):
    """
    Admin-managed list of reasons an evacuee may have been displaced.
    Staff can only pick from this list when registering an evacuee;
    only admins (Provincial/Municipal) can add, rename, deactivate, or delete entries.
    """

    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive reasons are hidden from the staff dropdown but kept for existing records."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

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
 
    # Vulnerable people arriving in this entry
    children_count = models.IntegerField(default=0)
    senior_count = models.IntegerField(default=0)
    pwd_count = models.IntegerField(default=0)
    pregnant_count = models.IntegerField(default=0)
    lactating_count = models.IntegerField(default=0)
 
    # Vulnerable people leaving in this entry
    children_out = models.IntegerField(default=0)
    senior_out = models.IntegerField(default=0)
    pwd_out = models.IntegerField(default=0)
    pregnant_out = models.IntegerField(default=0)
    lactating_out = models.IntegerField(default=0)
 
    # Running total of vulnerable individuals currently at the center
    # (mirrors total_current: prev + in - out, clamped at 0)
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
 
    disaster_cause = models.ForeignKey(
        EvacuationReason,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="cause",
    )
 
    remarks = models.TextField(null=True, blank=True)
 
    class Meta:
        ordering = ["-date_recorded", "-id"]
        indexes = [models.Index(fields=["center", "date_recorded"])]
 
    def __str__(self):
        return f"Log for {self.center.name} on {self.date_recorded}"
 
    # Fields that hold running totals. They are always derived from the in/out counts
    # of every log for the center, replayed oldest -> newest.
    RUNNING_TOTAL_FIELDS = ["total_current", "total_current_families", "vulnerable_individuals"]

    def _deltas(self):
        ind = int(self.individuals_in or 0) - int(self.individuals_out or 0)
        fam = int(self.families_in or 0) - int(self.families_out or 0)
        vul_in = (
            int(self.children_count or 0) + int(self.senior_count or 0) + int(self.pwd_count or 0)
            + int(self.pregnant_count or 0) + int(self.lactating_count or 0)
        )
        vul_out = (
            int(self.children_out or 0) + int(self.senior_out or 0) + int(self.pwd_out or 0)
            + int(self.pregnant_out or 0) + int(self.lactating_out or 0)
        )
        return ind, fam, vul_in - vul_out

    @classmethod
    def recalculate_center(cls, center_id):
        """
        Rebuild the running totals of every log of one center, oldest -> newest.
        Call after any create, edit or delete, because changing one log changes the
        totals of every log after it. Uses bulk_update, so it doesn't re-trigger save()
        or write extra audit entries.
        """
        if center_id is None:
            return 0
        logs = list(
            cls.objects
            .filter(center_id=center_id)
            .order_by("date_recorded", "id")
            .only(
                "id", "date_recorded",
                "individuals_in", "individuals_out", "families_in", "families_out",
                "children_count", "senior_count", "pwd_count", "pregnant_count", "lactating_count",
                "children_out", "senior_out", "pwd_out", "pregnant_out", "lactating_out",
                *cls.RUNNING_TOTAL_FIELDS,
            )
        )
        ind = fam = vul = 0
        changed = []
        for log in logs:
            d_ind, d_fam, d_vul = log._deltas()
            ind = max(0, ind + d_ind)
            fam = max(0, fam + d_fam)
            vul = max(0, vul + d_vul)
            if (log.total_current, log.total_current_families, log.vulnerable_individuals) != (ind, fam, vul):
                log.total_current, log.total_current_families, log.vulnerable_individuals = ind, fam, vul
                changed.append(log)
        if changed:
            cls.objects.bulk_update(changed, cls.RUNNING_TOTAL_FIELDS, batch_size=500)
        return len(changed)

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.center_id is None:
            return super().save(*args, **kwargs)

        # Serialize writes per center so two staff saving at once can't interleave.
        EvacuationCenter.objects.select_for_update().filter(pk=self.center_id).first()

        old_center_id = None
        if self.pk:
            old_center_id = (
                EvacuationLog.objects.filter(pk=self.pk).values_list("center_id", flat=True).first()
            )

        # Totals for THIS log come from the log just before it in time (not the newest
        # log), so edits to older logs and back-dated entries are computed correctly.
        previous_qs = EvacuationLog.objects.filter(center_id=self.center_id).exclude(pk=self.pk)
        if self.pk:
            previous_qs = previous_qs.filter(
                models.Q(date_recorded__lt=self.date_recorded)
                | models.Q(date_recorded=self.date_recorded, id__lt=self.pk)
            )
        else:
            previous_qs = previous_qs.filter(date_recorded__lte=self.date_recorded)
        previous = previous_qs.order_by("-date_recorded", "-id").first()

        d_ind, d_fam, d_vul = self._deltas()
        self.total_current = max(0, (previous.total_current if previous else 0) + d_ind)
        self.total_current_families = max(0, (previous.total_current_families if previous else 0) + d_fam)
        self.vulnerable_individuals = max(0, (previous.vulnerable_individuals if previous else 0) + d_vul)

        result = super().save(*args, **kwargs)

        # Logs AFTER this one depend on it: rebuild the whole chain.
        EvacuationLog.recalculate_center(self.center_id)
        if old_center_id and old_center_id != self.center_id:
            EvacuationLog.recalculate_center(old_center_id)
        self.refresh_from_db(fields=self.RUNNING_TOTAL_FIELDS)
        return result


@receiver(post_delete, sender=EvacuationLog)
def _recalculate_after_log_delete(sender, instance, **kwargs):
    """Deleting a log changes the totals of every later log of that center."""
    center_id = instance.center_id
    if not center_id:
        return
    # Skip when the whole center is being deleted (cascade); its logs are going too.
    transaction.on_commit(
        lambda: EvacuationCenter.objects.filter(pk=center_id).exists()
        and EvacuationLog.recalculate_center(center_id)
    )


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

    reason_for_evacuation = models.ForeignKey(
        EvacuationReason,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="evacuees",
    )

    is_child = models.BooleanField(default=False)
    is_senior = models.BooleanField(default=False)
    is_pwd = models.BooleanField(default=False)
    is_pregnant = models.BooleanField(default=False)
    is_lactating = models.BooleanField(default=False)

    date_registered = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    remarks = models.TextField(blank=True)

        # --- Offline-entry support ---
    # A UUID generated on the staff member's phone when the record is first typed in.
    # Re-sending the same record (a retry after a dropped connection) finds this id and
    # returns the existing row instead of creating a duplicate.
    client_id = models.UUIDField(null=True, blank=True, unique=True)
    # When the record was entered on the device (may be hours before it reached the server).
    recorded_at = models.DateTimeField(null=True, blank=True)
    registered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evacuees_registered",
    )

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