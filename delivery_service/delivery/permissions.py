from rest_framework.permissions import BasePermission

class IsAssignedCrew(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.user_id == obj.crew_id

class IsDeliveryCustomer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.user_id == obj.customer_id

    
