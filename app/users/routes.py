import json
from fastapi import (APIRouter,Depends,HTTPException,status,
                     Response,Path,Request)
from fastapi.responses import JSONResponse
from sqlalchemy import or_
from fastapi_cache.decorator import cache
from sqlalchemy.orm import joinedload
import auth.jwt_auth
from core.config import settings
from users.schemas import *
from users.models import UserModel
from sqlalchemy.orm import Session
from core.database import get_db
from auth.jwt_auth import (
generate_access_token,
generate_refresh_token,
decode_refresh_token
)
import random
from typing import List
from utils.email_util import send_email
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
router = APIRouter(tags=["users"],prefix="/users")

redis = aioredis.from_url(settings.REDIS_URL)
cache_backend = RedisBackend(redis)
FastAPICache.init(cache_backend,prefix="fastapi-cache")

@cache(expire=30)
@router.get("/",
            status_code=status.HTTP_200_OK,
            response_model=List[UserResponseSchema])
async def get_users(db : Session = Depends(get_db)):
    query = db.query(UserModel)
    get_all_query_result = query.all()
    return get_all_query_result

@router.get("/get_current_user")
async def get_current_user(request:Request):
    current_user = await auth.jwt_auth.get_current_user(request)
    return current_user
@router.post("/login",status_code=status.HTTP_200_OK)
async def first_step_login(request: UserLoginSchema,db: Session = Depends(get_db)):
    user_obj : UserModel | None = (
        db.query(UserModel).options(joinedload(UserModel.person))
        .filter_by(email=request.email.lower()).first()
    )
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_obj.verification_code = random.randint(1000,9999)
    db.commit()
    db.refresh(user_obj)
    await redis.set(
        f"login_code:{user_obj.email}",
        json.dumps({
           "code": user_obj.verification_code,
            "user_id": user_obj.id,
            "name":user_obj.person.name,
            "family_name":user_obj.person.family_name,
            "is_admin":user_obj.person.is_admin,
        }),
        ex=300
    )
    await send_email(
        subject="Talmood26 Verification Code",
        recipients=[user_obj.email],
        body=f"Your verification code is : {user_obj.verification_code}"
    )
    return JSONResponse({
        "status": status.HTTP_200_OK,
        "detail":"Verification code sent successfully"
    })
@router.post("/verify")
async def verify_code(request:VerificationCodeSchema,
                      response:Response):
    data = await redis.get(f"login_code:{request.email}")

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid verification code"
        )
    data = json.loads(data)
    if data["code"] != request.verification_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid verification code")

    await redis.delete(f"login_code:{request.email}")
    access_token = generate_access_token(data)
    refresh_token = generate_refresh_token(data)
    response = JSONResponse({
        "status": status.HTTP_200_OK,
        "detail": "User Logged in successfully"
    })
    response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=3600
        )
    response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite="lax",
                max_age=60 * 60 * 24,
            )
    return response


@router.post("/register",status_code=status.HTTP_201_CREATED)
async def register_user(request: UserRegisterSchema,db: Session = Depends(get_db)):
    if db.query(UserModel).filter(
        or_(
            UserModel.email == request.email.lower(),
            UserModel.phone == request.phone
        )
    ).first():
        raise HTTPException(
status_code=status.HTTP_409_CONFLICT,
    detail="User already exists"
        )
    data = request.model_dump(exclude_unset=True)
    user_obj = UserModel(**data)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return JSONResponse(content={
        "status": status.HTTP_201_CREATED,
        "data": user_obj
    },status_code=status.HTTP_201_CREATED)

@router.post("/refresh-token")
async def user_refresh_token(request: Request,
                             response:Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
    user_id = await decode_refresh_token(refresh_token)
    new_access = generate_access_token(user_id)
    new_refresh = generate_refresh_token(user_id)

    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=3600
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )
    return response

@router.put("/update/{user_id}",status_code=status.HTTP_200_OK,
            response_model=UserResponseSchema)
async def update_user(request:UserUpdateSchema,
                      user_id:str = Path(...,description="user id"),
                      db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(id=user_id).one_or_none()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    data = request.model_dump(exclude_unset=True)
    for key,value in data.items():
        setattr(user_obj, key, value)
    db.commit()
    db.refresh(user_obj)
    return user_obj

@router.delete("/delete/{user_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id:str = Path(...,description="user id"),
                      db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(id=user_id).one_or_none()
    if user_obj:
        db.delete(user_obj)
        db.commit()
        return JSONResponse(content={
            "status": status.HTTP_204_NO_CONTENT,
        })
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.post("/logout")
async def logout(response: Response):

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"status": "logged out"}