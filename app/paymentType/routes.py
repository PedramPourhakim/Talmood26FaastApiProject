from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session,joinedload
from auth.jwt_auth import get_authenticated_user
from core.database import get_db
from paymentType.models import PaymentTypeModel
from paymentType.schemas import PaymentTypeResponseSchema

router = APIRouter(tags=["payment_type"], prefix="/payment_type")

@cache(3600 * 24 * 7)
@router.get("/get_all_payment_types",
            response_model=List[PaymentTypeResponseSchema],
            status_code=status.HTTP_200_OK)
def get_all_payment_types(user:dict = Depends(get_authenticated_user),db: Session = Depends(get_db)):
    query = db.query(PaymentTypeModel).options(
        joinedload(PaymentTypeModel.payment_accounts)
    ).all()
    return query