from sqlalchemy import Column, Integer, Float, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship
from common.db import Base
from fastapi_users_db_sqlalchemy import GUID
from common.models import WeekdayEnum


class WeekTable(Base):
    __tablename__ = "week"

    id = Column(Integer, primary_key=True)
    total_points = Column(Integer)
    points_remaining = Column(Integer)
    weight = Column(Float)
    user_id = Column(GUID, ForeignKey("user.id"))
    user = relationship("UserTable", back_populates="week")


class DayTable(Base):
    __tablename__ = "day"

    id = Column(Integer, primary_key=True)
    total_points = Column(Integer)
    points_remaining = Column(Integer)
    points_used = Column(Integer)
    activity_points = Column(Integer)
    day_of_week = Column(Enum(WeekdayEnum))
    date = Column(Date)
    week_id = Column(Integer, ForeignKey("week.id"))
    week = relationship("WeekTable", back_populates="day")
    user_id = Column(GUID, ForeignKey("user.id"))
    user = relationship("UserTable", back_populates="day")
