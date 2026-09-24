from rest_framework import serializers
from .models import Cart, CartItem
from decimal import Decimal

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'menu_item_id', 'price', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total']

    def get_total(self, obj):
        total = sum((item.price * item.quantity for item in obj.items.all()), Decimal('0.00'))
        return str(total.quantize(Decimal('0.01')))

class AddCartItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1) 

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)

class RestoreCartItemSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1) 
    price = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=Decimal("0.00"))

class RestoreCartSerializer(serializers.Serializer):
    items = RestoreCartItemSerializer(many=True)


