from datetime import datetime
from pydantic import BaseModel,Field


class BaseParashahSchema(BaseModel):
    title: str = Field(...,max_length=255)
    description: str

class CreateParashahSchema(BaseParashahSchema):
    pass

class UpdateParashahSchema(BaseParashahSchema):
    pass

class ResponseParashahSchema(BaseParashahSchema):
    id: str = Field(..., description="Unique identifier of the Parashah")
    creation_date: datetime = Field(..., description="Date of creation of the Parashah")