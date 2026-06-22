from fastapi import APIRouter,status,Query,Depends,Path
from fastapi_cache.decorator import cache
from person.schemas import *
from person.models import *
from typing import List
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from core.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["person"],prefix="/person")


@cache(expire=30)
@router.get("/people",
            status_code=status.HTTP_200_OK,
            response_model=List[PersonResponseSchema])
async def get_people(db : Session = Depends(get_db)):
    query = db.query(PersonModel)
    get_all_query_result = query.all()
    return get_all_query_result

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PersonResponseSchema
)
async def create_person(request: CreatePersonSchema, db: Session = Depends(get_db)):
    new_person = PersonModel(**request.model_dump())
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    return new_person

@router.put(
    "/{person_id}",
    response_model=PersonResponseSchema,
    status_code=status.HTTP_200_OK
)
async def update_person(request: UpdatePersonSchema,
                    person_id: str = Path(...,description="Id of the person"),
                  db: Session = Depends(get_db)):
    person = db.query(PersonModel).filter_by(id=person_id).one_or_none()
    if person:
        person.email=request.email
        person.phone=request.phone
        db.commit()
        db.refresh(person)
        return person
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {person_id} not found")

@router.delete("/{person_id}")
async def delete_person(
    person_id:str = Path(...,description="Id of the person"),
    db: Session = Depends(get_db)
):
    person = db.query(PersonModel).filter_by(id=person_id).one_or_none()
    if person:
        db.delete(person)
        db.commit()
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                            content={"message": "Person deleted successfully"})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {person_id} not found")


@router.get(
    "/get_one_person/{person_id}",
    response_model=PersonResponseSchema,
    status_code=status.HTTP_200_OK
)
async def retrieve_person(
    person_id:str = Path(...,description="Id of the person"),
    db: Session = Depends(get_db)
):
    person = db.query(PersonModel).filter_by(id=person_id).one_or_none()
    if person:
        return person
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Person with id {person_id} not found")

@cache(300)
@router.get("/get_rabbies",response_model=List[PersonResponseSchema],
                status_code=status.HTTP_200_OK)
async def get_rabbies(db: Session = Depends(get_db)):
    query = db.query(PersonModel).filter_by(is_rabbie=True)
    get_all_query_result = query.all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "family_name": p.family_name,
            "image": p.image["url"] if p.image else None,
            "is_admin": p.is_admin,
            "is_rabbie": p.is_rabbie,
            "creation_date": p.creation_date,
        }
        for p in get_all_query_result
    ]
