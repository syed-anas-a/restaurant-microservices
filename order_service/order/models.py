from django.db import models

# Create your models here.
class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PLACED = "PLACED", "Placed"
        PREPARING = "PREPARING", "Preparing"
        OUT_FOR_DELIVERY = "OUT FOR DELIVERY", "Out for Delivery"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"

    user_id = models.IntegerField()
    order_value = models.DecimalField(max_digits=8, decimal_places=2)
    delivery_crew_id = models.IntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PLACED)
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item_id = models.IntegerField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
