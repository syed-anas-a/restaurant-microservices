import logging
import json

from django.core.management import BaseCommand
from confluent_kafka import Consumer
from django.conf import settings
from django.db import close_old_connections

from order.models import Order

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Consume delivery.status_changed events and sync order state"

    def handle(self, *args, **options):
        consumer = Consumer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "order-service",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        consumer.subscribe(["delivery.status_changed"])

        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error("Kafka error, %s", msg.error())
                    continue

                close_old_connections()
                try:
                    event = json.loads(msg.value())
                    self._handle(event)
                except KeyError, ValueError:
                    logger.exception("Permanent failure, skipping: %s", msg.value())

                consumer.commit(message=msg, asynchronous=False)
        finally:
            consumer.close()

    def _handle(event):
        data = event["data"]
        order_id = data["order_id"]
        new_status = data["status"]

        if new_status == "ASSIGNED":
            updated = Order.objects.filter(
                id=order_id
            ).exclude(status__in=[Order.Status.CANCELLED, Order.Status.FAILED]
            ).update(delivery_crew_id=data["crew_id"])

        elif new_status == "OUT FOR DELIVERY":
                    updated = Order.objects.filter(
                        id=order_id, status__in=[Order.Status.PLACED, Order.Status.PREPARING]
                    ).update(status=Order.Status.OUT_FOR_DELIVERY)

        elif new_status == "DELIVERED":
                    updated = Order.objects.filter(
                        id=order_id, status=Order.Status.OUT_FOR_DELIVERY
                    ).update(status=Order.Status.DELIVERED)

        else:
            updated = 0

        if not updated:
            logger.info("Duplicate or invalid transition for order id=%s, status=%s", order_id, new_status)


