from pydantic import BaseModel,Field
from paymentAccount.schemas import PaymentAccountResponseSchema
from typing import List

class PaymentTypeResponseSchema(BaseModel):
    id: str = Field(..., description="Unique identifier of the Payment Type")
    title: str =  Field(..., description="Title of the payment type")
    payment_accounts : List[PaymentAccountResponseSchema]



