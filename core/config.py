from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    mongo_user: Optional[str] = Field(default=None, env="MONGO_USER")
    mongo_password: Optional[str] = Field(default=None, env="MONGO_PASSWORD")
    mongo_url: Optional[str] = Field(default=None, env="MONGO_ATLAS_URL")
    database: str = Field(..., env="DATABASE")
    secret: str = Field(..., env="SECRET")
    mail_user: Optional[str] = Field(default=None, env="MAIL_USER")
    mail_password: Optional[str] = Field(default=None, env="MAIL_PASSWORD")
    mail_from: str = Field(..., env="MAIL_FROM")
    mail_server: str = Field(..., env="MAIL_SERVER")
    mail_port: Optional[int] = Field(default=None, env="MAIL_PORT")
    mail_from_name: str = Field(..., env="MAIL_FROM_NAME")
    tls_port: int = Field(..., env="TLS_PORT")
    ssl_port: int = Field(..., env="SSL_PORT")
    send_secure: bool = Field(default=False, env="SEND_SECURE")
    site_url: Optional[str] = Field(default="example.com", env="SITE_URL")
    site_name: Optional[str] = Field(default="Example.com", env="SITE_NAME")
    client_url: Optional[str] = Field(
        default="http://www.example.com", env="CLIENT_URL"
    )

    def __init__(self):
        super(Settings, self).__init__()
        assert self.mongo_url is not None or (
            self.mongo_user is not None and self.mongo_password is not None
        )

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
