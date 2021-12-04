from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet


router = DefaultRouter()
router.register(r"auth", ProfileViewSet, basename="user_auth")
# router.register(r"auth", AuthViewSet, basename="auth")
