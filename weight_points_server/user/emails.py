from typing import Optional, List

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ImproperlyConfigured
from django.views.generic.base import ContextMixin

DOMAIN = settings.DOMAIN
PROTOCOL = settings.PROTOCOL
CONTACT_NAME_FROM = settings.CONTACT_NAME_FROM
CONTACT_EMAIL_FROM = settings.CONTACT_EMAIL_FROM


class Email(EmailMultiAlternatives, ContextMixin):
    _message_item = None
    _subject = dict(
        registration="Confirm your new account!",
        registration_confirm="Your email has been confirmed!",
        password_forgot="Reset your password",
        password_change_confirm="Your password has changed",
        change_email="Change your email",
        change_email_confirm="Your email has changed",
    )
    _msg_line_1 = dict(
        registration="You are receiving this message because this email address was used to register on our site.",
        registration_confirm="Thank you for confirming your email address and validating your account!",
        password_forgot="You are receiving this message because you have forgotten your password.",
        password_change_confirm="You are receiving this message because your password has just been changed.",
        change_email="You are receiving this message because this address has been listed as a new possible login "
        "email.",
        change_email_confirm="You are receiving this message because the email you use to log in has changed.",
    )
    _msg_line_2 = dict(
        registration="To verify your account with this email address please navigate",
        registration_confirm="You should now be able to log in.",
        password_forgot="To reset your password please navigate",
        password_change_confirm="If you did not do this then reset your password.",
        change_email="To confirm this email address please navigate",
        change_email_confirm="If this was done in error please navigate",
    )
    _url_path = dict(
        registration="register/verify",
        registration_confirm="",
        password_forgot="password/forgot",
        password_change_confirm="",
        change_email="email/change",
        change_email_confirm="email/change/undo",
    )

    def __init__(self, user, *args, **kwargs) -> None:
        super(Email, self).__init__(*args, **kwargs)
        self._user = user
        self._message_item = user.message_type

        if DOMAIN is None:
            raise ImproperlyConfigured("DOMAIN is not set in .env file")
        if PROTOCOL is None:
            raise ImproperlyConfigured("PROTOCOL is not set in .env file")

    def _message_type(self) -> Optional[str]:
        if self._message_item in ["registration", "password_forgot", "email_change"]:
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
        if self._message_item == "change_email_confirm":
            return self._user.old_email
        return self._user.email

    def _msg_text(self) -> str:
        if self._message_type == "token":
            return f"""
                Hello from {DOMAIN}!

                {self._get_msg_line_1()}

                {self._get_msg_line_2()} to {self._get_url()}
                {self._get_token_expiration_string()}
                Regards,
                The team at {DOMAIN}.
            """
        else:
            return f"""
                Hello from {DOMAIN}!

                {self._get_msg_line_1()}

                {self._get_msg_line_2()}
                Regards,
                The team at {DOMAIN}.
            """

    def _msg_html(self) -> str:
        if self._message_type == "token":
            return f"""
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
        else:
            return f"""
                <html>
                  <head></head>
                  <body>
                    <h3>Hello from {DOMAIN}!</h3>
                    <p>{self._get_msg_line_1()}</p>
                    <p>{self._get_msg_line_2()}</p>
                    <br />
                    <p>Regards</p>
                    <p>The team at {DOMAIN}</p>
                  </body>
                </html>
            """

    def generate_messages(self) -> List[str]:
        if self._message_type is None:
            raise ImproperlyConfigured("The message type is not set.")
        text = self._msg_text()
        html = self._msg_html()

        return [text, html]

    def send_message(self):
        print(f"sending email {self._message_item}")
