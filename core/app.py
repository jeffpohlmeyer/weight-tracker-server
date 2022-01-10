from beanie import init_beanie
from fastapi import Depends, FastAPI

from core.config import get_settings
from core.db import get_db

from time_tracking.models import Week, Day
from time_tracking.routes import week_router, day_router
from users.controllers import current_active_user
from users.models import UserDB
from users.router import auth_router, user_router

settings = get_settings()


app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(week_router)
app.include_router(day_router)


@app.get("/")
async def root():
    return {
        "user": settings.mongo_user,
        "password": settings.mongo_password,
        "database": settings.database,
        "secret": settings.secret,
    }


@app.get("/authenticated-route")
async def authenticated_route(user: UserDB = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def app_init():
    """Initialize application services"""
    await init_beanie(get_db(), document_models=[Week, Day])
