from django.shortcuts import render
from rest_framework.views import APIView
from .permissions import IsAssignedCrew, IsDeliveryCustomer
from .services import DeliveryService
from django.shortcuts import get_object_or_404
from .models import Delivery
from remote_auth.permissions import IsManager
from rest_framework.permissions import IsAuthenticated
from .serializers import DeliveryCreateSerializer, DeliverySerializer
from rest_framework.response import Response
from rest_framework import status
from .exceptions import (
    OrderServiceUnavailable, OrderNotFound,
    UserServiceUnavailable, UserNotFound,
    UserNotDeliveryCrew, OrderNotPlaced
)
from django.db import IntegrityError

# Create your views here.
class DeliveryView(APIView):

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(),IsManager()]
        return [IsAuthenticated()]

    def get(self, request):
        if request.user.group == "MANAGER":
            delivery = Delivery.objects.all()
        elif request.user.group == "DELIVERY CREW":
            delivery = Delivery.objects.filter(crew_id=request.user.user_id)
        elif request.user.group == "CUSTOMER":
            delivery = Delivery.objects.filter(customer_id=request.user.user_id)
        return Response(DeliverySerializer(delivery, many=True).data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = DeliveryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            delivery = DeliveryService.assign_delivery(serializer.validated_data, request.headers.get("Authorization"))
        except UserNotFound as e:
            return Response({"error":str(e)}, status=status.HTTP_404_NOT_FOUND)
        except UserServiceUnavailable as e:
            return Response({"error":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except UserNotDeliveryCrew as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except OrderNotFound as e:
            return Response({"error":str(e)}, status=status.HTTP_404_NOT_FOUND)
        except OrderServiceUnavailable as e:
            return Response({"error":str(e)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except IntegrityError as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except OrderNotPlaced as e:
            return Response({"error":str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DeliverySerializer(delivery).data, status=status.HTTP_201_CREATED)

class DeliveryDetailView(APIView):
    ...
    


