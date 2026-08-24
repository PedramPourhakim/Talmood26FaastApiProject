from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi_swagger import patch_fastapi
from app.qa.view import QAView
from app.utils.exception_handler import (HttpExceptionHandler,
                                     ValidationExceptionHandler)
from app.utils.Auth_Middleware import RefreshTokenMiddleware,AdminAuth,SwaggerMiddleware
from app.person.routes import router as person_router
from app.weeklyParashah.routes import router as parasha_router
from app.templates.rendering_pages import router as index_page_router
from app.users.routes import router as users_router
from app.qa.routes import router as qa_router
from app.paymentType.routes import router as paymentType_router
from app.payment.routes import router as payment_router
from sqladmin import Admin
from app.core.database import engine
from app.person.view import PersonView
from app.weeklyParashah.view import ParashaView
from app.users.view import UserView
from app.paymentType.view import PaymentTypeView
from app.paymentAccount.view import PaymentAccountView
from app.payment.view import PaymentView
from fastapi.staticfiles import StaticFiles
from sqlalchemy_file.storage import StorageManager
from libcloud.storage.drivers.local import LocalStorageDriver
import os
from app.core.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
from app.core.redis import redis
import asyncio
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from pathlib import Path
# app = FastAPI(docs_url=None,
#     swagger_ui_oauth2_redirect_url=None)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

PERSON_IMAGES_DIR = STATIC_DIR / "person_images"
PARASHA_IMAGES_DIR = STATIC_DIR / "parasha_images"

PERSON_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
PARASHA_IMAGES_DIR.mkdir(parents=True, exist_ok=True)


person_container = LocalStorageDriver(
    str(STATIC_DIR)
).get_container("person_images")

parasha_container = LocalStorageDriver(
    str(STATIC_DIR)
).get_container("parasha_images")


StorageManager.add_storage(
    "person_storage",
    person_container
)

StorageManager.add_storage(
    "parasha_storage",
    parasha_container
)


default_container = LocalStorageDriver(
    str(STATIC_DIR)
).get_container(".")

StorageManager.add_storage(
    "default",
    default_container
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(
        RedisBackend(redis),
        prefix="fastapi-cache"
    )

    yield

    await redis.close()
app = FastAPI(lifespan=lifespan, docs_url="/swagger", redoc_url=None)


UPLOAD_DIR = PARASHA_IMAGES_DIR
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static"
)

app.mount(
    "/data",
    StaticFiles(directory=str(STATIC_DIR / "data")),
    name="data"
)

admin = Admin(app,engine,
    authentication_backend=AdminAuth(
        secret_key=settings.JWT_SECRET_KEY
    ))
# admin = Admin(app,engine)
admin.add_view(PersonView)
admin.add_view(ParashaView)
admin.add_view(UserView)
admin.add_view(QAView)
admin.add_view(PaymentTypeView)
admin.add_view(PaymentAccountView)
admin.add_view(PaymentView)

# patch_fastapi(app,docs_url="/swagger")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return HttpExceptionHandler().handle_exception(exc)

@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc):
    return ValidationExceptionHandler().handle_exception(exc)

app.include_router(person_router)
app.include_router(parasha_router)
app.include_router(users_router)
app.include_router(qa_router)
app.include_router(index_page_router)
app.include_router(paymentType_router)
app.include_router(payment_router)

app.add_middleware(SwaggerMiddleware)
app.add_middleware(RefreshTokenMiddleware)






