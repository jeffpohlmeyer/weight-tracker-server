from django.urls import re_path

from ..views import TokenDestroyView, TokenCreateView

urlpatterns = [
    re_path(r"^token/login/?$", TokenCreateView.as_view(), name="login"),
    re_path(r"^token/logout/?$", TokenDestroyView.as_view(), name="logout"),
]
