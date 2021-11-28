import os
from dotenv import load_dotenv
import databases
import sqlalchemy
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base


load_dotenv()

DATABASE_URL = os.getenv("FASTAPI_DATABASE_URL")
if DATABASE_URL is None:
    DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)
Base: DeclarativeMeta = declarative_base()

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
