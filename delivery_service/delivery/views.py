from django.shortcuts import render
from rest_framework.views import APIView
from .permissions import IsAssignedCrew, IsDeliveryCustomer
from .services import DeliveryService
from django.shortcuts import get_object_or_404
from .models import Delivery
from remote_auth.permissions import IsManager
from rest_framework.permissions import IsAuthenticated
from .serializers import DeliveryCreateSerializer, DeliverySerializer, DeliveryStatusSerializer
from rest_framework.response import Response
from rest_framework import status
from .exceptions import (
    OrderServiceUnavailable, OrderNotFound,
    UserServiceUnavailable, UserNotFound,
    UserNotDeliveryCrew, OrderNotPlaced,
    DeliveryInProgress
)
from django.db import IntegrityError
from django.utils import timezone
from django.db import transaction

# Create your views here.
class DeliveryView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(),IsManager()]
        return [IsAuthenticated()]

    def get(self, request):
        if request.user.group == "MANAGER":
            deliveries = Delivery.objects.all()
        elif request.user.group == "DELIVERY CREW":
            deliveries = Delivery.objects.filter(crew_id=request.user.user_id)
        elif request.user.group == "CUSTOMER":
            deliveries = Delivery.objects.filter(customer_id=request.user.user_id)
        else:
            return Response({"error":"Not authorized"}, status=status.HTTP_403_FORBIDDEN)

        return Response(DeliverySerializer(deliveries, many=True).data, status=status.HTTP_200_OK)

class DeliveryDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated(),IsManager()]
        return [IsAuthenticated()]

    def get(self, request, delivery_id):
        delivery = get_object_or_404(Delivery, id=delivery_id)

        if request.user.group == "CUSTOMER" and request.user.user_id != delivery.customer_id:
            return Response({"error":"You can only view your own delivery details"}, status=status.HTTP_403_FORBIDDEN)
        if request.user.group == "DELIVERY CREW" and request.user.user_id != delivery.crew_id:
            return Response({"error":"You can only view deliveries assigned to you"}, status=status.HTTP_403_FORBIDDEN)

        return Response(DeliverySerializer(delivery).data, status=status.HTTP_200_OK)

    def patch(self, request, delivery_id):
    
        new_crew_id = request.data.get("crew_id")

        try:
            delivery = DeliveryService.reassign_delivery(
                new_crew_id=new_crew_id,
                delivery_id=delivery_id,
                auth_header=request.headers.get("Authorization")
            )
        except UserNotFound as e:
            return Response({"error":str(e)}, status=status.HTTP_404_NOT_FOUND)
        except UserServiceUnavailable as e:
            return Response({"error":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except DeliveryInProgress as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except UserNotDeliveryCrew as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DeliverySerializer(delivery).data, status=status.HTTP_200_OK)

class DeliveryStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, delivery_id):
        delivery = get_object_or_404(Delivery, id=delivery_id)
        if delivery.crew_id != request.user.user_id:
            return Response({
                "error":"Not your delivery"
                }, status=status.HTTP_403_FORBIDDEN
            )
        serializer = DeliveryStatusSerializer(instance=delivery, data=request.data)
        serializer.is_valid(raise_exception=True)
        delivery.status = serializer.validated_data["status"]

        with transaction.atomic():
            if delivery.status == Delivery.Status.DELIVERED:
                delivery.delivered_at = timezone.now()
                delivery.save(update_fields=["status", "delivered_at"])
            else:
                delivery.save(update_fields=["status"])
                
            transaction.on_commit(
                lambda:DeliveryService.publish_delivery_status_changed(delivery=delivery),
                robust=True
            )

        return Response(DeliverySerializer(delivery).data, status=status.HTTP_200_OK)
        

    


