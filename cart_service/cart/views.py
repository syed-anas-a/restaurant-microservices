from django.shortcuts import render
from .models import CartItem, Cart
from .serializers import CartSerializer, CartItemSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .services import CartService
from .exceptions import MenuItemNotFound
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class CartView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = Cart.objects.get(user_id=request.user.user_id)

        if not cart:
            return Response({"items":"[]", "total":"0.0"}, status=status.HTTP_200_OK)
        
        cart_items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(cart_items, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        menu_item_id = request.data.get("menu_item_id")
        quantity = request.data.get("quantity", 1)

        try:
            cart_item = CartService.add_to_cart(
                user_id=request.user.user_id, 
                menu_item_id=menu_item_id, 
                quantity=quantity
            )
        except MenuItemNotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(cart_item)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
