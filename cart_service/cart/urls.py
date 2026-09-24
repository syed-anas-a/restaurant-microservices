from django.urls import path
from .views import CartView, CartItemView

urlpatterns = [
    path('', CartView.as_view()),
    path('items/<int:menu_item_id>/', CartItemView.as_view()),
]