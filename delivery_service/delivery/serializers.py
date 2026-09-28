from rest_framework import serializers
from .models import Delivery

class DeliveryCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    crew_id = serializers.IntegerField(min_value=1)

class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ['id', 'order_id', 'customer_id', 'crew_id', 'status', 'assigned_at', 'delivered_at']

class DeliveryStatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=20, choices=Delivery.Status.values)

    def validate_status(self, value):
        current_status = self.instance.status
        allowed = Delivery.ALLOWED_TRANSITIONS.get(current_status, set())
        if value not in allowed:
            raise serializers.ValidationError(
                f"Cannot transition from {current_status} to {value}"
            )
        return value