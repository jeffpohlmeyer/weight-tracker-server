from tortoise import Tortoise, run_async

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
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


if __name__ == "__main__":
    run_async(init())
