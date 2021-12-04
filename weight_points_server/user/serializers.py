from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Profile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = "__all__"


class PasswordForgotSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]


class PasswordResetSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64)

    class Meta:
        model = Profile
        fields = ["token", "password"]


class PasswordTokenGenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["token"]
