from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi_swagger import patch_fastapi
from qa.view import QAView
from utils.exception_handler import (HttpExceptionHandler,
                                     ValidationExceptionHandler)
from utils.Auth_Middleware import RefreshTokenMiddleware,AdminAuth,SwaggerMiddleware
from person.routes import router as person_router
from weeklyParashah.routes import router as parasha_router
from templates.rendering_pages import router as index_page_router
from users.routes import router as users_router
from qa.routes import router as qa_router
from sqladmin import Admin
from core.database import engine
from person.view import PersonView
from weeklyParashah.view import ParashaView
from users.view import UserView
from fastapi.staticfiles import StaticFiles
from sqlalchemy_file.storage import StorageManager
from libcloud.storage.drivers.local import LocalStorageDriver
import os
from core.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
# app = FastAPI(docs_url=None,
#     swagger_ui_oauth2_redirect_url=None)

os.makedirs("static/person_images",exist_ok=True)
os.makedirs("static/parasha_images",exist_ok=True)
person_container = LocalStorageDriver("static").get_container("person_images")
parasha_container = LocalStorageDriver("static").get_container("parasha_images")

StorageManager.add_storage("person_storage", person_container)
StorageManager.add_storage("parasha_storage", parasha_container)

# اگر خواستی default هم داشته باشی (اختیاری)
default_container = LocalStorageDriver("static").get_container(".")
StorageManager.add_storage("default", default_container)
app = FastAPI(docs_url="/swagger", redoc_url=None)


UPLOAD_DIR = "static/parasha_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

admin = Admin(app,engine,
    authentication_backend=AdminAuth(
        secret_key=settings.JWT_SECRET_KEY
    ))
admin.add_view(PersonView)
admin.add_view(ParashaView)
admin.add_view(UserView)
admin.add_view(QAView)

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

app.add_middleware(SwaggerMiddleware)
app.add_middleware(RefreshTokenMiddleware)

redis = aioredis.from_url(settings.REDIS_URL)
cache_backend = RedisBackend(redis)
FastAPICache.init(cache_backend,prefix="fastapi-cache")




