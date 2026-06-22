import json
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter,Request,Depends,HTTPException,status,Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from core.database import get_db
from weeklyParashah.models import ParashaModel
from person.schemas import CreatePersonSchema
from person.models import PersonModel
from users.models import UserModel
from sqlalchemy import or_
from pydantic import BaseModel,Field,EmailStr
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from core.config import settings

templates = Jinja2Templates(directory="templates")
router = APIRouter(tags=["index_page"])


def inject_user(request: Request):
    return {
        "current_user":  request.state.current_user
    }

templates.context_processors.append(inject_user)

redis = aioredis.from_url(settings.REDIS_URL)
cache_backend = RedisBackend(redis)
FastAPICache.init(cache_backend,prefix="fastapi-cache")
CACHE_KEY = "latest_parasha_landing_page"


@router.get("/")
async def get_landing_page(request: Request,
                           db: Session = Depends(get_db)):

    cached = await redis.get(CACHE_KEY)

    if cached:
        latest_parasha = json.loads(cached)
    else:
        parasha = (
            db.query(ParashaModel)
            .order_by(ParashaModel.creation_date.desc())
            .first()
        )

        latest_parasha = None

        if parasha:
            latest_parasha = {
                "id": parasha.id,
                "title": parasha.title,
                "description": parasha.description,
                "image_url": parasha.image["url"] if parasha.image else None,
                "creation_date": parasha.creation_date.isoformat()
            }

        await redis.set(
            CACHE_KEY,
            json.dumps(latest_parasha),
            ex=3600 * 24 * 7
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"latest_parasha": latest_parasha},
    )

@router.get("/parasha/{parasha_id}")
async def get_parasha_detail(request:Request,parasha_id:str,db: Session = Depends(get_db)):
    parasha = db.query(ParashaModel).filter(ParashaModel.id == parasha_id).first()
    if not parasha:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parasha not found")
    return templates.TemplateResponse(
        request=request,
        name="parasha_detail.html",
        context={"parasha": parasha},
    )

class UserRegisterBaseSchema(BaseModel):
    email: EmailStr
    phone: str = Field(..., max_length=11)
class AddPersonRegisterUserClass(CreatePersonSchema, UserRegisterBaseSchema):
    pass


@router.post("/AddPersonRegisterUser")
async def add_person_register_user(request: AddPersonRegisterUserClass,
                                   db: Session = Depends(get_db)):
    try:
        # ۱. چک کردن تکراری بودن کاربر قبل از هر کاری
        if db.query(UserModel).filter(
                or_(
                    UserModel.email == request.email.lower(),
                    UserModel.phone == request.phone
                )
        ).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="کاربری با این ایمیل یا شماره موبایل قبلاً ثبت‌نام کرده است."
            )

        # ۲. ایجاد Person (هنوز Commit نمی‌کنیم)
        person_data = {
            "name": request.name,
            "family_name": request.family_name,
            "is_admin": request.is_admin,
            "is_rabbie": request.is_rabbie
        }
        new_person = PersonModel(**person_data)
        db.add(new_person)

        # flush باعث می‌شود ID شخص تولید شود ولی هنوز در دیتابیس دائمی نشود
        db.flush()

        # ۳. ایجاد User با استفاده از ID مرحله قبل
        user_obj = UserModel(
            email=str(request.email).lower(),
            phone=request.phone,
            person_id=new_person.id  # اینجا متصل می‌شود
        )
        db.add(user_obj)

        # ۴. نهایی کردن هر دو عملیات با هم
        db.commit()
        db.refresh(user_obj)

        return {
            "status": status.HTTP_201_CREATED,
            "data": {
                "user_id": user_obj.id,
                "person_id": new_person.id,
                "email": user_obj.email
            }
        }

    except HTTPException as e:
        # اگر خطای تکراری بودن بود، تغییرات را برگردان و خطا را بفرست
        db.rollback()
        raise e
    except Exception as e:
        # در صورت هر خطای پیش‌بینی نشده‌ای، دیتابیس را به حالت اول برگردان
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطای سیستمی: {str(e)}"
        )

@router.post("/logout")
async def logout(request: Request):
    response = JSONResponse({"message": "logged out"})
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    request.state.current_user = None
    return response
