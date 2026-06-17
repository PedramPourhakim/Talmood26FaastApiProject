from typing import List

from fastapi import (
    APIRouter,
    status,
    Query,
    Depends,
    Path,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from core.database import get_db
from weeklyParashah.models import ParashaModel
from weeklyParashah.schemas import BaseParashahSchema, ResponseParashahSchema
from utils.FileManager import delete_old_image, save_file

router = APIRouter(tags=["Parasha"], prefix="/parasha")

@cache(expire=30)
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[BaseParashahSchema]
)
async def get_parashim(
    q: str | None = Query(
        default=None,
        alias="Search",
        description="Search Parashah by Title",
        max_length=255
    ),
    db: Session = Depends(get_db)
):
    query = db.query(ParashaModel)

    if q:
        query = query.filter(ParashaModel.title.ilike(f"%{q}%"))

    result = query.all()
    return result
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseParashahSchema
)
async def create_parasha(
    title: str = Form(..., description="Parasha title"),
    description: str | None = Form(None, description="Parasha description"),
    image: UploadFile = File(..., description="Parasha image"),
    db: Session = Depends(get_db)
):
    new_parashah = ParashaModel(
        title=title,
        description=description,
    )

    new_parashah.image_path = save_file("parasha_images",image)

    db.add(new_parashah)
    db.commit()
    db.refresh(new_parashah)

    return new_parashah

@router.put(
    "/{parasha_id}",
    response_model=ResponseParashahSchema,
    status_code=status.HTTP_200_OK
)
async def update_parasha(
    parasha_id: str = Path(..., description="Id of the parasha"),
    title: str | None = Form(None, description="Parasha title"),
    description: str | None = Form(None, description="Parasha description"),
    image: UploadFile | None = File(None, description="New parasha image"),
    db: Session = Depends(get_db)
):
    parasha = db.query(ParashaModel).filter_by(id=parasha_id).one_or_none()

    if not parasha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parasha with id {parasha_id} not found"
        )

    if title is not None:
        parasha.title = title

    if description is not None:
        parasha.description = description

    if image and getattr(image, "filename", "").strip():
        delete_old_image(parasha.image_path)
        parasha.image_path = save_file("parasha_images",image)

    db.commit()
    db.refresh(parasha)

    return parasha

@router.delete(
    "/{parasha_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_parasha(
    parasha_id: str = Path(..., description="Id of the parasha"),
    db: Session = Depends(get_db)
):
    parasha = db.query(ParashaModel).filter_by(id=parasha_id).one_or_none()

    if not parasha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parasha with id {parasha_id} not found"
        )

    delete_old_image(parasha.image)

    db.delete(parasha)
    db.commit()

# @router.get(
#     "/{parasha_id}",
#     status_code=status.HTTP_200_OK,
#     response_model=ResponseParashahSchema
# )
# async def get_one_parasha(
#     parasha_id: str = Path(..., description="Id of the parasha"),
#     db: Session = Depends(get_db)
# ):
#     parasha = db.query(ParashaModel).filter_by(id=parasha_id).one_or_none()
#
#     if not parasha:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Parasha with id {parasha_id} not found"
#         )
#
#     return parasha