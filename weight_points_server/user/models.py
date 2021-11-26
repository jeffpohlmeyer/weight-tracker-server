from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.
class Profile(models.Model):
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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    weight = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    weigh_in_day = models.CharField(max_length=2, choices=WEEKDAY_CHOICES, default="SU")

    def __str__(self):
        return f"{self.user.username}, weight: {self.weight}, weigh-in day: {self.weigh_in_day}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
