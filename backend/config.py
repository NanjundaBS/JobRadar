from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://jobradar:jobradar@localhost:5432/jobradar"

    # Gmail OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REFRESH_TOKEN: str = ""

    # Email
    EMAIL_TO: str = "nanjundabsom@gmail.com"
    EMAIL_FROM: str = "nanjundabsom@gmail.com"

    # App
    APP_SECRET_KEY: str = "change-me-in-production"
    LOG_LEVEL: str = "INFO"
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
