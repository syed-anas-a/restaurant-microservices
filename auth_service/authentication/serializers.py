from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    group = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'password', 'group']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop(password, None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)

        if password:
            instance.set_password(password) 
            
        instance.save()

        return instance
