from pydantic import BaseSettings


class Settings(BaseSettings):
    app_url: str
    pocketbase_url: str
    redis_url: str = None
    allow_plugins: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
