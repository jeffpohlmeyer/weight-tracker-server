from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CheckEmailUsernameView, CustomDjoserViewset
from djoser.urls.jwt import urlpatterns as djoser_urls

app_name = "users"

router = DefaultRouter()
router.register("users", CustomDjoserViewset)

urlpatterns = router.urls

urlpatterns += djoser_urls

urlpatterns += [path("check-email-username/", CheckEmailUsernameView.as_view())]
