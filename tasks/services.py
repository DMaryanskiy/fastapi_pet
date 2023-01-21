from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from db import models, schemas
from db.database import get_session, session_commit

from todolists.services import retrieve_list

from users.services import oauth2_scheme

task_router = APIRouter()

@task_router.post("/{list_id}/create", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    list_id: int,
    task: schemas.TaskCreate,
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    """
    Function to create new task.
    Args:
        list_id: id of a list to which task will be added.
        task: form with task data.
        token: token of currently logged in user.
        session: instance of current session with database.
    Returns:
        JSON with created task data.
    """
    # retrieve a list to which task will be added with verification whether a list belongs to currently authenticated user.
    list_item = await retrieve_list(list_id, token, session)

    task_data = {
        "task": task.task,
        "time": task.time,
        "description": task.description,
        "done": task.done,
    }

    query_task_create = models.task.insert().values(**task_data)
    result: AsyncResult = await session.execute(query_task_create)
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
    
    # values and query for intermediate table to provide MtM relation.
    task_list_data = {
        "list_id": list_item.id,
        "task_id": last_record_id
    }

    query_task_list_create = models.task_list.insert().values(**task_list_data)
    await session.execute(query_task_list_create)
    await session_commit(
        Exception,
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong.",
            headers={"WWW-Authenticate": "Bearer"}
        ),
        session
    )

    resp = schemas.Task(**task_data, id=last_record_id)
    return resp

# TODO: Implement dropdown list for existing tasks.

@task_router.patch("/{task_id}/complete", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
async def complete_task(
    task_id: int,
    _: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
):
    """
    Function to mark task as completed.
    Args:
        task_id: id of a task which we've completed.
        _: token of currently logged in user.
        session: instance of current session with database.
    Returns:
        JSON with created task data.
    """

    query_complete = models.task.update().where(models.task.c.id == task_id).values(done=True)
    await session.execute(query_complete)
    await session_commit(
        Exception,
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong.",
            headers={"WWW-Authenticate": "Bearer"}
        ),
        session
    )

    query_select = models.task.select().where(models.task.c.id == task_id)
    result: AsyncResult = await session.execute(query_select)
    completed_task = result.one()
    resp = schemas.Task(**completed_task._asdict())
    return resp

@task_router.delete("/{task_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    _: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Function to delete a task.
    Args:
        task_id: id of a task which we've completed.
        _: token of currently logged in user.
        session: instance of current session with database.
    """
    query_delete = models.task.delete().where(models.task.c.id == task_id)
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

@task_router.put("/{task_id}/edit", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
async def edit_task(
    task_id: int,
    new_task: schemas.TaskCreate,
    _: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
):
    """
    Function to edit task.
    Args:
        task_id: id of a task which we've completed.
        new_task: form with edited task data.
        _: token of currently logged in user.
        session: instance of current session with database.
    Returns:
        JSON with created task data.
    """
    task_data = {
        "task": new_task.task,
        "time": new_task.time,
        "description": new_task.description
    }

    query_update = models.task.update().where(models.task.c.id == task_id).values(**task_data)
    await session.execute(query_update)
    await session_commit(
        Exception,
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong.",
            headers={"WWW-Authenticate": "Bearer"}
        ),
        session
    )

    query_resp = models.task.select().where(models.task.c.id == task_id)
    result: AsyncResult = await session.execute(query_resp)
    task = result.one()
    resp = schemas.Task(**task._asdict())
    return resp
