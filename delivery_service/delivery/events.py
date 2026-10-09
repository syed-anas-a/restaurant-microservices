import atexit
import json
import logging
import uuid

from confluent_kafka import Producer, KafkaException
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

_producer = None

def _get_producer():
    global _producer
    if _producer is None:
        _producer = Producer({
            "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
            "client.id":"delivery-service",
            "acks":"all",
        })
        atexit.register(_producer.flush, 5)
    return _producer

def _on_delivery(err, msg):
    if err is not None:
        logger.error(
            f"Kafka delivery FAILED topic={msg.topic()} key={msg.key()} error={err}"
        )
    else:
        logger.info(
            f"Kafka delivered topic={msg.topic()} partition={msg.partition()} offset={msg.offset()} key={msg.key()}"
        )

def build_event(event_type, data):
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "occurred_at": timezone.now().isoformat(),
        "data": data
    }

def publish_event(topic, key, event):
    producer = _get_producer()
    try:
        producer.produce(
            topic=topic,
            key=str(key),
            value=json.dumps(event),
            on_delivery=_on_delivery,
        )
    except (BufferError, KafkaException):
        logger.exception("Kafka produce failed topic=%s key=%s", topic, key)
        return
    producer.poll(0)
