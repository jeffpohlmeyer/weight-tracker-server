from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from core.config import get_settings

settings = get_settings()


def get_client() -> AsyncIOMotorClient:
    if settings.mongo_url is not None:
        database_url = settings.mongo_url
    else:
        database_url = f"mongodb://{settings.mongo_user}:{settings.mongo_password}@localhost:27017/"
    return AsyncIOMotorClient(database_url, uuidRepresentation="standard")


def get_db() -> AsyncIOMotorDatabase:
    client = get_client()
    return client[settings.database]
