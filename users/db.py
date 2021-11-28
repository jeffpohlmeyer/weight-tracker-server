from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase

from common.db import Base, database
from .models import UserDB, SexEnum, WeekdayEnum


class UserTable(Base, SQLAlchemyBaseUserTable):
    name = Column(String)
    weight = Column(Integer)
    height = Column(Integer)
    sex = Column(Enum(SexEnum))
    weigh_in_day = Column(Enum(WeekdayEnum))
    week = relationship("WeekTable", back_populates="user")
    day = relationship("DayTable", back_populates="user")


users = UserTable.__table__


async def get_user_db():
    yield SQLAlchemyUserDatabase(UserDB, database, users)
