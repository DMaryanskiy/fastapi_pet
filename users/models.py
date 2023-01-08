from pydantic import BaseModel, EmailStr
from typing import Any


class Session(BaseModel):
    session: Any # should have been AsyncSession but OpenAPI can't show this type.

class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenData(BaseModel):
    email: EmailStr


class NewPassword(Token):
    new_password: str


class Success(BaseModel):
    success: bool
