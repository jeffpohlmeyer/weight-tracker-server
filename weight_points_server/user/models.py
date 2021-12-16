from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


from .emails import Email
from .utils import create_token, create_token_expiration


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
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
    old_email = models.EmailField(
        _("old email address"),
        null=True,
        blank=True,
        help_text=_(
            "This is only used in the case where a user is updating an email address. "
            'In this case the "current" email address becomes the old one and the new email address moves into the '
            "general email field, while being set as invalid."
        ),
    )
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    weigh_in_day = models.CharField(max_length=2, choices=WEEKDAY_CHOICES, default="SU")
    token = models.CharField(
        default=create_token, max_length=1024, null=True, blank=True
    )
    token_expiration = models.DateTimeField(
        default=create_token_expiration, null=True, blank=True
    )
    email_validated = models.BooleanField(
        _("email validated"),
        default=False,
        help_text=_(
            "Boolean that indicates whether the email address has been validated or not."
        ),
    )
    message_type = models.CharField(
        max_length=32,
        choices=MESSAGE_TYPE_CHOICES,
        default="registration",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email}, weight: {self.weight}, weigh-in day: {self.weigh_in_day}"

    def save(self, message_type=None, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        self.message_type = kwargs.get("message_type")


@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, **kwargs):
    if instance.message_type is not None:
        Email(instance).send_message()
    print("sender", sender)
    print("instance", instance)
