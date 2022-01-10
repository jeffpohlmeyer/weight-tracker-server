from datetime import date, datetime, timedelta

from time_tracking.models import Day, Week
from users.models import UserDB, WeekdayChoices
from utils.points_calculators import calculate_daily_points


async def create_days(
    start_date: datetime, user: UserDB, week: Week, num_days: int
) -> datetime:
    if num_days == 0:
        return start_date
    daily_points = calculate_daily_points(user)
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    days = []
    for dt in dates:
        days.append(
            Day(
                total_points=daily_points,
                points_remaining=daily_points,
                points_used=0,
                day_of_week=dt.weekday(),
                date=dt,
                week=week.id,
                user=user.id,
            )
        )
    created_days = await Day.insert_many(days)
    meals = []
    for day in created_days.inserted_ids:
        for meal in range(4):
            # TODO: you'll need to link to uncomment the below code once the Meal model is created
            meals.append(day)
            # meals.append(Meal(name=meal, day=day, user=user.id))
    # await Meal.insert_many(meals)
    return dates[-1]


async def create_week(
    start_date: datetime, user: UserDB, num_days: int = 7
) -> datetime:
    new_week = Week(
        start_date=start_date,
        weekly_total_points=user.weekly_points,
        weight=user.weight,
        user=user.id,
    )
    week = await new_week.insert()
    _date = await create_days(start_date, user, week, num_days)
    return _date


async def backfill_weeks(user: UserDB):
    latest_day = await Day.find({"user": user.id}).sort("-date").limit(1).to_list()
    if len(latest_day) == 0:
        latest_date = datetime.combine(date.today(), datetime.min.time()) - timedelta(
            days=7
        )
    else:
        latest_date = latest_day[0].date
    today = datetime.combine(date.today(), datetime.min.time())
    count = 0
    if latest_date < today:
        latest_date = await create_week(
            latest_date + timedelta(days=1),
            user,
            (user.weigh_in_day - latest_date.date().weekday() - 1) % 7,
        )
        while latest_date < today and count < 52:
            latest_date = await create_week(latest_date + timedelta(days=1), user)
            count += 1
