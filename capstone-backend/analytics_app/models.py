from django.db import models

from evac_app.models import EvacuationCenter


class CongestionSnapshot(models.Model):
    """
    One saved prediction per center per run of `snapshot_congestion`.
    `actual_total_at_horizon` is filled in later, once the horizon has passed.
    Over time this table becomes the historical dataset for evaluation / training.
    """
    center = models.ForeignKey(
        EvacuationCenter,
        on_delete=models.CASCADE,
        related_name="congestion_snapshots",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    horizon_minutes = models.PositiveIntegerField()

    model = models.CharField(max_length=10)                 # prior / hybrid / observed
    model_version = models.CharField(max_length=20)

    capacity = models.IntegerField()
    current_total = models.IntegerField()
    predicted_total = models.IntegerField()
    risk_score = models.FloatField()
    risk_level = models.CharField(max_length=10)

    actual_total_at_horizon = models.IntegerField(null=True, blank=True)
    features = models.JSONField(default=dict, blank=True)   # inputs, for later training

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["center", "created_at"])]

    def __str__(self):
        return f"{self.center_id} @ {self.created_at:%Y-%m-%d %H:%M} -> {self.predicted_total}"