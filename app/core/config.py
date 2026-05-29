from pydantic_settings import BaseSettings,SettingsConfigDict
import secrets
import os

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///:memory:"
    JWT_SECRET_KEY: str = secrets.token_urlsafe(64)
    JWT_ALGORITHM: str = "HS256"
    model_config = SettingsConfigDict(env_file=".env")
    REDIS_URL: str = "redis://redis:6379"
    UPLOAD_DIR:str = os.getenv("UPLOAD_DIR", "static/parasha_images")
    UPLOAD_URL_PREFIX:str = os.getenv("UPLOAD_URL_PREFIX", "/static/parasha_images")


settings = Settings()