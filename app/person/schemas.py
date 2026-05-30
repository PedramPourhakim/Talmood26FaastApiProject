from datetime import datetime
from pydantic import BaseModel, Field,EmailStr


class BasePersonSchema(BaseModel):
    name: str = Field(max_length=255)
    family_name: str = Field(max_length=512)
    is_admin: bool
    is_rabbie : bool

class CreatePersonSchema(BasePersonSchema):
    pass

class UpdatePersonSchema(BasePersonSchema):
    pass


class PersonResponseSchema(BasePersonSchema):
    id: str = Field(..., description="Unique identifier of the person")
    creation_date: datetime = Field(..., description="Date of creation of the person")
