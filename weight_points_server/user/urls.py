from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CheckEmailUsernameView,
    CustomDjoserViewset,
)

app_name = "users"

router = DefaultRouter()
router.register("users", CustomDjoserViewset)

urlpatterns = router.urls

urlpatterns += [
    path("check-email-username/", CheckEmailUsernameView.as_view()),
]
