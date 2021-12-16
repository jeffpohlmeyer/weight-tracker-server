from typing import TypedDict
from datetime import timedelta, datetime as dt
import secrets

from django.utils import timezone


class TokenAndExpiration(TypedDict):
    token: str
    token_expiration: dt


def create_token(n_bytes: int = 64) -> str:
    return secrets.token_urlsafe(n_bytes)


def create_token_expiration(minutes: int = 60) -> dt:
    return timezone.now() + timedelta(minutes=minutes)


def create_token_and_expiration(
    n_bytes: int = 64, minutes: int = 60
) -> TokenAndExpiration:
    return dict(
        token=create_token(n_bytes),
        token_expiration=create_token_expiration(minutes),
    )
