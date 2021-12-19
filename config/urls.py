"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls import url

from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# from weight_points_server.user.urls import router as user_router
from weight_points_server.time_tracking.urls import router as time_router

# from weight_points_server.user.views import token_obtain_view, token_refresh_view

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

if settings.DEBUG:
    urlpatterns = [path("admin/", admin.site.urls)]
else:
    urlpatterns = [
        path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
        path("SSsjhKo1OdrmDFhq8bOO9kJgMyFnzyOS/", admin.site.urls),
    ]

urlpatterns += [
    path("api-auth/", include("rest_framework.urls")),
    url(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    url(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("auth/", include("weight_points_server.user.urls")),
    # path('auth/', include('djoser.urls')),
    path("auth/", include("djoser.urls.jwt")),
]
urlpatterns += time_router.urls

# urlpatterns += user_router.urls
