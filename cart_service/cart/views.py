from .models import Cart
from .serializers import CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .services import CartService
from .exceptions import MenuItemNotFound, MenuServiceUnavailable, CartItemNotFound
from rest_framework.permissions import IsAuthenticated

# Create your views here.
class CartView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.prefetch_related("items").get_or_create(user_id=request.user.user_id)
        serializer = CartSerializer(cart)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        input_serializer = AddCartItemSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            cart_item = CartService.add_item(
                user_id=request.user.user_id, 
                **input_serializer.validated_data,
            )
        except MenuItemNotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        except MenuServiceUnavailable as e:
            return Response({"error":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


        serializer = CartItemSerializer(cart_item)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, menu_item_id):
        input_serializer = UpdateCartItemSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            cart_item = CartService.update_item(
                user_id = request.user.user_id,
                menu_item_id=menu_item_id,
                **input_serializer.validated_data
            )
        except CartItemNotFound as e:
            return Response({"error":str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemSerializer(cart_item)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, menu_item_id):
        try:
            CartService.delete_item(
                user_id=request.user.user_id,
                menu_item_id=menu_item_id
            )
        except CartItemNotFound as e:
            return Response({"error":str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message":"Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        