import uuid
from datetime import datetime
from pydantic import BaseModel,Field,field_validator
from payment.models import PaymentStatusEnum
from typing import List
from paymentAccount.schemas import PaymentAccountResponseSchema

class PaymentSchema(BaseModel):
    person_id: str = Field(..., description="Unique identifier of the Person Who wants to pay")
    payment_account_id : str = Field(..., description="Unique identifier of the Payment Account")
    amount: int = Field(..., gt=26000,description="Amount to be paid")
    status : PaymentStatusEnum = Field(PaymentStatusEnum.PENDING, description="Payment Status")
    description : str = Field(description="Payment Description")

    @field_validator("person_id", "payment_account_id")
    @classmethod
    def validate_ids(cls, value: str):
        if not value.strip():
            raise ValueError("This field is required")
        return value

class CreatePaymentSchema(PaymentSchema):
    payment_account_title: str = Field(..., description="Payment Account Title")

class UpdatePaymentSchema(PaymentSchema):
    pass

class ResponsePaymentSchema(PaymentSchema):
    id: str = Field(..., description="Unique identifier of the Payment")
    creation_date: datetime= Field(description="Date of creation")
    payment_account : PaymentAccountResponseSchema = Field()
    authority: str | None = Field(description="Authority from zarin pal")
    ref_id: str | None = Field(description="reference id of the payment")
    card_pan: str | None = Field(description="card pan of the payment")
    fee: int | None = Field(description="fee of the payment")
    paid_at : datetime | None = Field(description="Date of paid")



class PaginatedPaymentResponseSchema(BaseModel):
    items: List[ResponsePaymentSchema]
    total: int
    page: int
    page_size: int

class CreatePaymentRequestSchema(BaseModel):
    amount: int = Field(..., description="Amount to be paid")
    description: str = Field(...,description="Payment Description")
    callback_url: str = Field(...,description="Callback URL")
    mobile: str | None= Field(description="Mobile Number")
    email: str | None= Field(description="Email Address")
    currency: str = Field(default="IRT")

