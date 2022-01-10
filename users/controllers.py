from fastapi import APIRouter, status, Request, Body, Depends, HTTPException

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTAuthentication
from fastapi_users.manager import InvalidVerifyToken
from fastapi_users.router import get_verify_router as base_verify_router
from fastapi_users.router.common import ErrorCode, ErrorModel

from core.config import get_settings

from users.models import User, UserCreate, UserDB, UserUpdate
from users.managers import get_user_manager  # , UserManager

settings = get_settings()

SECRET = settings.secret


jwt_authentication = JWTAuthentication(
    secret=SECRET, lifetime_seconds=3600, tokenUrl="auth/jwt/login"
)


# class FastAPIUsers(BaseUsers):
#     def base_verify_router(self):
#         return base_verify_router(self.get_user_manager, self._user_model)
#
#     def get_verify_router(self) -> APIRouter:
#         router = self.base_verify_router()
#
#         @router.post(
#             "/cancel-verify-request",
#             status_code=status.HTTP_204_NO_CONTENT,
#             name="verify:cancel-verify-request",
#             responses={
#                 status.HTTP_400_BAD_REQUEST: {
#                     "model": ErrorModel,
#                     "content": {
#                         "application/json": {
#                             "examples": {
#                                 ErrorCode.VERIFY_USER_BAD_TOKEN: {
#                                     "summary": "Bad token, not existing user or "
#                                     "not the e-mail currently set for the user.",
#                                     "value": {
#                                         "detail": ErrorCode.VERIFY_USER_BAD_TOKEN
#                                     },
#                                 }
#                             }
#                         }
#                     },
#                 }
#             },
#         )
#         async def cancel(
#             request: Request,
#             token: str = Body(..., embed=True),
#             user_manager: UserManager = Depends(get_user_manager),
#         ):
#             try:
#                 return await user_manager.cancel(token, request)
#             except InvalidVerifyToken:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail=ErrorCode.VERIFY_USER_BAD_TOKEN,
#                 )
#
#         return router


fastapi_users = FastAPIUsers(
    get_user_manager,
    [jwt_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_active_user = fastapi_users.current_user(active=True)
