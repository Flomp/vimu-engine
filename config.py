from pydantic import BaseSettings


class Settings(BaseSettings):
    app_url: str
    redis_url: str = None

    class Config:
        env_file = ".env"


settings = Settings()
