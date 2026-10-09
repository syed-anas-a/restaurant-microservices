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
from django.utils import timezone
from .events import build_event, publish_event
from django.db import transaction

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
    def publish_delivery_status_changed(delivery):
        event = build_event(
            event_type="delivery.status_changed",
            data={
                "order_id": delivery.order_id,
                "delivery_id": delivery.id,
                "crew_id": delivery.crew_id,
                "status": delivery.status,
            },
        )
        publish_event(topic="delivery.status_changed", event=event, key=delivery.order_id)

    @staticmethod
    def assign_delivery(delivery_id, new_crew_id, auth_header):
        delivery = get_object_or_404(Delivery, id=delivery_id)

        if delivery.status not in [Delivery.Status.ASSIGNED, Delivery.Status.UNASSIGNED]:
            raise DeliveryInProgress("Can't reassign once delivery in progress or delivered")

        user = DeliveryService.fetch_user(user_id=new_crew_id, auth_header=auth_header)

        if user["group"] != "DELIVERY CREW":
            raise UserNotDeliveryCrew("User is not a delivery crew")

        if Delivery.objects.filter(crew_id=new_crew_id).exclude(status=Delivery.Status.DELIVERED).exclude(id=delivery_id).exists():
            raise DeliveryInProgress("crew member already has an active delivery")

        delivery.crew_id = new_crew_id
        delivery.status = Delivery.Status.ASSIGNED
        delivery.assigned_at = timezone.now()

        with transaction.atomic():
            delivery.save(update_fields=["crew_id", "status", "assigned_at"])
            transaction.on_commit(
                lambda:DeliveryService.publish_delivery_status_changed(delivery),
                robust=True
            )
        return delivery
        

        

