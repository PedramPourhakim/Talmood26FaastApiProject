from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi_swagger import patch_fastapi
from utils.exception_handler import (HttpExceptionHandler,
                                     ValidationExceptionHandler)
from utils.Auth_Middleware import RefreshTokenMiddleware
from person.routes import router as person_router
from weeklyParashah.routes import router as parasha_router
from templates.rendering_pages import router as index_page_router
from users.routes import router as users_router
from sqladmin import Admin
from core.database import engine
from person.view import PersonView
from weeklyParashah.view import ParashaView
from users.view import UserView
from fastapi.staticfiles import StaticFiles
import os
# app = FastAPI(docs_url=None,
#     swagger_ui_oauth2_redirect_url=None)
app = FastAPI(docs_url="/swagger", redoc_url=None)
UPLOAD_DIR = "static/parasha_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")

admin = Admin(app,engine)
admin.add_view(PersonView)
admin.add_view(ParashaView)
admin.add_view(UserView)

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
app.include_router(index_page_router)

app.add_middleware(RefreshTokenMiddleware)



