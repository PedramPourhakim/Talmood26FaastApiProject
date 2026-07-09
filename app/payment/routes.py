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
from sqlalchemy import and_, or_, desc, asc
from person.models import PersonModel
from datetime import  date,time
from sqlalchemy import cast, Date

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


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_new_payment(request: CreatePaymentSchema,
                                user:dict = Depends(get_authenticated_user),
                                 db: Session = Depends(get_db)):
    new_payment = PaymentModel(amount=request.amount,
                               description=request.description,
                               payment_account_id=request.payment_account_id,
                               person_id=request.person_id
                               )
    payment_request = CreatePaymentRequestSchema(
        amount=new_payment.amount,
        description= f"{request.payment_account_title} : {new_payment.description}",
        callback_url= settings.ZARIN_PAL_CALLBACK_URL,
        mobile= user["phone"],
        email= user["email"],

    )
    authority,payment_url = initiate_payment(payment_request)
    new_payment.authority = authority
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return JSONResponse({
        "payment_url": payment_url
    })



def initiate_payment(payment_request: CreatePaymentRequestSchema):
    try:
        zarinpal = ZarinPal(zarinpal_config)
        response = zarinpal.payments.create(
            payment_request.model_dump()
        )

        if "data" in response and "authority" in response["data"]:
            authority = response["data"]["authority"]
            payment_url = zarinpal.payments.generate_payment_url(authority)
            return authority, payment_url
        else:
            print("Authority not found in response.")
    except Exception as e:
        print("Error during payment creation:", e)

@router.get("/payment-report")
async def payment_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_authenticated_user),

    page_size: int = Query(20, ge=1, le=100),

    cursor_date: datetime | None = None,
    cursor_id: str | None = None,

    status: PaymentStatusEnum | None = None,

    from_date: date | None = None,
    to_date: date | None = None,

    search: str | None = None,

    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
):

    payment_account_ids = current_user.get("payment_account_ids", [])

    if not payment_account_ids:
        return {
            "has_next": False,
            "next_cursor": None,
            "items": []
        }

    query = (
        db.query(PaymentModel)
        .join(PaymentModel.person)
        .options(
            joinedload(PaymentModel.person),
            joinedload(PaymentModel.payment_account)
        )
        .filter(
            PaymentModel.payment_account_id.in_(payment_account_ids)
        )
    )

    # وضعیت پرداخت
    if status:
        query = query.filter(
            PaymentModel.status == status
        )

    # بازه زمانی
    if from_date:
        query = query.filter(
            cast(PaymentModel.creation_date, Date) >= from_date
        )

    if to_date:
        query = query.filter(
            cast(PaymentModel.creation_date, Date) <= to_date
        )

    # جستجو
    if search:
        search = f"%{search.strip()}%"
        query = query.filter(
            or_(
                PersonModel.name.ilike(search),
                PersonModel.family_name.ilike(search)
            )
        )

    # Cursor Pagination
    if cursor_date:

        if sort_order == "desc":

            if cursor_id:
                query = query.filter(
                    or_(
                        PaymentModel.creation_date < cursor_date,
                        and_(
                            PaymentModel.creation_date == cursor_date,
                            PaymentModel.id < cursor_id
                        )
                    )
                )
            else:
                query = query.filter(
                    PaymentModel.creation_date < cursor_date
                )

        else:

            if cursor_id:
                query = query.filter(
                    or_(
                        PaymentModel.creation_date > cursor_date,
                        and_(
                            PaymentModel.creation_date == cursor_date,
                            PaymentModel.id > cursor_id
                        )
                    )
                )
            else:
                query = query.filter(
                    PaymentModel.creation_date > cursor_date
                )

    # مرتب سازی
    if sort_order == "desc":
        query = query.order_by(
            desc(PaymentModel.creation_date),
            desc(PaymentModel.id)
        )
    else:
        query = query.order_by(
            asc(PaymentModel.creation_date),
            asc(PaymentModel.id)
        )

    # یک رکورد بیشتر می‌خوانیم تا بفهمیم صفحه بعدی وجود دارد یا خیر
    payments = query.limit(page_size + 1).all()

    has_next = len(payments) > page_size

    if has_next:
        payments = payments[:-1]

    items = []

    for payment in payments:

        items.append({
            "payment_id": payment.id,
            "amount": payment.amount,
            "status": payment.status.value,
            "authority": payment.authority,
            "ref_id": payment.ref_id,
            "card_pan": payment.card_pan,
            "fee": payment.fee,
            "creation_date": payment.creation_date,
            "paid_at": payment.paid_at,
            "description":payment.description,

            "payment_account": {
                "id": payment.payment_account.id,
                "title": payment.payment_account.account_title,
                "sheba_number": payment.payment_account.sheba_number,
            },

            "payer": {
                "id": payment.person.id,
                "name": payment.person.name,
                "family_name": payment.person.family_name,
            }
        })

    next_cursor = None

    if has_next:
        last = payments[-1]
        next_cursor = {
            "cursor_date": last.creation_date.isoformat(),
            "cursor_id": last.id
        }

    return {
        "has_next": has_next,
        "next_cursor": next_cursor,
        "items": items
    }


# @router.put(
#     "/{payment_id}",
#     response_model=ResponsePaymentSchema,
#     status_code=status.HTTP_200_OK
# )
# async def update_payment(request: UpdatePaymentSchema,
#                    payment_id: str = Path(..., description="Id of the Payment"),
#                     db: Session = Depends(get_db),
#                     user: dict = Depends(get_authenticated_user)):
#     payment = db.query(PaymentModel).filter_by(id=payment_id,person_id=user["person_id"]).one_or_none()
#     if payment:
#         payment = PaymentModel(**request.model_dump())
#         db.commit()
#         db.refresh(payment)
#         return payment
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Payment with id {payment_id} not found")
#
#
# @router.delete("/{payment_id}")
# async def delete_payment(
#         payment_id: str = Path(..., description="Id of the payment"),
#         db: Session = Depends(get_db),
#         user: dict = Depends(get_authenticated_user)
# ):
#     payment = (db.query(PaymentModel)
#                .filter_by(id=payment_id,
#                           person_id=user["person_id"]).one_or_none())
#     if payment:
#         db.delete(payment)
#         db.commit()
#         return JSONResponse(status_code=status.HTTP_204_NO_CONTENT,
#                             content={})
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"Payment with id {payment_id} not found")
#
#
# @router.get(
#     "/{payment_id}",
#     response_model=ResponsePaymentSchema,
#     status_code=status.HTTP_200_OK
# )
# async def retrieve_payment(
#         payment_id: str = Path(..., description="Id of the payment"),
#         user: dict = Depends(get_authenticated_user),
#         db: Session = Depends(get_db)
# ):
#     payment = (db.query(PaymentModel)
#                .options(joinedload(PaymentModel.payment_account))
#                .filter_by(id=payment_id,person_id=user["person_id"]).one_or_none())
#     if payment:
#         return payment
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"payment with id {payment_id} not found")