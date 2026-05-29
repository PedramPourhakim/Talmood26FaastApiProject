from fastapi.templating import Jinja2Templates
from fastapi import APIRouter,Request,Depends,HTTPException,status
from sqlalchemy.orm import Session
from core.database import get_db
from weeklyParashah.models import ParashaModel
from fastapi_cache.decorator import cache

templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["index_page"])

@cache(expire=7200)
@router.get("/")
async def get_landing_page(request: Request,db: Session = Depends(get_db)):
    latest_parasha = db.query(ParashaModel).order_by(ParashaModel.creation_date.desc()).first()
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