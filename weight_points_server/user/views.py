from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from djoser.signals import user_activated
from djoser.views import UserViewSet
from djoser.compat import get_user_email
from djoser.conf import settings


User = get_user_model()


class CustomDjoserViewset(UserViewSet):
    def perform_update(self, serializer):
        super(UserViewSet, self).perform_update(serializer)
        user = serializer.instance
        # should we send activation email after update?
        if settings.SEND_ACTIVATION_EMAIL and not user.is_active:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.activation(self.request, context).send(to)

    @staticmethod
    def generate_jwt_pair(user):
        # Pull from jwt ObtainTokenPairView to generate token on activation
        refresh = RefreshToken.for_user(user)
        data = dict(refresh=str(refresh), access=str(refresh.access_token))

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        return data

    # Overwrite Djoser activation route to return token(s) when confirming email
    @action(["post"], detail=False)
    def activation(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        user.is_active = True
        user.save()

        user_activated.send(sender=self.__class__, user=user, request=self.request)

        if settings.SEND_CONFIRMATION_EMAIL:
            context = {"user": user}
            to = [get_user_email(user)]
            settings.EMAIL.confirmation(self.request, context).send(to)

        return Response(self.generate_jwt_pair(user), status=status.HTTP_200_OK)

    @action(["post"], detail=False)
    def reset_password_confirm(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.set_password(serializer.data["new_password"])
        if hasattr(serializer.user, "last_login"):
            serializer.user.last_login = now()
        serializer.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": serializer.user}
            to = [get_user_email(serializer.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        return Response(
            data=dict(**self.generate_jwt_pair(serializer.user)),
            status=status.HTTP_200_OK,
        )


class CheckEmailUsernameView(APIView):
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request, *args, **kwargs):
        email = request.query_params.get("email")
        username = request.query_params.get("username")
        if email is None and username is None:
            return Response(
                "Please provide an email address or username",
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif email is None:
            try:
                User.objects.get(username=username)
                return Response(
                    "An account with that username already exists.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except User.DoesNotExist:
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            try:
                User.objects.get(email=email)
                return Response(
                    "An account with that email address already exists.",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except User.DoesNotExist:
                return Response(status=status.HTTP_204_NO_CONTENT)
