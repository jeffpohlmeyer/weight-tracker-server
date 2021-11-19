from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class EmailBody(BaseModel):
    email: str


class BaseUser(EmailBody):
    name: str


class ExtendedUser(BaseUser):
    is_active: bool = False
    is_verified: bool = False
    token: Optional[str] = None
    token_expiration: Optional[datetime] = None
    is_superuser: bool = False


class UserInDB(ExtendedUser):
    hashed_password: str


class NewPassword(BaseModel):
    new_password: str
    new_password_confirm: str


class UserIn(BaseUser, NewPassword):
    pass


class PasswordChange(NewPassword):
    old_password: str


class VerificationToken(BaseModel):
    token: str


class VerificationTokenWithPassword(VerificationToken, NewPassword):
    pass
