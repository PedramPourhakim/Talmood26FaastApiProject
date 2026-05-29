from datetime import datetime
from pydantic import BaseModel, Field,EmailStr


class BasePersonSchema(BaseModel):
    email: str = EmailStr()
    phone: str = Field(...,max_length=11)

class CreatePersonSchema(BasePersonSchema):
    pass

class UpdatePersonSchema(BasePersonSchema):
    pass

class LoginPersonSchema(BasePersonSchema):
    verification_code : int = Field(...,max_length=4)

class PersonResponseSchema(BasePersonSchema):
    id: str = Field(..., description="Unique identifier of the person")
    creation_date: datetime = Field(..., description="Date of creation of the person")
