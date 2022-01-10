from users.models import UserDB


def calculate_food_points(food, quantity, quantity_string):
    pass


def calculate_weekly_points():
    pass


def calculate_daily_points(user: UserDB) -> int:
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
