from pydantic_settings import BaseSettings,SettingsConfigDict
import secrets
import os

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///:memory:"
    JWT_SECRET_KEY: str = secrets.token_urlsafe(64)
    JWT_ALGORITHM: str = "HS256"
    REDIS_URL: str = "redis://redis:6379"
    UPLOAD_DIR:str = os.getenv("UPLOAD_DIR", "static/parasha_images")
    UPLOAD_URL_PREFIX:str = os.getenv("UPLOAD_URL_PREFIX", "/static/parasha_images")

    MAIL_USERNAME : str = ""
    MAIL_PASSWORD : str = ""
    MAIL_FROM : str = "no-reply@example.com"
    MAIL_PORT : int = 25
    MAIL_SERVER : str = "smtp4dev"
    MAIL_FROM_NAME : str = "Talmood26"
    MAIL_STARTTLS : bool = False
    MAIL_SSL_TLS : bool = False
    USE_CREDENTIALS : bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()