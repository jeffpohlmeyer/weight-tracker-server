from rest_framework.routers import DefaultRouter

from .views import AuthViewSet  # , PasswordViewSet


router = DefaultRouter()
router.register(r"auth", AuthViewSet, basename="user_auth")
# router.register(r"password", PasswordViewSet, basename="password")
