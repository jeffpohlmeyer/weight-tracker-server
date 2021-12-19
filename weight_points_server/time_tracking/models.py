from datetime import timedelta

from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

from weight_points_server.utils.points_calculators import calculate_daily_points


class Week(models.Model):
    weekly_total_points = models.IntegerField(default=49)
    weekly_points_remaining = models.IntegerField(default=49)
    weekly_points_used = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    start_date = models.DateField()
    weight_recorded = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user_id", "start_date")

    def __str__(self):
        return f"Week starting on {self.start_date}"


class Day(models.Model):
    DAY_OF_WEEK_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    total_points = models.IntegerField()
    points_remaining = models.IntegerField()
    points_used = models.IntegerField(default=0)
    activity_points = models.IntegerField(default=0)
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES)
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user_id", "date")

    def __str__(self):
        return f"{self.date}"


@receiver(post_save, sender=Week)
def days_of_week(sender, instance, created, **kwargs):
    if created:
        print("created")


#     user = instance.user
#     daily_points = calculate_daily_points(user)
#     if created:
#         Day.objects.filter(user=user, date__gte=instance.start_date).delete()
#         date = instance.start_date
#         days = []
#         for _ in range(7):
#             day_of_week = date.weekday()
#             days.append(
#                 Day(
#                     total_points=daily_points,
#                     points_remaining=daily_points,
#                     day_of_week=day_of_week,
#                     date=date,
#                     week=instance,
#                     user=user,
#                 )
#             )
#             date += timedelta(days=1)
#         Day.objects.bulk_create(days)
#     else:
#         if timezone.now().today().weekday() == instance.user.weigh_in_day:
#             qs = Day.objects.filter(user=user, week=instance)
#             for item in qs:
#                 item.total_points = daily_points
#                 item.points_remaining = daily_points - item.points_used
#             Day.objects.bulk_update(qs, ["total_points", "points_remaining"])
