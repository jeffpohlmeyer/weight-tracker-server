from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status

from time_tracking.controllers import fetch_day
from time_tracking.models import Week, Day
from users.controllers import current_active_user
from users.models import UserDB
from utils import time_tracking

week_router = APIRouter(
    prefix="/week",
    tags=["Time Tracking", "Week"],
)

day_router = APIRouter(
    prefix="/day",
    tags=["Time Tracking", "Day"],
)


@week_router.get("/", summary="For testing purposes only")
async def get_weeks(user: UserDB = Depends(current_active_user)) -> list[Week]:
    """
    There will be no point where you'll need/want to get ALL weeks.  This is simply testing functionality.
    """
    return await Week.find({"user": user.id}).to_list()


@week_router.post(
    "/{start_date}",
    status_code=status.HTTP_201_CREATED,
    summary="For testing purposes only",
)
async def create_week(
    start_date: date, user: UserDB = Depends(current_active_user)
) -> None:
    """
    There will be no point where you'll be creating weeks from an API call.
    Weeks will only ever be created when fetching a given day.
    """
    await time_tracking.create_week(
        datetime.combine(start_date, datetime.min.time()), user
    )


@day_router.get(
    "/{input_date}",
    summary="Get a given date",
)
async def get_day(input_date: date, user: UserDB = Depends(current_active_user)) -> Day:
    """
    The input parameter must be a valid datetime type.
    See <https://pydantic-docs.helpmanual.io/usage/types/#datetime-types> for more information.

    - date fields can be:
        - date, existing date object
        - int or float, see datetime
        - str, following formats work:
            - YYYY-MM-DD
            - int or float, see datetime
    """
    try:
        return await fetch_day(input_date, user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
