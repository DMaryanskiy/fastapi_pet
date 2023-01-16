import os

from databases.interfaces import Record
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncResult

from db import models, schemas

from ..models import Session

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(session: Session, token: str = Depends(OAuth2PasswordBearer(tokenUrl="api/v1/users/token"))) -> Record:
    """
    Function to get current user by its access token.
    Args:
        token: access token of current user.
        session: Pydantic model of AsyncSession object.
    Returns:
        Instance of SQLAlchemy Record class with user info.
    """
    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=[os.environ.get("ALGORITHM")])
        email: EmailStr = payload.get("sub") # getting email from token
        if not email:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception

    query_user = models.users.select(models.users.c.email == email)
    result: AsyncResult = await session.session.execute(query_user) # getting user from db
    user = result.one()
    if not user:
        raise credentials_exception
    
    return user

async def is_user_activated(token: str, session: Session) -> schemas.User:
    """
    Function to check whether user is activated or not.
    Args:
        token: access token of current user.
        session: Pydantic model of AsyncSession object.
    Returns:
        The same model if user is activated.
    """
    current_user: schemas.User = await get_current_user(session, token)
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user."
        )
    return current_user
