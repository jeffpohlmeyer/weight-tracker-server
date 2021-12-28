# from django.db.models import Sum

# from weight_points_server.food_tracking.models import Meal, FoodInstance
# from weight_points_server.time_tracking.models import Day


def calculate_food_points(food, quantity, quantity_string):

    pass


def calculate_weekly_points():

    pass


def calculate_daily_points(user):
    MIN_POINTS = 26
    MAX_POINTS = 71

    weight = float(user.weight) * 0.453592
    height = user.height * 0.0254

    if user.sex == "M":
        tee = 864 - (9.72 * user.age) + (1.12 * (14.2 * weight + 503 * height))
    else:
        tee = 387 - (7.31 * user.age) + (1.14 * (10.9 * weight + 660.7 * height))
    atee = tee - (tee * 0.1) + 200
    target = round(min(max(atee - 1000, 1000), 2500) / 35)
    if user.sex == "F":
        if user.nursing == 1:
            target += 7
        elif user.nursing == 2:
            target += 14
    return max(min(target - 11, MAX_POINTS), MIN_POINTS)


# def update_daily_points(day):
#     meal_ids = Meal.objects.filter(day=day).values_list("id")
#     points = FoodInstance.objects.filter(meal_id__in=meal_ids).aggregate(Sum("points"))[
#         "points__sum"
#     ]
#     points_remaining = day.total_points - points
#     day.points_used = points
#     day.points_remaining = points_remaining
#     day.save()
#     if points_remaining < 0:
#         weekly_points_used = Day.objects.filter(
#             week=day.week, points_remaining__lt=0
#         ).aggregate(Sum("points_remaining"))["points_remaining__sum"]
#         week = day.week
#         week.weekly_points_used = -weekly_points_used
#         week.weekly_points_remaining = week.weekly_total_points + weekly_points_used
#         week.save()
