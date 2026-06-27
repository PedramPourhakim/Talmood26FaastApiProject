from pydantic_settings import BaseSettings,SettingsConfigDict
import secrets
import os
import uuid
from zarinpal_utils.Config import Config


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
    MERCHANT_ID : str = uuid.uuid4()
    SAND_BOX : bool
    ZARIN_PAL_ACCESS_TOKEN : str
    ZARIN_PAL_CALLBACK_URL : str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

zarinpal_config = Config(
    merchant_id=settings.MERCHANT_ID,
    access_token=settings.ZARIN_PAL_ACCESS_TOKEN,
    sandbox=settings.SAND_BOX,
)