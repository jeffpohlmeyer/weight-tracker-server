from typing import Optional
from enum import Enum, IntEnum
from fastapi_users import models


class SexEnum(str, Enum):
    male = "male"
    female = "female"


class WeekdayEnum(IntEnum):
    Sunday = 0
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6


class User(models.BaseUser):
    name: str
    weight: Optional[float]
    height: Optional[int]
    sex: Optional[SexEnum]
    weigh_in_day: Optional[WeekdayEnum]


class UserCreate(models.BaseUserCreate):
    name: str
    weight: Optional[float]
    height: Optional[int]
    sex: Optional[SexEnum]
    weigh_in_day: Optional[WeekdayEnum]


class UserUpdate(models.BaseUserUpdate):
    name: Optional[str]
    weight: Optional[float]
    height: Optional[int]
    sex: Optional[SexEnum]
    weigh_in_day: Optional[WeekdayEnum]


class UserDB(User, models.BaseUserDB):
    weight: Optional[float]
    height: Optional[int]
    sex: Optional[SexEnum]
    weigh_in_day: Optional[WeekdayEnum]
