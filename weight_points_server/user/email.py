from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.views.generic.base import ContextMixin
from djoser import utils
from djoser.conf import settings as djoser_settings

SITE_NAME = settings.SITE_NAME
DOMAIN = settings.DOMAIN
URL = settings.SITE_URL


def get_uid_and_token(context):
    user = context.get("user")
    uid = utils.encode_uid(user.pk)
    token = default_token_generator.make_token(user)

    return uid, token


class CustomBaseEmail(EmailMultiAlternatives, ContextMixin):
    template_name = None
    template_name_txt = None
    text_content = None
    html_content = None
    email_subject = None

    def __init__(
        self,
        request=None,
        context=None,
        template_name=None,
        template_name_txt=None,
        *args,
        **kwargs,
    ):
        super(CustomBaseEmail, self).__init__(*args, **kwargs)

        self.request = request
        self.context = {} if context is None else context
        if template_name is not None:
            self.template_name = template_name
        if template_name_txt is not None:
            self.template_name_txt = template_name_txt
        self.subject = self.email_subject

    def get_context_data(self, **kwargs):
        self.context["site_name"] = SITE_NAME
        self.context["site_url"] = URL
        return self.context

    def send(self, to, *args, **kwargs):
        self.to = to
        self.cc = kwargs.pop("cc", [])
        self.bcc = kwargs.pop("bcc", [])
        self.reply_to = kwargs.pop("reply_to", [])
        self.from_email = kwargs.pop("from_email", djoser_settings.DEFAULT_FROM_EMAIL)
        context = self.get_context_data()
        plaintext = get_template(self.template_name_txt)
        htmly = get_template(self.template_name)

        self.body = plaintext.render(context)
        html_content = htmly.render(context)
        super(CustomBaseEmail, self).attach_alternative(html_content, "text/html")
        super(CustomBaseEmail, self).send(*args, **kwargs)


class CustomActivationEmail(CustomBaseEmail):
    template_name = "user/activation/activation_email.html"
    template_name_txt = "user/activation/activation_email.txt"
    email_subject = f"{SITE_NAME} - Account Activation Required"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        uid, token = get_uid_and_token(context)
        url = djoser_settings.ACTIVATION_URL.format(uid=uid, token=token)
        context["activation_url"] = f"{URL}/{url}"
        return context


class CustomConfirmationEmail(CustomBaseEmail):
    template_name = "user/confirmation/confirmation_email.html"
    template_name_txt = "user/confirmation/confirmation_email.txt"
    email_subject = f"{SITE_NAME} - Account Activated"


class CustomPasswordResetEmail(CustomBaseEmail):
    template_name = "user/password_reset/password_reset_email.html"
    template_name_txt = "user/password_reset/password_reset_email.txt"
    email_subject = f"{SITE_NAME} - Password Reset"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        uid, token = get_uid_and_token(context)
        url = djoser_settings.PASSWORD_RESET_CONFIRM_URL.format(uid=uid, token=token)
        context["reset_url"] = f"{URL}/{url}"
        return context


class CustomPasswordChangedConfirmationEmail(CustomBaseEmail):
    template_name = "user/password_changed/password_changed_email.html"
    template_name_txt = "user/password_changed/password_changed_email.txt"
    email_subject = f"{SITE_NAME} - Password Changed"


class CustomUsernameChangedConfirmationEmail(CustomBaseEmail):
    template_name = "user/username_changed/username_changed_email.html"
    template_name_txt = "user/username_changed/username_changed_email.txt"
    email_subject = f"{SITE_NAME} - Username Changed"


class CustomUsernameResetEmail(CustomBaseEmail):
    template_name = "user/username_reset/username_reset_email.html"
    template_name_txt = "user/username_reset/username_reset_email.txt"
    email_subject = f"{SITE_NAME} - Reset Username"

    def get_context_data(self):
        context = super().get_context_data()

        uid, token = get_uid_and_token(context)
        url = djoser_settings.USERNAME_RESET_CONFIRM_URL.format(uid=uid, token=token)
        context["reset_url"] = f"{URL}/{url}"
        return context
