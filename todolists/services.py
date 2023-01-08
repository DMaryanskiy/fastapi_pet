from fastapi import APIRouter

from db import models, schemas
from db.database import get_session
todolist_router = APIRouter()

@todolist_router.post("/create", response_model=schemas.List)
async def create_list(todolist: schemas.ListCreate):
    pass
    # todolist_data = {
    #     "name": todolist.name,
    #     "user": todolist.user
    # }

    # query_todolist_create = models.todolist.insert().values(**todolist_data)
    # last_record_id = await database.execute(query_todolist_create)
    # resp = schemas.List(**todolist_data, id=last_record_id, tasks=[])
    # return resp
