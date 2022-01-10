from datetime import datetime
from decimal import Decimal
from enum import IntEnum
import uuid

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field, condecimal
import pymongo


class Week(Document):
    weekly_total_points: int = Field(default=49)
    weekly_points_remaining: int = Field(default=49)
    weekly_points_used: int = Field(0)
    weight: condecimal(gt=Decimal(0), max_digits=5, decimal_places=2) = Field(...)
    start_date: datetime
    weight_recorded: bool = Field(default=False)
    user: uuid.UUID

    class Collection:
        name = "weeks"
        indexes = [
            pymongo.IndexModel(
                [("user", pymongo.TEXT), ("start_date", pymongo.ASCENDING)],
                name="week_user_date_index",
                unique=True,
            )
        ]


class DayOfWeek(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Day(Document):
    total_points: int
    points_remaining: int
    points_used: int
    day_of_week: DayOfWeek = Field(default=DayOfWeek.SUNDAY)
    date: datetime
    week: PydanticObjectId
    user: uuid.UUID

    class Collection:
        name = "days"
        indexes = [
            pymongo.IndexModel(
                [("user", pymongo.TEXT), ("date", pymongo.ASCENDING)],
                name="day_user_date_index",
                unique=True,
            )
        ]
