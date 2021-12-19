from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def set_weigh_in_day():
    return timezone.now().today().weekday()


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
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]
    NURSING_CHOICES = [(0, "None"), (1, "Supplemental"), (2, "Exclusive")]

    username = None
    email = models.EmailField(_("email address"), unique=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    weigh_in_day = models.IntegerField(
        choices=WEEKDAY_CHOICES, default=set_weigh_in_day
    )
    birth_date = models.DateField(null=True, blank=True)
    weekly_points = models.IntegerField(default=49)
    nursing = models.IntegerField(default=0, choices=NURSING_CHOICES)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @property
    def age(self):
        today = timezone.now().today().date()
        if today.month > self.birth_date.month:
            return today.year - self.birth_date.year
        elif today.month == self.birth_date.month:
            if today.day >= self.birth_date.day:
                return today.year - self.birth_date.year
            else:
                return today.year - self.birth_date.year - 1
        else:
            return today.year - self.birth_date.year - 1
