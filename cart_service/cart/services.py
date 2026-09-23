import requests
from .models import Cart, CartItem
from .exceptions import MenuItemNotFound, MenuServiceUnavailable
from django.conf import settings

class CartService:

    @staticmethod
    def fetch_menu_item(menu_item_id):
        try:
            response = requests.get(
                f"{settings.MENU_SERVICE_URL}/menu/{menu_item_id}/",
                timeout=3
            )
        except requests.exceptions.RequestException:
            raise MenuServiceUnavailable("Menu service unavailable")

        if response.status_code == 404:
            raise MenuItemNotFound("Menu item not found")
        if response.status_code != 200:
            raise MenuServiceUnavailable("Menu service error")

        return response.json()


    @staticmethod
    def add_item(user_id, menu_item_id, quantity):

        menu_item = CartService.fetch_menu_item(menu_item_id)

        cart, _ = Cart.objects.get_or_create(user_id=user_id)
        cart_item, created = CartItem.objects.get_or_create(
            menu_item_id=menu_item_id,
            cart=cart,
            defaults={
                "price":menu_item["price"], 
                "quantity":quantity
            }
        )
        if not created:
            cart_item.price = menu_item.price
            cart_item.quantity += quantity

        cart_item.save()

        return cart_item



