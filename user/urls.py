from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet


router = DefaultRouter()
router.register(r"users", ProfileViewSet, basename="user_profile")
