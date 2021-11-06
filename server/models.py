import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Enum
from sqlalchemy.orm import relationship

from server.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Set a one-to-one relationship with profile
    profile = relationship("Profile", back_populates="user", uselist=False)


class SexEnum(enum.Enum):
    male = "M"
    female = "F"


class Profile(Base):
    __tablename__ = "profile"
    id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float)
    height = Column(Integer)
    sex = Column(Enum(SexEnum))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="items")
