from django.urls import path
from .views import MenuView, MenuDetailView, CategoryView, CategoryDetailView

urlpatterns = [
    path('', MenuView.as_view(), name='menu'),
    path('items/<int:item_id>/', MenuDetailView.as_view()),

    path('categories/', CategoryView.as_view()),
    path('categories/<int:category_id>/', CategoryDetailView.as_view()),
]