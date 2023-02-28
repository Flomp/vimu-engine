import os

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_url: str
    pocketbase_url: str
    pocketbase_admin_email: str
    pocketbase_admin_password: str
    stripe_api_key: str = None
    stripe_webhook_secret: str = None
    redis_url: str = None

    class Config:
        env_file = ".env"


settings = Settings()
