from fastapi import FastAPI

from routers.routers import api_router

app = FastAPI(
    title="Pet ToDoList using FastAPI."
)

app.include_router(api_router)
