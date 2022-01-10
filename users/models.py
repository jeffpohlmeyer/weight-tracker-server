from dateutil.relativedelta import relativedelta
from datetime import date, datetime
from enum import Enum, IntEnum, auto
from typing import Optional, Dict

from fastapi_users import models
from fastapi_users.db import MongoDBUserDatabase
from pydantic import BaseModel, Field, root_validator

from core.db import get_db


class SexChoices(str, Enum):
    male = "Male"
    female = "Female"


class WeekdayChoices(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class NursingChoices(IntEnum):
    NONE = 0
    SUPPLEMENTAL = 1
    EXCLUSIVE = 2


class OptionalUser(BaseModel):
    weight: Optional[float] = None
    height: Optional[int] = None
    sex: Optional[SexChoices] = None
    weigh_in_day: Optional[WeekdayChoices] = None
    birth_date: Optional[date] = None
    weekly_points: Optional[int] = None
    nursing: Optional[NursingChoices] = Field(
        default=NursingChoices.NONE,
        description="If sex is set to male then this option will have no effect.",
    )


class User(models.BaseUser, OptionalUser):
    age: Optional[int] = None


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(models.BaseUserUpdate, OptionalUser):
    @classmethod
    @root_validator
    def compute_age(cls, values) -> Dict:
        print("values", values)
        values["age"] = relativedelta(datetime.today(), values["birth_date"]).years

        return values


class UserDB(User, models.BaseUserDB, OptionalUser):
    birth_date: Optional[datetime] = None
    has_been_updated: bool = False


async def get_user_db():
    db = get_db()
    collection = db["users"]
    yield MongoDBUserDatabase(UserDB, collection)
