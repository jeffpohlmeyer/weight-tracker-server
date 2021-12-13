import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.utils import swagger_auto_schema

from .serializers import (
    UserSerializer,
    PasswordForgotSerializer,
    AuthTokenSerializer,
    PasswordResetSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    EmailChangeSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()


info_dict = {
    "Forgot Password": dict(
        serializer=PasswordForgotSerializer,
        permission=[
            AllowAny,
        ],
    ),
    "Generate Token From Token": dict(
        serializer=AuthTokenSerializer,
        permission=[
            AllowAny,
        ],
    ),
    "Reset Password": dict(
        serializer=PasswordResetSerializer,
        permission=[
            AllowAny,
        ],
    ),
    "Change Email": dict(
        serializer=EmailChangeSerializer,
    ),
    "Change Password": dict(
        serializer=PasswordChangeSerializer,
    ),
    "Validate Email": dict(
        serializer=AuthTokenSerializer,
        permission=[
            AllowAny,
        ],
    ),
    "create": dict(
        serializer=UserCreateSerializer,
        permission=[
            AllowAny,
        ],
    ),
    "update": dict(
        serializer=UserUpdateSerializer,
    ),
}


class AuthViewSet(
    mixins.CreateModelMixin,
    # mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()

    def get_method_name(self):
        name = None
        if self.name is not None:
            name = self.name
        elif self.request.method == "POST":
            name = "create"
        elif self.request.method == "PATCH" or self.request.method == "PUT":
            name = "update"
        return name

    def get_serializer_class(self):
        name = self.get_method_name()
        if name is not None:
            return info_dict.get(name).get("serializer")

        return UserSerializer

    def get_permissions(self):
        name = self.get_method_name()
        if name is not None and info_dict.get(name).get("permission") is not None:
            return [
                permission() for permission in info_dict.get(name).get("permission")
            ]
        return super(AuthViewSet, self).get_permissions()

    @action(detail=False, methods=["POST"], name="Forgot Password")
    def forgot_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            email = data.get("email")
            if email is not None:
                result = self.queryset.filter(email=email)
                if len(result) == 1:
                    user = result.first()
                    user.token = secrets.token_urlsafe(64)
                    user.token_expiration = timezone.now() + timedelta(minutes=60)
                    user.save(update_fields=["token", "token_expiration"])

            return Response(
                "If an account exists with that email then you should receive a password reset email shortly.",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(dict(detail=str(e)), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], name="Generate Token From Token")
    def regenerate_token(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            token = data.get("token")
            user = User.objects.get(token=token)
            user.token = secrets.token_urlsafe(64)
            user.token_expiration = timezone.now() + timedelta(seconds=60)
            user.save(update_fields=["token", "token_expiration"])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(dict(detail=str(e)), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], name="Reset Password")
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            token = data.get("token")
            password = data.get("password")
            user = User.objects.get(token=token)
            if user.token_expiration < timezone.now():
                raise ValidationError("Token expired")
            user.set_password(password)
            user.token = None
            user.token_expiration = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(dict(detail=str(e)), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"], name="Change Email")
    def change_email(self, request, *args, **kwargs):
        return super(AuthViewSet, self).partial_update(request, *args, **kwargs)

    @action(detail=False, methods=["POST"], name="Validate Email")
    def validate_email(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.data
            token = data.get("token")
            user = User.objects.get(token=token)
            if user.token_expiration < timezone.now():
                raise ValidationError("Token expired")
            user.token = None
            user.token_expiration = None
            user.email_validated = True
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            return Response(dict(detail=str(e)), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"], name="Change Password")
    def change_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            if not self.request.user.check_password(
                serializer.data.get("old_password")
            ):
                raise ValidationError("Incorrect password")

            self.request.user.set_password(serializer.data.get("password"))
            self.request.user.save()
        except Exception as e:
            return Response(dict(detail=str(e)), status=status.HTTP_400_BAD_REQUEST)


class TokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={status.HTTP_200_OK: TokenObtainPairResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


token_obtain_view = DecoratedTokenObtainPairView.as_view()


class TokenRefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(responses={status.HTTP_200_OK: TokenRefreshResponseSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


token_refresh_view = DecoratedTokenRefreshView.as_view()


class TokenVerifyResponseSerializer(serializers.Serializer):
    def create(self, validated_data):
        raise NotImplementedError()

    def update(self, instance, validated_data):
        raise NotImplementedError()


class DecoratedTokenVerifyView(TokenVerifyView):
    @swagger_auto_schema(responses={status.HTTP_200_OK: TokenVerifyResponseSerializer})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
