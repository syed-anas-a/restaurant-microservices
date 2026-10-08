from .models import Order, OrderItem
from .exceptions import (
    CartEmpty, CartServiceUnavailable, MenuServiceUnavailable, 
    MenuItemNotFound, CartClearFailed, CartRestoreFailed
)
from django.conf import settings
import requests
from decimal import Decimal
from django.db import transaction
import logging
from .tasks import send_order_confirmation_email
from kombu.exceptions import OperationalError
from .events import build_event, publish_event

logger = logging.getLogger(__name__)

class OrderService:

    @staticmethod
    def get_all_orders(user_id):

        return Order.objects.prefetch_related("items").filter(user_id=user_id)

    @staticmethod
    def fetch_cart(auth_header):
        try:
            response = requests.get(
                f"{settings.CART_SERVICE_URL}/cart/",
                headers={"Authorization":auth_header},
                timeout=3
            )
        except requests.exceptions.RequestException:
            raise CartServiceUnavailable("Cart service unavailable")

        if response.status_code != 200:
            raise CartServiceUnavailable("Cart service error")

        cart = response.json()

        if not cart["items"]:
            raise CartEmpty("Cart is empty")

        return [ 
            {
                "menu_item_id": item["menu_item_id"],
                "quantity": item["quantity"]
            }
            for item in cart["items"]
        ]

    @staticmethod
    def fetch_menu_price(menu_item_id):
        try:
            response = requests.get(
                f"{settings.MENU_SERVICE_URL}/menu/items/{menu_item_id}/"
                , timeout=3
            )
        except requests.exceptions.RequestException:
            raise MenuServiceUnavailable("Menu service is unavailable")

        if response.status_code == 404:
            raise MenuItemNotFound("Menu item no longer exists")
        if response.status_code != 200:
            raise MenuServiceUnavailable("Menu service error")

        return Decimal(response.json()["price"])

    @staticmethod
    def clear_cart(auth_header):
        try: 
            response = requests.delete(
                f"{settings.CART_SERVICE_URL}/cart/"
                , headers={"Authorization": auth_header}
                , timeout=3
            )
        except requests.exceptions.RequestException:
            return False

        return response.status_code == 204

    @staticmethod
    def restore_cart(auth_header, cart_snapshot):
        try:
            response = requests.put(
                f"{settings.CART_SERVICE_URL}/cart/",
                json={"items":cart_snapshot},
                headers={
                    "Authorization":auth_header,
                    "X-Internal-Token": settings.INTERNAL_SERVICE_TOKEN,
                },
                timeout=3
            )
        except requests.exceptions.RequestException:
            return False
        return response.status_code == 204

    @staticmethod
    def queue_order_confirmation_email(order_id, email):
        try:
            send_order_confirmation_email.delay(order_id, email)
        except OperationalError:
            logger.exception("Could not queue confirmation mail")

    @staticmethod
    def publish_order_placed(order):
        event = build_event(
            event_type="order.placed",
            data={
                "order_id":order.id,
                "customer_id":order.user_id
            }
        )
        publish_event(topic="order.placed", key=order.id, event=event)

    @staticmethod
    def place_order(user_id, email, auth_header):
        cart_items = OrderService.fetch_cart(auth_header=auth_header)
        for item in cart_items:
            item["price"] = OrderService.fetch_menu_price(menu_item_id=item["menu_item_id"])

        order_value = sum(
            (item["price"]*item["quantity"]
            for item in cart_items),
            Decimal("0.00")
        )

        with transaction.atomic():
            order = Order.objects.create(
                user_id=user_id,
                order_value=order_value
            )

            OrderItem.objects.bulk_create([
                OrderItem(order=order, **item) for item in cart_items
            ])

        if not OrderService.clear_cart(auth_header=auth_header):
            restored = OrderService.restore_cart(auth_header=auth_header, cart_snapshot=cart_items)
            order.status = Order.Status.FAILED
            order.save(update_fields=["status"])

            if not restored:
                raise CartRestoreFailed("Cart cannot be restored")

            raise CartClearFailed("Order failed")

        with transaction.atomic():

            order.status = Order.Status.PLACED
            order.save(update_fields=["status"])

            transaction.on_commit(
                lambda:OrderService.publish_order_placed(order),
                robust=True
            )

            if email:
                transaction.on_commit(
                    lambda:OrderService.queue_order_confirmation_email(order_id=order.id, email=email), 
                    robust=True,
                )

        return order


