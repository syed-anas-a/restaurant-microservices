import requests
from .models import Cart, CartItem
from .exceptions import MenuItemNotFound, MenuServiceUnavailable, CartItemNotFound
from django.conf import settings
from django.db import transaction
from django.db.models import F

class CartService:

    @staticmethod
    def fetch_menu_item(menu_item_id):
        try:
            response = requests.get(
                f"{settings.MENU_SERVICE_URL}/menu/items/{menu_item_id}/",
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

        with transaction.atomic():
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
                cart_item.price = menu_item["price"]
                cart_item.quantity = F("quantity") + quantity
                cart_item.save(update_fields=["price", "quantity"])
                cart_item.refresh_from_db(fields=["quantity"])

        return cart_item

    @staticmethod
    def update_item(user_id, menu_item_id, quantity):
        try:
            cart_item = CartItem.objects.get(
                cart__user_id=user_id,
                menu_item_id=menu_item_id,
            )
        except CartItem.DoesNotExist:
            raise CartItemNotFound("Cart item not found")

        cart_item.quantity = quantity
        cart_item.save(update_fields=["quantity"])

        return cart_item

    @staticmethod
    def delete_item(user_id, menu_item_id):
        try:
            cart_item = CartItem.objects.get(
                user_id=user_id,
                menu_item_id=menu_item_id
            )
        except CartItem.DoesNotExist:
            raise CartItemNotFound("Cart item not found")

        cart_item.delete()

    @staticmethod
    def clear_cart(user_id):
        CartItem.objects.filter(
            cart__user_id=user_id
        ).delete()
        




