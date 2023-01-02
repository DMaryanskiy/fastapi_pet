from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenData(BaseModel):
    email: EmailStr


class NewPassword(Token):
    new_password: str


class Success(BaseModel):
    success: bool
