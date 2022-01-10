from datetime import date, datetime

from time_tracking.models import Day
from users.models import UserDB
from utils.time_tracking import backfill_weeks


async def fetch_day(date_val: date, user: UserDB) -> Day:
    await backfill_weeks(user)
    return await Day.find_one(
        {"user": user.id, "date": datetime.combine(date_val, datetime.min.time())}
    )
