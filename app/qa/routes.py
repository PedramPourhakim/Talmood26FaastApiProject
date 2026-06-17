from typing import List

from fastapi import APIRouter, Depends, status, Query, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session, joinedload

from auth.jwt_auth import require_role,get_authenticated_user
from core.database import get_db
from qa.models import QAModel
from qa.schemas import *

router = APIRouter(tags=["qa"], prefix="/qa")


@cache(300)
@router.get("/get_all_questions_answers_rabbie", status_code=status.HTTP_200_OK,
            response_model=List[QAResponseSchema])
async def get_question_answers_of_rabbie(
        is_answered: bool = Query(None, description="filter question based on is answered or not"),
        limit: int = Query(
            10, gt=0, le=50, description="limiting the number of items to retrieve"
        ),
        offset: int = Query(
            0, ge=0, description="use for paginating based on passed items"
        ),
        user=Depends(require_role("is_rabbie")),
        db: Session = Depends(get_db)):
    query = (
        db.query(QAModel).options(joinedload(QAModel.talmid))
        .filter_by(rabbie_id=user.id)
    )
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not Found")
    if is_answered is not None:
        query = query.filter_by(is_answered=is_answered)
    return query.limit(limit).offset(offset).all()

@cache(300)
@router.get("/get_all_questions_answers_talmid", status_code=status.HTTP_200_OK,
            response_model=List[QAResponseSchema])
async def get_question_answers_of_talmid(
        is_answered: bool = Query(None, description="filter question based on is answered or not"),
        limit: int = Query(
            10, gt=0, le=50, description="limiting the number of items to retrieve"
        ),
        offset: int = Query(
            0, ge=0, description="use for paginating based on passed items"
        ),
        user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)):
    query = (
        db.query(QAModel).options(joinedload(QAModel.rabbie))
        .filter_by(talmid_id=user.id)
    )
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not Found")
    if is_answered is not None:
        query = query.filter_by(is_answered=is_answered)
    return query.limit(limit).offset(offset).all()


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=QAResponseSchema)
async def create_question_answer(request: CreateQASchema,
                                 db: Session = Depends(get_db)):
    new_question_answer = QAModel(**request.model_dump())
    db.add(new_question_answer)
    db.commit()
    db.refresh(new_question_answer)
    return new_question_answer


@router.put(
    "/{qa_id}",
    response_model=QAResponseSchema,
    status_code=status.HTTP_200_OK
)
async def update_qa(request: UpdateQASchema,
                    qa_id: str = Path(..., description="Id of the QA"),
                    db: Session = Depends(get_db)):
    qa = db.query(QAModel).filter_by(id=qa_id).one_or_none()
    if qa:
        qa.question = request.question
        qa.answer = request.answer
        qa.is_answered = request.is_answered
        db.commit()
        db.refresh(qa)
        return qa
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"QA with id {qa_id} not found")


@router.delete("/{qa_id}")
async def delete_qa(
        qa_id: str = Path(..., description="Id of the qa"),
        db: Session = Depends(get_db)
):
    qa = db.query(QAModel).filter_by(id=qa_id).one_or_none()
    if qa:
        db.delete(qa)
        db.commit()
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                            content={"message": "QA deleted successfully"})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"QA with id {qa_id} not found")


@router.get(
    "/{qa_id}",
    response_model=QAResponseSchema,
    status_code=status.HTTP_200_OK
)
async def retrieve_qa(
        qa_id: str = Path(..., description="Id of the qa"),
        db: Session = Depends(get_db)
):
    qa = db.query(QAModel).filter_by(id=qa_id).one_or_none()
    if qa:
        return qa
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"QA with id {qa} not found")


