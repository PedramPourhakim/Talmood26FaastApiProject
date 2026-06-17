from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError
from core.config import settings
security = HTTPBearer(scheme_name="Token")


def get_authenticated_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM
        )
        if payload.get("type") != "access":
            print("Token type not supported")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed,token type not valid",
            )
        current_user = {
            "user_id": payload["user_id"],
            "name": payload["name"],
            "family_name": payload["family_name"],
            "is_admin": payload["is_admin"],
            "is_rabbie": payload["is_rabbie"],
        }
        return current_user
    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed,invalid signature",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed decode failed",
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed expired token "
                   f"{ExpiredSignatureError}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e}",
        )


def get_authenticated_rabbie(
        user: dict = Depends(get_authenticated_user),
):
    if user.get("is_rabbie"):
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden Access To EndPoint"
    )
def require_role(role: str):
    def checker(user: dict = Depends(get_authenticated_user)):
        if user.get(role):
            return user
        raise HTTPException(status_code=403, detail="Forbidden")
    return checker

def generate_access_token(
        user_data: dict,
        expires_in: int = 60 * 60
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "type": "access",
        "user_id": str(user_data["user_id"]),
        "name": user_data["name"],
        "family_name": user_data["family_name"],
        "is_admin": user_data["is_admin"],
        "is_rabbie": user_data["is_rabbie"],
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(seconds=expires_in)).timestamp()
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def generate_refresh_token(
        user_data: dict,
        expires_in: int = 60 * 60 * 24
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "type": "refresh",
        "user_id": str(user_data["user_id"]),
        "name": user_data["name"],
        "family_name": user_data["family_name"],
        "is_admin": user_data["is_admin"],
        "is_rabbie": user_data["is_rabbie"],
        "iat": int(now.timestamp()),
        "exp": int(
            (now + timedelta(seconds=expires_in)).timestamp()
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


async def decode_refresh_token(token):
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed,token type not valid",
            )
        return decoded

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed,invalid signature",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed decode failed",
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed expired token" f"{ExpiredSignatureError}",
        )
    except Exception as e:
        print(type(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e}",
        )


def decode_token(token: str):
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=settings.JWT_ALGORITHM
    )


def get_current_user(
        request: Request,
):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return None
    try:
        payload = decode_token(access_token)
        if payload.get("type") != "access":
            return None
        return payload
    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed,invalid signature",
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed decode failed",
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed expired token" f"{ExpiredSignatureError}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {e}",
        )
# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db),
# ):
#     token = credentials.credentials
#     try:
#         decoded = jwt.decode(
#             token, settings.JWT_SECRET_KEY, algorithms=settings.JWT_ALGORITHM
#         )
#         user_id = decoded.get("user_id", None)
#         if not user_id:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Authentication failed,user_id not in the payload",
#             )
#         if decoded.get("type") != "access":
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Authentication failed,token type not valid",
#             )
#         user_obj = db.query(UserModel).filter_by(id=user_id).first()
#         return user_obj
#     except InvalidSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication failed,invalid signature",
#         )
#     except DecodeError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication failed decode failed",
#         )
#     except ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Authentication failed expired token" f"{ExpiredSignatureError}",
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=f"Authentication failed: {e}",
#         )
