from typing import Optional, List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

User = get_user_model()

env = settings.env

DOMAIN = env("DOMAIN")
PROTOCOL = env("PROTOCOL")
CONTACT_NAME_FROM = env("CONTACT_NAME_FROM")
CONTACT_EMAIL_FROM = env("CONTACT_EMAIL_FROM")


class Email:
    _message_item = None
    _subject = dict(
        registration="Confirm your new account!",
        registration_confirm="Your account has been confirmed!",
        password_forgot="Reset your password",
    )
    _msg_line_1 = dict(
        registration="You are receiving this message because this email address was used to register on our site.",
        registration_confirm="Thank you for confirming your email address and validating your account!",
        password_forgot="You are receiving this message because you have forgotten your password.",
    )
    _msg_line_2 = dict(
        registration="To verify your account with this email address please navigate",
        registration_confirm="",
        password_forgot="To reset your password please navigate",
    )
    _url_path = dict(
        registration="register/verify",
        registration_confirm="",
        password_forgot="password/forgot",
    )

    def __init__(self, user: User) -> None:
        self._user = user

        if DOMAIN is None:
            raise ImproperlyConfigured("DOMAIN is not set in .env file")
        if PROTOCOL is None:
            raise ImproperlyConfigured("PROTOCOL is not set in .env file")

    def _message_type(self) -> Optional[str]:
        if self._message_item in ["registration", "password_forgot"]:
            return "token"
        return None

    def _get_url_path(self) -> str:
        return self._url_path.get(self._message_item, "")

    def _get_subject(self) -> str:
        return self._subject.get(self._message_item, "")

    def _get_msg_line_1(self) -> str:
        return self._msg_line_1.get(self._message_item, "")

    def _get_msg_line_2(self) -> str:
        return self._msg_line_2.get(self._message_item, "")

    def _get_url(self) -> str:
        return f"{PROTOCOL}://{DOMAIN}/{self._url_path}/{self._token}"

    def _token(self) -> Optional[str]:
        return self._user.token

    def _token_expiration(self) -> Optional[str]:
        expiration = self._user().token_expiration
        if expiration is not None:
            return expiration.strftime("%m/%d/%Y, %H:%M:%S")
        return None

    def _get_token_expiration_string(self, html=False) -> str:
        expiration = ""
        if self._token_expiration() is not None:
            if not html:
                expiration = f"\nYour token expires at {self._token_expiration()}.\n"
            else:
                expiration = f"<p>Your token expires at {self._token_expiration()}.</p>"
        return expiration

    def _to_address(self) -> str:
        return self._user.email

    def _msg_text(self) -> str:
        message = ""

        if self._message_type == "token":
            message = f"""
                Hello from {DOMAIN}!

                {self._get_msg_line_1()}

                {self._get_msg_line_2()} to {self._get_url()}
                {self._get_token_expiration_string()}
                Regards,
                The team at {DOMAIN}.
            """
        return message

    def _msg_html(self) -> str:
        message = ""
        if self._message_type == "token":
            message = f"""
                <html>
                  <head></head>
                  <body>
                    <h3>Hello from {DOMAIN}!</h3>
                    <p>{self._get_msg_line_1()}</p>
                    <p>{self._get_msg_line_2()} <a href={self._get_url()} target="_blank">here</a>.</p>
                    <p>If the link doesn't work then copy and paste this link into your url bar {self._get_url()}</p>
                    {self._get_token_expiration_string(html=True)}
                    <br />
                    <p>Regards</p>
                    <p>The team at {DOMAIN}</p>
                  </body>
                </html>
            """
        return message

    def generate_messages(self) -> List[str]:
        if self._message_type is None:
            raise ImproperlyConfigured("The message type is not set.")
        text = self._msg_text()
        html = self._msg_html()

        return [text, html]

    def send_registration_email() -> None:
        send_message("registration")

    def send_registration_confirm_email():
        send_message("registration_confirm")

    def send_password_forgot_email():
        send_message("password_forgot")

    def send_password_change_confirm_email():
        send_message("password_change_confirm")

    def send_change_email_address():
        send_message("change_email_address")

    def send_change_email_address_confirm():
        send_message("change_email_address_confirm")

    def send_token_regeneration_email():
        send_message("token_regeneration")

    def send_message(message_name):
        print(f"sending email {message_name}")
