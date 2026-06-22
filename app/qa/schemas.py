from pydantic import BaseModel,Field
from datetime import datetime
from person.schemas import PersonResponseSchema

class BaseQASchema(BaseModel):
    question : str = Field(...,description="The question text")
    answer : str | None = Field(description="The answer text")
    rabbie_id: str = Field(nullable=True, description="The rabbie id")
    talmid_id: str = Field(nullable=True, description="The talmid id")
    is_answered: bool = Field(nullable=True, description="filter question based on is answered")

class CreateQASchema(BaseQASchema):
    pass


class UpdateQASchema(BaseQASchema):
    pass


class PersonShortSchema(BaseModel):
    name: str
    family_name: str

class QAResponseSchema(BaseQASchema):
    id : str = Field(...,description='unique identifier')
    creation_date: datetime = Field(..., description="Date of creation of the person")
    rabbie: PersonShortSchema | None = None
    talmid: PersonShortSchema | None = None

    model_config = {
        "from_attributes": True
    }