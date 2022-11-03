from datetime import timedelta
import os

import bcrypt
from fastapi import APIRouter, BackgroundTasks, Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import EmailStr

from db import schemas, models
from db.database import database

from .models import Token
from . import utils

user_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/token")

@user_router.post("/create", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, backgroundtasks: BackgroundTasks):
    """
    Registration request.
    Args:
        user: form with user credentials - email, firstname, lastname and password.
        backgroundtasks: instance of BackgroundTasks class.
    Returns:
        User: model with user parameteres.
    """
    query_db_user = models.users.select().where(models.users.c.email == user.email)
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
    await utils.send_verify_mail(resp.email, "verify", "Account Verification", backgroundtasks)
    return resp

@user_router.post("/token", response_model=Token, status_code=status.HTTP_201_CREATED)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login request.
    Args:
        form_data: form with OAuth2 parameteres. Most important are username and password.
    Returns:
        token: dictionary with access token and its type.
    """
    user = await utils.user_authenticate(form_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token_expires = timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = await utils.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@user_router.get("/me", response_model=schemas.User, status_code=status.HTTP_200_OK)
async def retrieve_current_user(current_user: schemas.User = Depends(utils.get_current_active_user)):
    """ Request to get current user. """
    return current_user

@user_router.get("/verification", status_code=status.HTTP_200_OK)
async def email_verification(token: Token):
    """
    Email verification request. If user is disabled, changes this attribute to False.
    Args:
        token: JWT access token.
    Returns:
        JSON Response if successful.
    """
    user = await utils.get_current_user(token.access_token)
    if user and user.disabled:
        query_update = models.users.update().where(models.users.c.email == user.email).values(disabled=False)
        await database.execute(query_update)
        return {"Success": True}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"}
    )

@user_router.delete("/{user_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    query = models.users.delete().where(models.users.c.id == user_id)
    await database.execute(query)
    return {"Success": True}

@user_router.post("/reset/send", status_code=status.HTTP_200_OK)
async def send_reset_mail(bacgroundtasks: BackgroundTasks, email: EmailStr = Form()):
    await utils.send_mail(email, "reset", "Reset password.", bacgroundtasks)
    return {"Success": True}

@user_router.patch("/reset/new_password", status_code=status.HTTP_201_CREATED)
async def reset_password(token: str, new_password: str = Form()):
    user = await utils.get_current_user(token)
    hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())

    query = models.users.update().where(models.users.c.id == user.id).values(hashed_password=hashed_password.decode())
    await database.execute(query)
    return {"hashed_password": hashed_password}
