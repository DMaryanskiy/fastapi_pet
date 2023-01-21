from sqlalchemy.ext.asyncio import AsyncSession, AsyncResult

from db import models, schemas

async def get_tasks(
    list_id: int,
    session: AsyncSession
) -> list[schemas.Task]:
    query_tasks_ids = models.task.select().join(models.task_list, models.task.c.id == models.task_list.c.task_id).where(models.task_list.c.list_id == list_id)
    result_tasks: AsyncResult = await session.execute(query_tasks_ids)
    tasks = result_tasks.all()
    return [schemas.Task(**item._asdict()) for item in tasks]
