from fastapi import APIRouter, Depends
from users.controllers import fastapi_users, jwt_authentication, current_active_user
from users.models import UserDB

from time_tracking.models import Week


auth_router = APIRouter(prefix="/auth", tags=["auth"])


auth_router.include_router(
    fastapi_users.get_auth_router(jwt_authentication, requires_verification=True),
    prefix="/jwt",
)
auth_router.include_router(fastapi_users.get_register_router(), prefix="")
auth_router.include_router(fastapi_users.get_reset_password_router(), prefix="")
auth_router.include_router(fastapi_users.get_verify_router(), prefix="")

user_router = APIRouter(prefix="/users", tags=["users"])
user_router.include_router(fastapi_users.get_users_router(), prefix="")


@user_router.get("/weeks")
async def get_all_weeks(user: UserDB = Depends(current_active_user)) -> list[Week]:
    weeks = await Week.find({"user": user.id}).to_list()
    return weeks
