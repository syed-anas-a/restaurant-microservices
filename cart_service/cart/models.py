from django.db import models

# Create your models here.
class Cart(models.Model):
    user_id = models.IntegerField(unique=True) 

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
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

