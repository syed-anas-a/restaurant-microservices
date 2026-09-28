from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .services import OrderService
from .exceptions import (
    CartClearFailed, CartRestoreFailed,
    CartServiceUnavailable, CartEmpty,
    MenuServiceUnavailable, MenuItemNotFound
)
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer
from remote_auth.permissions import IsManager, IsOwner
from django.shortcuts import get_object_or_404
from .models import Order

# Create your views here.
class OrderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        order = OrderService.get_all_orders(user_id=request.user.user_id)

        serializer = OrderSerializer(order, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        auth_header = request.headers.get("Authorization")
        try:
            order = OrderService.place_order(auth_header=auth_header, user_id=request.user.user_id, email=request.user.email)

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
        except CartRestoreFailed as e:
            return Response({"error":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        serializer = OrderSerializer(order)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if request.user.group != "MANAGER" and order.user_id != request.user.user_id:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, order_id):
        if request.user.group != "MANAGER":
            return Response(status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get("status")
        order = get_object_or_404(Order, id=order_id)
        if new_status not in Order.Status.values:
            return Response({"error":"Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save(update_fields=["status"])

        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
        