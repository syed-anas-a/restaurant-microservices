from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import OrderService
from .exceptions import (
    CartClearFailed,
    CartServiceUnavailable, CartEmpty,
    MenuServiceUnavailable, MenuItemNotFound
)
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer

# Create your views here.
class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        order = OrderService.get_all_orders(user_id=request.user.user_id)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        auth_header = request.headers.get("Authorization")
        try:
            order = OrderService.place_order(auth_header=auth_header, user_id=request.user.user_id)

        except MenuItemNotFound as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except MenuServiceUnavailable as e:
            return Response({"error":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except CartEmpty as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except CartClearFailed as e:
            return Response({"error":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except CartServiceUnavailable as e:
            return Response({"error":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = OrderSerializer(order, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        