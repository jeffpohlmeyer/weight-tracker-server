import uvicorn
from fastapi import FastAPI
from tortoise import Tortoise, run_async

from user.routes import user_router

app = FastAPI()
app.include_router(user_router)

TORTOISE_ORM = {
    "connections": {"default": "sqlite://sqlite3.db"},
    "apps": {
        "models": {
            "models": ["user.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}


async def init():
    await Tortoise.init(
        db_url="sqlite://sqlite3.db", modules={"models": ["user.models"]}
    )
    await Tortoise.generate_schemas()


@app.get("/")
def root():
    return {"hello": "world"}


if __name__ == "__main__":
    run_async(init())
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
