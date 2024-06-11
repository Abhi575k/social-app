from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id','email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['email'] = validated_data['email'].lower()

        user = User.objects.create_user(
            email=validated_data['email'], 
            password=validated_data['password']
        )
        if user:
            return user
        raise serializers.ValidationError('Incorrect Credentials')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'date_joined', 'last_login', 'is_active', 'is_staff', 'is_superuser']