from django.db import models

# Create your models here.
class Delivery(models.Model):
    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", "Assigned"
        OUT_FOR_DELIVERY = "OUT FOR DELIVERY", "Out for delivery"
        DELIVERED = "DELIVERED", "Delivered"

    crew_id = models.IntegerField()
    order_id = models.IntegerField(unique=True)
    customer_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ASSIGNED)
    assigned_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
