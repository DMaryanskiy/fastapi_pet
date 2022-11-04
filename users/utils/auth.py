from datetime import datetime, timedelta
import os

import bcrypt
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from db import models, schemas
from db.database import database

async def row2dict(row) -> dict:
    """ Function to convert SQLAlchemy row to dictionary. """
    d = {}
    for column in row._result_columns:
        d[column[0]] = str(getattr(row, column[0]))
    
    return d

async def user_authenticate(form_data: OAuth2PasswordRequestForm) -> schemas.User | bool:
    """ Function to check whether user exists and its password is true. """
    query_user_model = models.users.select(models.users.c.email == form_data.username)
    user_model = await database.fetch_one(query_user_model)
    if not user_model:
        return False
    
    user = schemas.User(**(await row2dict(user_model))) # converting SQLAlchemy row to dict.
    # password checking
    if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode()):
        return False
    
    return user

async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """ Function to create access token """
    to_encode = data.copy() # copy of dictionary we need to encode
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"), algorithm=os.environ.get("ALGORITHM"))
    return encoded_jwt
