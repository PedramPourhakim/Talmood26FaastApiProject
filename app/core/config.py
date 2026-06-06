from pydantic_settings import BaseSettings,SettingsConfigDict
import secrets
import os

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///:memory:"
    JWT_SECRET_KEY: str = secrets.token_urlsafe(64)
    JWT_ALGORITHM: str
    REDIS_URL: str
    UPLOAD_DIR:str = os.getenv("UPLOAD_DIR", "static/parasha_images")
    UPLOAD_URL_PREFIX:str = os.getenv("UPLOAD_URL_PREFIX", "/static/parasha_images")

    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_FROM : str
    MAIL_PORT : int
    MAIL_SERVER : str
    MAIL_FROM_NAME : str
    MAIL_STARTTLS : bool = True
    MAIL_SSL_TLS : bool = False
    USE_CREDENTIALS : bool = True
    VALIDATE_CERTS : bool = True

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()