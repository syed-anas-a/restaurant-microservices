from django.urls import path
from .views import DeliveryView, DeliveryDetailView, DeliveryStatusView

urlpatterns = [
    path('', DeliveryView.as_view()),
    path('<int:delivery_id>/', DeliveryDetailView.as_view()),
    path('<int:delivery_id>/status/', DeliveryStatusView.as_view()),
]