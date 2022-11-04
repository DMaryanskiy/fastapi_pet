import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import EmailStr

from db import models, schemas
from db.database import database

from ..models import TokenData

async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/v1/users/token"))):
    """ Function to get current user by its access token. """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])
        email: EmailStr = payload.get("sub") # getting email from token
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
