from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


class UserAdmin(BaseUserAdmin):
    list_display = [
        "email",
    ]
    exclude = ("username",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Profile info"),
            {
                "fields": (
                    "weight",
                    "height",
                    "sex",
                    "weigh_in_day",
                    "email_validated",
                    "token",
                    "token_expiration",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "weight",
                    "height",
                    "sex",
                    "weigh_in_day",
                    "email_validated",
                ),
            },
        ),
    )
    ordering = ("email",)


admin.site.register(CustomUser, UserAdmin)
