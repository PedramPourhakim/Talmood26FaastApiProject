from typing import List

from fastapi import APIRouter, Depends, status, Query, HTTPException, Path
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session, joinedload

import qa
from auth.jwt_auth import get_authenticated_user
from core.database import get_db
from qa.models import QAModel
from qa.schemas import *

router = APIRouter(tags=["qa"], prefix="/qa")


@cache(60)
@router.get("/get_all_questions_answers", status_code=status.HTTP_200_OK,
            response_model=List[QAResponseSchema])
async def get_question_answers(
        is_answered: bool = Query(None, description="filter question based on is answered or not"),
        limit: int = Query(
            10, gt=0, le=50, description="limiting the number of items to retrieve"
        ),
        offset: int = Query(
            0, ge=0, description="use for paginating based on passed items"
        ),
        user=Depends(get_authenticated_user),
        db: Session = Depends(get_db)):
    if user["is_rabbie"]:
        query = (
            db.query(QAModel)
            .options(joinedload(QAModel.talmid))
            .filter(QAModel.rabbie_id == user["person_id"])
        )
    else:
        query = (
            db.query(QAModel)
            .options(joinedload(QAModel.rabbie))
            .filter(QAModel.talmid_id == user["person_id"])
        )

    if is_answered is not None:
        query = query.filter(QAModel.is_answered == is_answered)

    query_result = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )
    return query_result


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
                    db: Session = Depends(get_db),
                    user: dict = Depends(get_authenticated_user)):

    qa = db.query(QAModel).filter_by(id=qa_id).one_or_none()
    if qa:
        if user["is_rabbie"]:
            answer = (request.answer or "").strip()

            if not answer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Answer is required"
                )

            qa.answer = answer
            qa.is_answered = True
        else:
            qa.question = request.question
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
