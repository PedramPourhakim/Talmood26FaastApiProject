from datetime import datetime
from pydantic import BaseModel, Field,FilePath


class BasePersonSchema(BaseModel):
    name: str = Field(max_length=255)
    family_name: str = Field(max_length=512)
    image : str | None = None
    is_admin: bool
    is_rabbie : bool

class CreatePersonSchema(BasePersonSchema):
    pass

class UpdatePersonSchema(BasePersonSchema):
    pass


class PersonResponseSchema(BasePersonSchema):
    id: str = Field(..., description="Unique identifier of the person")
    creation_date: datetime = Field(..., description="Date of creation of the person")
