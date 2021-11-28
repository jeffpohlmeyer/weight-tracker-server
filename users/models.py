from typing import Optional
from fastapi_users import models
from fastapi_users.db import TortoiseBaseUserModel
from tortoise.contrib.pydantic import PydanticModel

from common.models import SexEnum, WeekdayEnum


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


class UserModel(TortoiseBaseUserModel):
    name: Optional[str]
    weight: Optional[float]
    height: Optional[int]
    sex: Optional[SexEnum]
    weigh_in_day: Optional[WeekdayEnum]


class UserDB(User, models.BaseUserDB, PydanticModel):
    class Config:
        orm_mode = True
        orig_model = UserModel
