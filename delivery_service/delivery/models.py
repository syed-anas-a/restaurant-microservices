from django.db import models

# Create your models here.
class Delivery(models.Model):
    class Status(models.TextChoices):
        UNASSIGNED = "UNASSIGNED", "Unassigned"
        ASSIGNED = "ASSIGNED", "Assigned"
        OUT_FOR_DELIVERY = "OUT FOR DELIVERY", "Out for delivery"
        DELIVERED = "DELIVERED", "Delivered"

    crew_id = models.IntegerField(null=True, blank=True)
    order_id = models.IntegerField(unique=True)
    customer_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.UNASSIGNED)
    assigned_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    ALLOWED_TRANSITIONS = {
        Status.UNASSIGNED: {Status.ASSIGNED},
        Status.ASSIGNED: {Status.OUT_FOR_DELIVERY},
        Status.OUT_FOR_DELIVERY: {Status.DELIVERED},
        Status.DELIVERED: set(),
    }
