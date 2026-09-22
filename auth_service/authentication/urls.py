from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from .views import RegisterView, UserView, UserDetailView, LogoutView

urlpatterns = [
    path('register/', RegisterView.as_view()),

    path('login/', TokenObtainPairView.as_view()),
    path('login/refresh/', TokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),

    path('users/', UserView.as_view()),
    path('users/<int:user_id>/', UserDetailView.as_view()),
]