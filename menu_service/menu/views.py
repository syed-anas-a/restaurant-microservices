from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from .serializers import MenuSerializer, CategorySerializer
from .models import Menu, Category
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

# Create your views here.
class MenuView(APIView):

    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Menu.objects.all()
        serializer = MenuSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        if request.user.group != "MANAGER":
            return Response({"error":"Not Authorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = MenuSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MenuDetailView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, item_id):
        item = get_object_or_404(Menu, id=item_id)
        serializer = MenuSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def put(self, request, item_id):
        if request.user.group != "MANAGER":
            return Response({"error":"Not Authorized"}, status=status.HTTP_403_FORBIDDEN)
        item = get_object_or_404(Menu, id=item_id)
        serializer = MenuSerializer(data=item)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_OK)

    def delete(self, request, item_id):
        if request.user.group != "MANAGER":
            return Response({"error":"Not Authorized"}, status=status.HTTP_403_FORBIDDEN)
        item = get_object_or_404(Menu, id=item_id)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CategoryView(APIView):

    permission_classes = [AllowAny]
    
    def get(self, request):
        queryset = Category.objects.all()
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        if request.user.group != "MANAGER":
            return Response({"error":"Not Authorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = CategorySerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(category)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def put(self, request, category_id):
        if request.user.group != "MANAGER":
            return Response({"error":"Not Authorized"}, status=status.HTTP_403_FORBIDDEN)
        obj = get_object_or_404(Category, id=category_id)
        serializer = CategorySerializer(obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_OK)

    def delete(self, request, category_id):
        if request.user.group != "MANAGER":
            return Response({"error":"Not Authorized"}, status=status.HTTP_403_FORBIDDEN)
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)