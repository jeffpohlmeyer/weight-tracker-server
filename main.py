import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from db import TORTOISE_ORM

from user.routes import user_router

app = FastAPI()
app.include_router(user_router)


@app.get("/")
def root():
    return {"hello": "world"}


register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
