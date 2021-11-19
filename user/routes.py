from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .models import User

from .schemas import (
    Token,
    UserIn,
    UserInDB,
    PasswordChange,
    VerificationToken,
    VerificationTokenWithPassword,
    EmailBody,
)
from .utils import (
    authenticate_user,
    get_access_token,
    get_current_active_user,
    verify_password,
    validate_password,
    create_email_token,
    get_password_hash,
)
from utils.validators import validate_email


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def register_user(form_data: UserIn):
    if not form_data.new_password == form_data.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords must match"
        )
    if not validate_email(form_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter a valid email address",
        )
    if await User.exists(email=form_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists",
        )
    hashed_password = get_password_hash(form_data.new_password)
    await User.create(
        email=form_data.email,
        name=form_data.name,
        hashed_password=hashed_password,
        is_active=True,
        **create_email_token()
    )
    return dict(detail="Success.  Please check your email for a verification link.")


@user_router.post("/token/verify/", response_model=Token)
async def verify_registration_token(body: VerificationToken):
    user = await User.get_or_none(token=body.token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
    expiration = user.token_expiration
    if expiration is None or (expiration < datetime.utcnow().timestamp()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired"
        )

    user.token = None
    user.token_expiration = None
    user.is_verified = True
    await user.save()

    return dict(access_token=get_access_token(user.email), token_type="bearer")


@user_router.post("/token/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not verified.  Please click the link in your email",
        )
    if not user.is_active:
        await User.filter(email=user.email).update(is_active=True)
    access_token = get_access_token(user.email)
    return dict(access_token=access_token, token_type="bearer")


@user_router.post("/password/change/", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: PasswordChange,
    user: UserInDB = Depends(get_current_active_user),
):
    if not verify_password(body.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your old password is incorrect",
        )
    if not validate_password(body.new_password, body.new_password_confirm):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords must match"
        )
    await User.filter(email=user.email).update(
        hashed_password=get_password_hash(body.new_password)
    )


@user_router.post("/password/forgot/", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(body: EmailBody):
    if not validate_email(body.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid emailn"
        )
    await User.filter(email=body.email).update(**create_email_token())


@user_router.post("/password/forgot/confirm/", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password_confirm(body: VerificationTokenWithPassword):
    if not validate_password(body.new_password, body.new_password_confirm):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords must match"
        )

    user = await User.get_or_none(token=body.token)
    if not user or (user.token_expiration < datetime.utcnow().timestamp()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    user.hashed_password = get_password_hash(body.new_password)
    user.token = None
    user.token_expiration = None
    await user.save()


@user_router.post("/token/regenerate/", status_code=status.HTTP_204_NO_CONTENT)
async def regenerate_token(body: EmailBody):
    await User.filter(email=body.email).update(**create_email_token())
