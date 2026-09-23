from rest_framework.serializers import ModelSerializer
from .models import Cart, CartItem

class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

class CartItemSerializer(ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'