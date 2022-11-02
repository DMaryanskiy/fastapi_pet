from datetime import datetime, timedelta
import os

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from db import crud, schemas
from db.database import get_db
from .schemas import TokenData

async def row2dict(row) -> dict:
    """ Function to convert SQLAlchemy row to dictionary. """
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    
    return d

async def user_authenticate(form_data: OAuth2PasswordRequestForm, db: Session) -> schemas.User | bool:
    """ Function to check whether user exists and its password is true. """
    user_model = crud.get_user_by_email(db, email=form_data.username)
    if not user_model:
        return False
    user = schemas.User(**(await row2dict(user_model))) # converting SQLAlchemy row to dict.
    if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode()):
        return False
    return user

async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """ Function to create access token """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ.get("SECRET_KEY"), algorithm=os.environ.get("ALGORITHM"))
    return encoded_jwt

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/v1/users/token"))):
    """ Function to get current user by its access token. """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db=db, email=token_data.email)
    if not user:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user.")
    return current_user
