import requests
from .models import Cart, CartItem
from .exceptions import MenuItemNotFound

class CartService:

    @staticmethod
    def add_item(user_id, menu_item_id, quantity):
        response = requests.get(
            f"http://127.0.0.1:8002/menu/items/{menu_item_id}/"
            , timeout=3
        )
        if response.status_code != 200:
            raise MenuItemNotFound("Menu item not found")
        menu_item = response.json()
        cart = Cart.objects.get(user_id=user_id)
        cart_item, created = CartItem.objects.get_or_create(
            menu_item_id=menu_item_id,
            cart=cart
        )
        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.save()

        return cart_item