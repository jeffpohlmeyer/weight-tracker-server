from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.translation import gettext_lazy as _


class CustomAccountManager(BaseUserManager):
    def create_user(self, email, username, password, **kwargs):
        if not email:
            raise ValueError(_("Please provide an email address"))
        email = self.normalize_email(email)

        user = self.model(email=email, username=username, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)
        if kwargs.get("is_staff") is not True:
            raise ValueError(_("Please assign is_staff=True for superuser"))
        if kwargs.get("is_superuser") is not True:
            raise ValueError(_("Please assign is_superuser=True for superuser"))

        return self.create_user(email, username, password, **kwargs)


class CustomUser(AbstractBaseUser):
    SEX_CHOICES = [("M", "Male"), ("F", "Female")]
    WEEKDAY_CHOICES = [
        ("SU", "Sunday"),
        ("M", "Monday"),
        ("T", "Tuesday"),
        ("W", "Wednesday"),
        ("TR", "Thursday"),
        ("F", "Friday"),
        ("SA", "Saturday"),
    ]
    MESSAGE_TYPE_CHOICES = [
        ("registration", "Registration"),
        ("registration_confirm", "Registration Confirmation"),
        ("password_forgot", "Forgot Password"),
        ("password_change_confirm", "Password Change Confirmation"),
        ("change_email", "Change Email"),
        ("change_email_confirm", "Email Change Confirmation"),
    ]

    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("First Name"), max_length=256)
    last_name = models.CharField(_("Last Name"), max_length=256)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    weigh_in_day = models.CharField(max_length=2, choices=WEEKDAY_CHOICES, default="SU")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomAccountManager()

    def __str__(self):
        return f"{self.email}, weight: {self.weight}, weigh-in day: {self.weigh_in_day}"
