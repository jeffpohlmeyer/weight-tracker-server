from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from .utils import create_token_and_expiration

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "weight",
            "height",
            "sex",
            "weigh_in_day",
        ]


class EmailChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email"]

    """
    Overwriting this to pass updated_fields to save method of model
    """

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes("update", self, validated_data)
        info = model_meta.get_field_info(instance)

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        token_info = create_token_and_expiration()
        instance.token = token_info.get("token")
        instance.token_expiration = token_info.get("token_expiration")

        instance.save(update_fields=["email", "token", "token_expiration"])

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance


class PasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField()

    class Meta:
        model = User
        fields = ["password", "old_password"]


class PasswordForgotSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=64)

    class Meta:
        model = User
        fields = ["token", "password"]


class AuthTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["token"]
