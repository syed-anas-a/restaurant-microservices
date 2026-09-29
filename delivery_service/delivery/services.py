from .models import Delivery
import requests
from django.conf import settings
from .exceptions import (
    UserNotFound, UserServiceUnavailable,
    OrderNotFound, OrderServiceUnavailable,
    UserNotDeliveryCrew, OrderNotPlaced,
    DeliveryInProgress
)
from django.shortcuts import get_object_or_404

class DeliveryService:

    @staticmethod
    def fetch_user(user_id, auth_header):
        try:
            response = requests.get(
                f"{settings.AUTH_SERVICE_URL}/auth/users/{user_id}/",
                headers={
                    "Authorization":auth_header
                },
                timeout=3
            )
        except requests.exceptions.RequestException:
            raise UserServiceUnavailable("User service unavailable")

        if response.status_code == 404:
            raise UserNotFound("User not found")

        if response.status_code != 200:
            raise UserServiceUnavailable("User service error")

        return response.json()

    @staticmethod
    def fetch_order(order_id, auth_header):
        try:
            response = requests.get(
                f"{settings.ORDER_SERVICE_URL}/orders/{order_id}/",
                headers={
                    "Authorization":auth_header
                },
                timeout=3
            )
        except requests.exceptions.RequestException:
            raise OrderServiceUnavailable("Order service unavailable")

        if response.status_code == 404:
            raise OrderNotFound("Order not found")

        if response.status_code != 200:
            raise OrderServiceUnavailable("Order service error")

        return response.json()

    @staticmethod
    def assign_delivery(data, auth_header):
        order_id = data.get("order_id")
        crew_id = data.get("crew_id")

        user = DeliveryService.fetch_user(crew_id=crew_id, auth_header=auth_header)
        if user["group"] != "DELIVERY CREW":
            raise UserNotDeliveryCrew("User is not a delivery crew")

        order = DeliveryService.fetch_order(order_id=order_id, auth_header=auth_header)
        if order.status != "PLACED":
            raise OrderNotPlaced("Order not placed")
        
        delivery = Delivery.objects.create(
            crew_id=crew_id,
            order_id=order_id,
            customer_id=order["user_id"],
        )

        return delivery

    @staticmethod
    def reassign_delivery(delivery_id, new_crew_id, auth_header):
        delivery = get_object_or_404(Delivery, id=delivery_id)

        if delivery.status != Delivery.Status.ASSIGNED:
            raise DeliveryInProgress("Can't reassign once delivery in progress")

        user = DeliveryService.fetch_user(user_id=new_crew_id, auth_header=auth_header)

        if user["group"] != "DELIVERY CREW":
            raise UserNotDeliveryCrew("User is not a delivery crew")

        if Delivery.objects.filter(crew_id=new_crew_id).exclude(status=Delivery.Status.DELIVERED).exists():
            raise DeliveryInProgress("crew member already has an active delivery")

        delivery.crew_id = new_crew_id
        delivery.save(update_fields=["crew_id"])

        return delivery
        

        

