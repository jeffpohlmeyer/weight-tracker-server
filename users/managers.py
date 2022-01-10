from datetime import date, datetime
from typing import Any, Dict, Literal, Optional

from dateutil.relativedelta import relativedelta
from fastapi import Depends, Request, HTTPException, status
from fastapi_users import BaseUserManager, models
from fastapi_users.db import MongoDBUserDatabase
from fastapi_users.jwt import generate_jwt
from fastapi_users.manager import (
    FastAPIUsersException,
    UserInactive,
    UserAlreadyVerified,
)

from core.config import get_settings

from users.emails import EmailClass
from users.models import get_user_db, UserCreate, UserDB
from utils.time_tracking import backfill_weeks

settings = get_settings()

SECRET = settings.secret

actions_types = Literal[
    "register",
    "confirmation",
    "password_reset",
    "password_reset_confirm",
    "email_changed",
    "email_changed_confirm",
    "password_changed",
    "request_verify",
    "set_up_initial_days",
]


class InvalidSetupException(FastAPIUsersException):
    pass


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    @staticmethod
    def get_action(user: UserDB, action: actions_types, token: Optional[str] = None):

        base_body = dict(
            user=user.email, site_url=settings.site_url, site_name=settings.site_name
        )
        if token is None:
            if action in [
                "register",
                "password_reset",
                "email_changed",
                "request_verify",
            ]:
                raise ValueError("Token can not be None")
        actions = dict(
            register=dict(
                subject="Account Created",
                template_str="user/activation/activation_email.html",
                body=dict(
                    **base_body,
                    activation_url=f"{settings.client_url}/register/confirm/{token}",
                ),
                email_to=user.email,
            ),
            confirmation=dict(
                subject="Email Verified",
                template_str="user/confirmation/confirmation_email.html",
                body=base_body,
                email_to=user.email,
            ),
            password_reset=dict(
                subject="Forgot Password",
                template_str="user/password_reset/password_reset.html",
                body=dict(
                    **base_body,
                    reset_url=f"{settings.client_url}/password/forgot/{token}",
                ),
                email_to=user.email,
            ),
            password_reset_confirm=dict(
                subject="Password Reset",
                template_str="user/password_changed/password_changed.html",
                body=base_body,
                email_to=user.email,
            ),
            email_changed=dict(
                subject="Email Changed",
                template_str="user/email_changed/email_changed.html",
                body=dict(
                    **base_body,
                    activation_url=f"{settings.client_url}/email/changed/{token}",
                ),
                email_to=user.email,
            ),
            email_changed_confirm=dict(
                subject="Email Updated",
                template_str="user/email_changed_confirm/email_changed_confirm.html",
                body=base_body,
                email_to=user.email,
            ),
            password_changed=dict(
                subject="Password Changed",
                template_str="user/password_changed/password_changed.html",
                body=base_body,
                email_to=user.email,
            ),
            request_verify=dict(
                subject="Verification Token Requested",
                template_str="user/request_verify/request_verify.html",
                body=dict(
                    **base_body,
                    activation_url=f"{settings.client_url}/request/verify/{token}",
                ),
                email_to=user.email,
            ),
        )
        return actions[action]

    async def update(
        self,
        user_update: models.UU,
        user: models.UD,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> models.UD:
        """
        Update a user.

        Triggers the on_after_update handler on success

        :param user_update: The UserUpdate model containing
        the changes to apply to the user.
        :param user: The current user to update.
        :param safe: If True, sensitive values like is_superuser or is_verified
        will be ignored during the update, defaults to False
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :return: The updated user.
        """
        if safe:
            updated_user_data = user_update.create_update_dict()
        else:
            updated_user_data = user_update.create_update_dict_superuser()
        action = None
        if "birth_date" in updated_user_data.keys():
            updated_user_data["birth_date"] = datetime.combine(
                updated_user_data["birth_date"], datetime.min.time()
            )
            updated_user_data["age"] = relativedelta(
                datetime.today(), updated_user_data["birth_date"]
            ).years
        if not user.has_been_updated:
            initial_keys = ["weight", "height", "sex", "birth_date", "weekly_points"]
            for key in initial_keys:
                if updated_user_data.get(key) is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Weight, height, sex, birth date, weekly points must all be included initial setup.",
                    )
            if "weigh_in_day" in updated_user_data.keys():
                del updated_user_data["weigh_in_day"]
            updated_user_data["has_been_updated"] = True
            action = "set_up_initial_days"
        updated_user = await self._update(user, updated_user_data)
        await self.on_after_update(updated_user, updated_user_data, request, action)
        return updated_user

    async def request_verify(
        self,
        user: models.UD,
        request: Optional[Request] = None,
        action: Optional[actions_types] = None,
    ) -> None:
        """
        *** THIS IS A SLIGHTLY MODIFIED OVERRIDDEN BUILT-IN METHOD ***

        Start a verification request.

        Triggers the on_after_request_verify handler on success.

        :param user: The user to verify.
        :param request: Optional FastAPI request that
        triggered the operation, defaults to None.
        :param action: Optional parameter for overridden
        implementation to handle email
        :raises UserInactive: The user is inactive.
        :raises UserAlreadyVerified: The user is already verified.
        """
        if not user.is_active:
            raise UserInactive()
        if user.is_verified:
            raise UserAlreadyVerified()

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
        await self.on_after_request_verify(user, token, request, action)

    async def on_after_update(
        self,
        user: models.UD,
        update_dict: Dict[str, Any],
        request: Optional[Request] = None,
        action: Optional[actions_types] = None,
    ) -> None:
        print("action", action)
        if "password" in update_dict.keys():
            await EmailClass(**self.get_action(user, "password_changed")).send_email()
        if "email" in update_dict.keys():
            await self.request_verify(user, action="email_changed")
        if action == "set_up_initial_days":
            await backfill_weeks(user)

    async def on_after_register(self, user: UserDB, request: Optional[Request] = None):
        await self.request_verify(user, action="register")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        await EmailClass(**self.get_action(user, "password_reset", token)).send_email()

    async def on_after_reset_password(
        self, user: models.UD, request: Optional[Request] = None
    ) -> None:
        await EmailClass(**self.get_action(user, "password_reset_confirm")).send_email()

    async def on_after_request_verify(
        self,
        user: UserDB,
        token: str,
        request: Optional[Request] = None,
        action: Optional[actions_types] = None,
    ):
        if action is not None:
            await EmailClass(**self.get_action(user, action, token)).send_email()
        else:
            await EmailClass(
                **self.get_action(user, "request_verify", token)
            ).send_email()
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_verify(
        self,
        user: models.UD,
        request: Optional[Request] = None,
    ) -> None:
        await EmailClass(**self.get_action(user, "confirmation")).send_email()
        await self._update(user, {"weigh_in_day": date.today().weekday()})


async def get_user_manager(user_db: MongoDBUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
