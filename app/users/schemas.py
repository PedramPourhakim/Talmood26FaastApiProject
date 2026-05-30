from pydantic import BaseModel,Field,EmailStr
from datetime import datetime

class UserLoginSchema(BaseModel):
    email :str= EmailStr
    verification_code: int = Field(description="a Verification code that sent to user")

class UserRegisterSchema(BaseModel):
    email : str = EmailStr
    phone :str = Field(...,max_length=11,description="phone number of the user")
    person_id : str = Field(...,max_length=36, description="person id of the user")

class UserUpdateSchema(UserRegisterSchema):
    pass

class UserResponseSchema(UserRegisterSchema):
    id: str = Field(..., description="Unique identifier of the person")
    creation_date: datetime = Field(..., description="Date of creation of the person")


class UserRefreshTokenSchema(BaseModel):
    refresh_token: str = Field(...,description="refresh token of the user")