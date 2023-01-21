from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from db import models, schemas
from db.database import get_session, session_commit
from users.services import oauth2_scheme
from users.models import Session
from users.utils.get_current_user import is_user_activated

from .utils import get_tasks

todolist_router = APIRouter()

@todolist_router.post("/create", response_model=schemas.List, status_code=status.HTTP_201_CREATED)
async def create_list(
    todolist: schemas.ListCreate,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    """
    Function to create todolist.
    Args:
        todolist: form with data for creation (name).
        token: token of currently logged in user.
        session: instance of current session with database.
    Returns:
        JSON with full todolist data (id, name, user_id, task's list)
    """
    
    user = await is_user_activated(token=token, session=Session(session=session))

    todolist_data = {
        "name": todolist.name,
        "user_id": user._data[0]
    }

    query_todolist_create = models.todolist.insert().values(**todolist_data)
    result: AsyncResult = await session.execute(query_todolist_create)
    await session_commit(
        Exception,
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong.",
            headers={"WWW-Authenticate": "Bearer"}
        ),
        session
    )
    last_record_id: int = result.inserted_primary_key[0] # creates new record and returns its id.
    resp = schemas.List(**todolist_data, id=last_record_id, tasks=[])
    return resp

@todolist_router.get("", response_model=list[schemas.List], status_code=status.HTTP_200_OK)
async def get_lists(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Function to get all lists of current authenticated user.
    Args:
        token: token of currently logged in user.
        session: instance of current session with database.
    Returns:
        List of JSONa with full todolist data (id, name, user_id, task's list)
    """
    user = await is_user_activated(token=token, session=Session(session=session))

    query_get_lists = models.todolist.select().where(models.todolist.c.user_id == user.id)
    result: AsyncResult = await session.execute(query_get_lists)
    lists = result.all()
    resp = [schemas.List(**item._asdict(), tasks=await get_tasks(item._asdict()["id"], session)) for item in lists]
    return resp

@todolist_router.get("/{list_id}", response_model=schemas.List, status_code=status.HTTP_200_OK)
async def retrieve_list(
    list_id: int,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Function to retrieve a list with specific id.
    Args:
        list_id: id of a searched list.
        token: token of currently logged in user.
        session: instance of current session with database.
    Returns:
        JSON with full todolist data (id, name, user_id, task's list)
    """
    user = await is_user_activated(token=token, session=Session(session=session))

    query_retrieve = models.todolist.select().where(models.todolist.c.id == list_id)
    result_list: AsyncResult = await session.execute(query_retrieve)
    list_item = result_list.one()

    tasks_data = await get_tasks(list_id=list_id, session=session)

    resp = schemas.List(**list_item._asdict(), tasks=tasks_data)
    if user.id != resp.user_id: # check whether user is an owner of the list.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This list belongs to other user."
        )
    return resp

@todolist_router.delete("/{list_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: int,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Function to delete a list with specific id.
    Args:
        list_id: id of a searched list.
        token: token of currently logged in user.
        session: instance of current session with database.
    """
    # retrieve a list which needs to be deleted with verification whether a list belongs to currently authenticated user.
    list_item = await retrieve_list(list_id, token, session)

    query_delete = models.todolist.delete().where(models.todolist.c.id == list_item.id)
    await session.execute(query_delete)
    await session_commit(
        Exception,
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong.",
            headers={"WWW-Authenticate": "Bearer"}
        ),
        session
    )
