from starlette.middleware.base import BaseHTTPMiddleware
from jwt.exceptions import ExpiredSignatureError
from auth.jwt_auth import generate_access_token, decode_token
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from fastapi.responses import JSONResponse


class RefreshTokenMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        if request.url.path == "/logout":
            return await call_next(request)

        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        new_access_token = None
        current_user = None
        access_token_expired = False
        if access_token:
            try:
                payload = decode_token(access_token)

                if payload.get("type") == "access":
                    current_user = {
                        "user_id": payload["user_id"],
                        "person_id": payload["person_id"],
                        "name": payload["name"],
                        "family_name": payload["family_name"],
                        "is_admin": payload["is_admin"],
                        "is_rabbie": payload["is_rabbie"],
                        "phone": payload["phone"],
                        "email": payload["email"],
                    }
            except ExpiredSignatureError:
                access_token_expired = True
        elif refresh_token:
            try:
                payload = decode_token(refresh_token)

                if payload.get("type") == "refresh":
                    current_user = {
                        "user_id": payload["user_id"],
                        "person_id": payload["person_id"],
                        "name": payload["name"],
                        "family_name": payload["family_name"],
                        "is_admin": payload["is_admin"],
                        "is_rabbie": payload["is_rabbie"],
                        "phone": payload["phone"],
                        "email": payload["email"],
                    }

                    new_access_token = generate_access_token(current_user)
            except Exception as e:
                print(e)

        request.state.current_user = current_user

        response = await call_next(request)

        if new_access_token:
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=3600,
            )

        return response

class AdminAuth(AuthenticationBackend):

    def __init__(self, secret_key: str):
        super().__init__(secret_key)

    async def login(self, request: Request) -> bool:
        return True

    async def logout(self, request: Request) -> bool:
        return True

    async def authenticate(self, request: Request) -> bool:

        current_user = getattr(request.state, "current_user", None)

        if current_user is None:
            return False

        return current_user["is_admin"]

class SwaggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        protected_paths = [
            "/swagger",
            "/openapi.json"
        ]

        if request.url.path in protected_paths:

            current_user = getattr(
                request.state,
                "current_user",
                None
            )

            if (
                current_user is None
                or not current_user["is_admin"]
            ):
                return JSONResponse(
                    {"detail": "Forbidden"},
                    status_code=403
                )

        return await call_next(request)


