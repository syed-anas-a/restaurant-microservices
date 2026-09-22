from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import UserSerializer
from .models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsOwner, IsManager, IsCustomer, IsDeliveryCrew

# Create your views here.
class RegisterView(APIView):

    permission_classes=[AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": serializer.data,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_201_CREATED)

class UserView(APIView):

    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        data = User.objects.all()
        serializer = UserSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserDetailView(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def is_manager(self):
        return self.request.user.group == "MANAGER"

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if not self.is_manager():
            self.check_object_permissions(request, user)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if not self.is_manager():
            self.check_object_permissions(request, user)

        serializer = UserSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        if not self.is_manager():
            self.check_object_permissions(request, user)

        user.delete()
        return Response(status=status.HTTP_NO_CONTENT)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logged out"}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error":"Invalid Token"}, status=status.HTTP_400_BAD_REQUEST)

class VerifyTokenView(APIView):

    permission_classes = [AllowAny]
    
    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"error":"Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            user = get_object_or_404(User, id=user_id)
            return Response(
                {
                    "user_id": user_id,
                    "group": user.group
            })

        except TokenError:
            return Response({"error": "Invalid or expired token"},
                            status=status.HTTP_401_UNAUTHORIZED)



