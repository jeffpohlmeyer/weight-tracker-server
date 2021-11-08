from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .schemas import Token, User, UserRegister
from .utils import (
    authenticate_user,
    get_access_token,
    get_current_active_user,
    create_user,
)


user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/register/", response_model=Token)
async def register_user(form_data: UserRegister):
    return await create_user(form_data)


@user_router.post("/token/", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = get_access_token(user)
    return dict(access_token=access_token, token_type="bearer")


@user_router.get("/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
