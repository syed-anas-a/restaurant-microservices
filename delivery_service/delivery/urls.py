from django.urls import path
from .views import DeliveryView

urlpatterns = [
    path('', DeliveryView.as_view()),
]