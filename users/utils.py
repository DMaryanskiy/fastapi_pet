from datetime import datetime, timedelta
import os

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError

from db import models, schemas
from db.database import database
from .models import TokenData

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

async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/v1/users/token"))):
    """ Function to get current user by its access token. """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])
        email: str = payload.get("sub") # getting email from token
        if not email:
            raise credentials_exception
        
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    query_user = models.users.select(models.users.c.email == token_data.email)
    user = await database.fetch_one(query_user) # getting user from db
    if not user:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """ Function to check whether user is activated or not. """
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")
    return current_user
