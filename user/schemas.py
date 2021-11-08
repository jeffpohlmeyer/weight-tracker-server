from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    email: str
    name: str
    is_active: bool = False
    is_verified: bool = False
    token: Optional[str] = None
    token_expiration: Optional[datetime] = None
    is_superuser: bool = False


class UserInDB(User):
    hashed_password: str


class UserRegister(BaseModel):
    email: str
    name: str
    password: str
    password_confirm: str
