import secrets
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Profile
from .serializers import (
    ProfileSerializer,
    PasswordForgotSerializer,
    PasswordTokenGenerateSerializer,
    PasswordResetSerializer,
)


serializer_dict = {
    "Forgot Password": PasswordForgotSerializer,
    "Generate Token From Token": PasswordTokenGenerateSerializer,
    "Reset Password": PasswordResetSerializer,
}


class ProfileViewSet(
    # mixins.CreateModelMixin,
    # mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Profile.objects.all()
    # serializer_class = ProfileSerializer

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        if self.name is not None:
            return serializer_dict.get(self.name)
        return ProfileSerializer

    @action(detail=False, methods=["POST"], name="Forgot Password")
    def forgot_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            email = data.get("email")
            if email is not None:
                result = User.objects.filter(email=email)
                if len(result) == 1:
                    user = result.first()
                    profile = user.profile
                    profile.token = secrets.token_urlsafe(64)
                    profile.token_expiration = timezone.now() + timedelta(minutes=60)
                    profile.save(update_fields=["token", "token_expiration"])

        return Response(
            "If an account exists with that email then you should receive a password reset email shortly.",
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["POST"], name="Generate Token From Token")
    def regenerate_token(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                data = serializer.data
                token = data.get("token")
                profile = Profile.objects.get(token=token)
                profile.token = secrets.token_urlsafe(64)
                profile.token_expiration = timezone.now() + timedelta(seconds=60)
                profile.save(update_fields=["token", "token_expiration"])
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(dict(detail=str(e)), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["POST"], name="Reset Password")
    def reset_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                data = serializer.data
                token = data.get("token")
                password = data.get("password")
                profile = Profile.objects.get(token=token)
                if profile.token_expiration < timezone.now():
                    raise ValidationError("Token expired")
                user = profile.user
                user.set_password(password)
                profile.token = None
                profile.token_expiration = None
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(dict(detail=str(e)), status=status.HTTP_400_BAD_REQUEST)
