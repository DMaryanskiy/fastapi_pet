from datetime import timedelta
import os

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from db import schemas, models
from db.database import database

from .models import Token
from .utils import user_authenticate, create_access_token, get_current_active_user

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token")

@user_router.post("/create", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate):
    """
    Registration request.
    Args:
        user: form with user credentials - email, firstname, lastname and password
    """
    query_db_user = models.users.select(models.users.c.email == user.email)
    db_user = await database.execute(query_db_user)
    if db_user:
        raise HTTPException(status_code=400, detail="User with this email already exists.")

    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
    user_data = {
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "hashed_password": hashed_password.decode(),
        "disabled": True
    }

    query_user_create = models.users.insert().values(**user_data)
    last_record_id = await database.execute(query_user_create) # creates new record and returns its id.
    resp = schemas.User(**user_data, id=last_record_id)
    return resp

@user_router.post("/token", response_model=Token, status_code=status.HTTP_201_CREATED)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login request.
    Args:
        form_data: form with OAuth2 parameteres. Most important are username and password.
        db: instance of connection to database.
    Returns:
        token: dictionary with access token and its type.
    """
    user = await user_authenticate(form_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = await create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/me", response_model=schemas.User, status_code=status.HTTP_200_OK)
async def retrieve_current_user(current_user: schemas.User = Depends(get_current_active_user)):
    """ Request to get current user. """
    return current_user
