from rest_framework.permissions import BasePermission
from django.conf import settings

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.group == "MANAGER"

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
            return request.user.group == "DELIVERY CREW"

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.group == "CUSTOMER"

class IsInternalService(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get("X-Internal-Token")
        if not token:
            return False
        return token == settings.INTERNAL_SERVICE_TOKEN
