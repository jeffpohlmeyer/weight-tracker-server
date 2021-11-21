import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid

from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager

from .db import get_user_db
from .models import UserCreate, UserDB


load_dotenv()
SECRET = os.getenv("SECRET")


async def make_email():
    msg = EmailMessage()
    msg["Subject"] = "Hello world"
    msg["From"] = Address("Blah", "mail", "example.com")
    msg["To"] = Address("Hello world", "hello", "world.com")
    msg.set_content(
        """
        Salut!
    
        Cela ressemble à un excellent recipie[1] déjeuner.
    
        [1] http://www.yummly.com/recipe/Roasted-Asparagus-Epicurious-203718
    
        --Pepé
    """
    )
    asparagus_cid = make_msgid()
    msg.add_alternative(
        """\
    <html>
      <head></head>
      <body>
        <p>Salut!</p>
        <p>Cela ressemble à un excellent
            <a href="http://www.yummly.com/recipe/Roasted-Asparagus-Epicurious-203718">
                recipie
            </a> déjeuner.
        </p>
        <img src="cid:{asparagus_cid}" />
      </body>
    </html>
    """.format(
            asparagus_cid=asparagus_cid[1:-1]
        ),
        subtype="html",
    )

    with open("outgoing.msg", "wb") as f:
        f.write(bytes(msg))

    with smtplib.SMTP("smtp.titan.email", 465) as s:
        await s.login("contact-form@jvp.design", "qdD7UzwadGmgFeZZBcj8kye8YQhuRg7i")
        await s.send_message(msg)


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(
        self, user: UserDB, request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has registered")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"User {user.id} has forgotten their password.  Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ) -> None:
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
