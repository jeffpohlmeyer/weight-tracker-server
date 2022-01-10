from pathlib import Path
from smtplib import SMTP
from typing import Optional

from fastapi import BackgroundTasks
from jinja2 import Environment, FileSystemLoader

from core.config import get_settings

from email.message import EmailMessage
from email.headerregistry import Address


settings = get_settings()


class EmailClass:
    def __init__(self, subject: str, email_to: str, body: dict, template_str: str):
        self.conf = dict(
            MAIL_USERNAME=settings.mail_user,
            MAIL_PASSWORD=settings.mail_password,
            MAIL_FROM=settings.mail_from,
            MAIL_SERVER=settings.mail_server,
            MAIL_PORT=settings.mail_port,
            MAIL_FROM_NAME=settings.mail_from_name,
            MAIL_TLS=True,
            MAIL_SSL=False,
            TLS_PORT=settings.tls_port,
            SSL_PORT=settings.ssl_port,
            USE_CREDENTIALS=True,
            TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
            SEND_SECURE=settings.send_secure,
        )
        env = Environment(loader=FileSystemLoader(str(self.conf["TEMPLATE_FOLDER"])))
        template = env.get_template(template_str)
        sender = self.conf["MAIL_FROM"].split("@")
        receiver = email_to.split("@")
        self.msg = EmailMessage()
        self.msg["Subject"] = subject
        self.msg["From"] = Address(
            display_name=self.conf["MAIL_FROM_NAME"],
            username=sender[0],
            domain=sender[1],
        )
        self.msg["To"] = Address(
            display_name="blah blah user", username=receiver[0], domain=receiver[1]
        )
        self.msg.add_alternative(template.render(**body), subtype="html")
        if self.conf["SEND_SECURE"]:
            self.PORT = (
                settings.tls_port if self.conf["MAIL_TLS"] else settings.ssl_port
            )
        else:
            self.PORT = self.conf["MAIL_PORT"]
        self.SERVER = f'{self.conf["MAIL_SERVER"]}:{self.PORT}'

    async def send_email(self):
        with SMTP(self.SERVER) as s:
            if self.conf["SEND_SECURE"]:
                if self.conf["MAIL_TLS"]:
                    s.starttls()
                s.login(self.conf["MAIL_USERNAME"], self.conf["MAIL_PASSWORD"])
            s.send_message(self.msg)
