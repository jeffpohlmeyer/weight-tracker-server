from datetime import timedelta

from django.utils import timezone

from weight_points_server.time_tracking.models import Week, Day
from .points_calculators import calculate_daily_points


def create_days(start_date, user, week, num_days):
    if num_days == 0:
        return start_date
    daily_points = calculate_daily_points(user)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    days = []
    for date in dates:
        days.append(
            Day(
                total_points=daily_points,
                points_remaining=daily_points,
                day_of_week=date.weekday(),
                date=date,
                week=week,
                user=user,
            )
        )
    Day.objects.bulk_create(days)
    return dates[-1]


def create_week(start_date, user, num_days=7):
    week = Week.objects.create(
        start_date=start_date,
        weekly_total_points=user.weekly_points,
        weight=user.weight,
        user=user,
    )
    return create_days(start_date, user, week, num_days)


def backfill_weeks(user):
    latest_day = Day.objects.filter(user=user).last().date
    today = timezone.now().today().date()
    count = 0
    if latest_day < today:
        latest_day = create_week(
            latest_day + timedelta(days=1),
            user,
            (user.weigh_in_day - latest_day.weekday() - 1) % 7,
        )
        while latest_day < today and count < 52:
            latest_day = create_week(latest_day + timedelta(days=1), user)
            count += 1
