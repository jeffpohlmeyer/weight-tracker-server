import os
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication

from users.managers import get_user_manager
from users.models import User, UserCreate, UserUpdate, UserDB

load_dotenv()

SECRET = os.getenv("SECRET")
jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=3600, tokenUrl="auth/jwt/login"
)

app = FastAPI()
fast_api_users = FastAPIUsers(
    get_user_manager, [jwt_authentication], User, UserCreate, UserUpdate, UserDB
)
app.include_router(
    fast_api_users.get_auth_router(jwt_authentication, requires_verification=True),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(fast_api_users.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(fast_api_users.get_verify_router(), prefix="/auth", tags=["auth"])
app.include_router(
    fast_api_users.get_reset_password_router(), prefix="/auth", tags=["auth"]
)
app.include_router(
    fast_api_users.get_users_router(requires_verification=True),
    prefix="/users",
    tags=["users"],
)


@app.get("/")
async def root():
    return {"message": "Hello world"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
