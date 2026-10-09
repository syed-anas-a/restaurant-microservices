import logging
import json

from confluent_kafka import Consumer
from django.core.management import BaseCommand
from django.conf import settings
from django.db import close_old_connections

from delivery.models import Delivery


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Consume order.placed events and create UNASSIGNED delivery records"

    def handle(self, *args, **options):
        consumer = Consumer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "group.id": "delivery-service",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        })
        consumer.subscribe(["order.placed"])
        try:
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error("Kafka error %s", msg.error())
                    continue

                close_old_connections()
                try:
                    event = json.loads(msg.value())
                    print(event)
                    self._handle(event)
                except ValueError, KeyError:
                    logger.exception("Permanent failure, skipping: %s", msg.value())
                consumer.commit(message=msg, asynchronous=False)
        finally:
            consumer.close()

    def _handle(self, event):
        data = event["data"]
        Delivery.objects.get_or_create(
            order_id=data["order_id"],
            defaults={"customer_id":data["customer_id"]},
        )
