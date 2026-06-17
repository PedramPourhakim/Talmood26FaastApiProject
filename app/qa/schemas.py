from pydantic import BaseModel,Field
from datetime import datetime

class BaseQASchema(BaseModel):
    question : str = Field(...,description="The question text")
    answer : str = Field(nullable=True,description="The answer text")
    rabbie_id : str = Field(...,description="The rabbie id")
    talmid_id : str = Field(...,description="The talmid id")

class CreateQASchema(BaseQASchema):
    pass

class UpdateQASchema(BaseQASchema):
    pass

class QAResponseSchema(BaseQASchema):
    id : str = Field(...,description='unique identifier')
    creation_date: datetime = Field(..., description="Date of creation of the person")