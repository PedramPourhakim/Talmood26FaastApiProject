from starlette.middleware.base import BaseHTTPMiddleware
from jwt.exceptions import ExpiredSignatureError
from auth.jwt_auth import generate_access_token, decode_token


class RefreshTokenMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        new_access_token = None
        current_user = None

        if access_token:
            try:
                payload = decode_token(access_token)

                if payload.get("type") == "access":
                    current_user = payload

            except ExpiredSignatureError:

                if refresh_token:
                    try:
                        payload = decode_token(refresh_token)

                        if payload.get("type") == "refresh":

                            current_user = {
                                "user_id": payload["user_id"],
                                "name": payload["name"],
                                "family_name": payload["family_name"],
                            }

                            new_access_token = generate_access_token(
                                current_user
                            )

                    except Exception:
                        pass

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