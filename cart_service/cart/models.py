from django.db import models

# Create your models here.
class Cart(models.Model):
    user_id = models.IntegerField()
    cart_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.0) 

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu_item_id = models.IntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'menu_item_id'],
                name='unique_cart_menu_item_id'
            )
        ]

