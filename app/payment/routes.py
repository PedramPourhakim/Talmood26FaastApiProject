from payment.schemas import *
from fastapi import APIRouter, Depends, status,Query,Path
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session, joinedload
from auth.jwt_auth import get_authenticated_user
from core.database import get_db
from payment.models import PaymentModel,PaymentStatusEnum
from zarinpal import ZarinPal
from core.config import zarinpal_config,settings

router = APIRouter(tags=["payment"], prefix="/payments")


@cache(60)
@router.get("/get_person_payments",status_code=status.HTTP_200_OK,
            response_model=PaginatedPaymentResponseSchema)
async def get_person_payments(user:dict = Depends(get_authenticated_user),
                            payment_status:PaymentStatusEnum=Query(None),
                            limit: int = Query(10, gt=0, le=50),
                            offset: int = Query(0, ge=0),
                            db: Session = Depends(get_db)):

    query = (
        db.query(PaymentModel)
        .options(joinedload(PaymentModel.payment_account))
        .filter(PaymentModel.person_id == user["person_id"])
        .order_by(PaymentModel.creation_date.desc())
    )
    if payment_status is not None:
        query = query.filter(PaymentModel.status == payment_status)
    total = query.count()
    items = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "items": items,
        "total": total,
        "page": (offset // limit) + 1,
        "page_size": limit
    }


@router.post("", status_code=status.HTTP_201_CREATED,
             response_model=ResponsePaymentSchema)
async def create_new_payment(request: CreatePaymentSchema,
                                user:dict = Depends(get_authenticated_user),
                                 db: Session = Depends(get_db)):
    new_payment = PaymentModel(amount=request.amount,
                               description=request.description,
                               payment_account_id=request.payment_account_id,
                               person_id=request.person_id
                               )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    payment_request = CreatePaymentRequestSchema(
        amount=new_payment.amount,
        description= f"{request.payment_account_title} : {new_payment.description}",
        callback_url= settings.ZARIN_PAL_CALLBACK_URL,
        mobile= user["phone"],
        email= user["email"],
    )
    return new_payment



# def initiate_payment():
#     try:
#         zarinpal = ZarinPal(zarinpal_config)
#         response = zarinpal.payments.create({
#
#         })

@router.put(
    "/{payment_id}",
    response_model=ResponsePaymentSchema,
    status_code=status.HTTP_200_OK
)
async def update_payment(request: UpdatePaymentSchema,
                   payment_id: str = Path(..., description="Id of the Payment"),
                    db: Session = Depends(get_db),
                    user: dict = Depends(get_authenticated_user)):
    payment = db.query(PaymentModel).filter_by(id=payment_id,person_id=user["person_id"]).one_or_none()
    if payment:
        payment = PaymentModel(**request.model_dump())
        db.commit()
        db.refresh(payment)
        return payment
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Payment with id {payment_id} not found")


@router.delete("/{payment_id}")
async def delete_payment(
        payment_id: str = Path(..., description="Id of the payment"),
        db: Session = Depends(get_db),
        user: dict = Depends(get_authenticated_user)
):
    payment = (db.query(PaymentModel)
               .filter_by(id=payment_id,
                          person_id=user["person_id"]).one_or_none())
    if payment:
        db.delete(payment)
        db.commit()
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
                            content={})
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Payment with id {payment_id} not found")


@router.get(
    "/{payment_id}",
    response_model=ResponsePaymentSchema,
    status_code=status.HTTP_200_OK
)
async def retrieve_payment(
        payment_id: str = Path(..., description="Id of the payment"),
        user: dict = Depends(get_authenticated_user),
        db: Session = Depends(get_db)
):
    payment = (db.query(PaymentModel)
               .options(joinedload(PaymentModel.payment_account))
               .filter_by(id=payment_id,person_id=user["person_id"]).one_or_none())
    if payment:
        return payment
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"payment with id {payment_id} not found")