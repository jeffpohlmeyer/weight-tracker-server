import os
from dotenv import load_dotenv

import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid

from typing import Optional, List

from fastapi import Depends, Request, BackgroundTasks
from fastapi_users import BaseUserManager
from fastapi_users.jwt import generate_jwt
from starlette.requests import Request
from pydantic import BaseModel, EmailStr

from .db import get_user_db
from .models import UserCreate, UserDB

load_dotenv()
SECRET = os.getenv("SECRET")
PROTOCOL = os.getenv("PROTOCOL", default="http")
DOMAIN = os.getenv("DOMAIN", default="example.com")
RAW_DEBUG = os.getenv("DEBUG", default=True)

try:
    DEBUG = int(RAW_DEBUG) == 1
except ValueError:
    DEBUG = False


class EmailPayload(BaseModel):
    subject: str
    to_name: Optional[str]
    to_email: EmailStr
    msg_line_1: str
    msg_line_2: str
    token: str


async def make_email(payload: EmailPayload):
    msg = EmailMessage()
    msg["Subject"] = payload.subject
    sender = os.getenv("CONTACT_NAME_FROM")
    [sender_username, sender_domain] = os.getenv("CONTACT_EMAIL_FROM").split("@")
    [to_username, to_domain] = payload.to_email.split("@")
    msg["From"] = Address(sender, sender_username, sender_domain)
    if payload.to_name is not None:
        msg["To"] = Address(payload.to_name, to_username, to_domain)
    else:
        msg["To"] = Address(payload.to_email, to_username, to_domain)

    url = f"{os.getenv('PROTOCOL')}://{DOMAIN}/register/verify/{payload.token}"

    msg_text = f"""
    Hello from {DOMAIN}!

    {payload.msg_line_1}

    {payload.msg_line_2} to {url}

    Regards,
    The team at {DOMAIN}.
    """

    msg.set_content(msg_text)

    msg_html = f"""
        <html>
        <head></head>
        <body>
        <h3>Hello from {DOMAIN}!</h3>
        <p>{payload.msg_line_1}</p>
        <p>{payload.msg_line_2} <a href="{url}" target="_blank">here</a>.</p>
        <p>If the link doesn't work then copy and paste this link into your url bar {url}
        <br />
        <p>Regards,</p>
        <p>The team at {DOMAIN}</p>
        </body>
        </html>
    """
    msg.add_alternative(
        msg_html,
        subtype="html",
    )

    if DEBUG:
        print(msg)
    else:
        with smtplib.SMTP(os.getenv("EMAIL_SERVER"), os.getenv("EMAIL_PORT")) as s:
            s.login(
                os.getenv("CONTACT_EMAIL_FROM"), os.getenv("CONTACT_EMAIL_PASSWORD")
            )
            s.send_message(msg)


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: UserDB, request: Optional[Request] = None
    ) -> None:
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )

        msg_line_1 = "You are receiving this message because this email address was used to register on our site."
        msg_line_2 = "To verify your account with this email address please navigate"

        await make_email(
            EmailPayload(
                subject="Verify your email address!",
                to_email=user.email,
                msg_line_1=msg_line_1,
                msg_line_2=msg_line_2,
                token=token,
            )
        )
        print(f"User {user.id} has registered")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ) -> None:
        msg_line_1 = (
            "You are receiving this message because you have forgotten your password."
        )
        msg_line_2 = "To reset your password please navigate"

        await make_email(
            EmailPayload(
                subject="Verify your email address!",
                to_email=user.email,
                msg_line_1=msg_line_1,
                msg_line_2=msg_line_2,
                token=token,
            )
        )
        print(f"User {user.id} has forgotten their password.  Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ) -> None:
        msg_line_1 = "You are receiving this message because you have requested a new verification token be generated."
        msg_line_2 = "To verify your account with this email address please navigate"

        await make_email(
            EmailPayload(
                subject="Verify your email address!",
                to_email=user.email,
                msg_line_1=msg_line_1,
                msg_line_2=msg_line_2,
                token=token,
            )
        )
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
