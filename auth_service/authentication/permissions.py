from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
            return request.user.group == "MANAGER"

class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
            return request.user.group == "DELIVERY_CREW"

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.group == "CUSTOMER"

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj