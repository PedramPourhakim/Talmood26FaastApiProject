from pydantic import BaseModel, Field

class PaymentAccountResponseSchema(BaseModel):
    id: str = Field(..., description="Unique identifier of the Payment Account")
    account_title: str = Field(...,description="Name of the Payment Account")