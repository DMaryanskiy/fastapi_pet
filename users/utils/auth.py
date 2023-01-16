import os
from datetime import datetime, timedelta

import bcrypt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncResult

from db import models, schemas
from ..models import Session

async def user_authenticate(
        form_data: OAuth2PasswordRequestForm,
        session: Session
    ) -> schemas.User:
    """
    Function to check whether user exists and its password is true.
    Args:
        form_data: username and password from OAuth2 form.
    Returns:
        Pydantic model of User
    """
    query_user_model = models.users.select(models.users.c.email == form_data.username)
    result: AsyncResult = await session.session.execute(query_user_model)
    user_model = result.one()
    if not user_model:
        raise HTTPException(status_code=400, detail=f"No user with {form_data.username} found")
    
    user = schemas.User(**user_model._asdict())
    # password checking
    if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode()):
        raise HTTPException(
            status_code=400,
            detail=f"No user with {form_data.username} found"
        )

    
    return user

async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Function to create access token.
    Args:
        data: dictionary with token data.
        expires_delta: time before token expires.
    Returns:
        Encoded JWT token.
    """
    to_encode = data.copy() # copy of dictionary we need to encode
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"), algorithm=os.environ.get("ALGORITHM"))
    return encoded_jwt
