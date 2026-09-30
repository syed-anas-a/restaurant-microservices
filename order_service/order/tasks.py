import logging
from celery import shared_task
from .models import Order
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@shared_task(
    autoretry_for=(OSError,),
    retry_backoff=True,
    retry_kwargs={"max_retries":5},
)
def send_order_confirmation_email(order_id, email):
    try:
        order = Order.objects.prefetch_related("items").get(id=order_id)
    except Order.DoesNotExist:
        logger.warning(f"Order {order_id} not found")
        return

    email_content = ("\n").join(
        f"Item {item.menu_item_id} x {item.quantity} @ Rs.{item.price}"
        for item in order.items.all()
    )

    send_mail(
        subject=f"Order #{order_id} placed",
        message=(
            f"Your order has been placed.\n\n"
            f"Order ID: {order.id}\n"
            f"Items:\n{email_content}\n\n"
            f"Total: ₹{order.order_value}\n"
        ),
        from_email=None,
        recipient_list=[email],
    )