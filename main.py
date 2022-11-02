from fastapi import FastAPI

from db.database import database
from routers.routers import api_router

app = FastAPI(
    title="Pet ToDo List using FastAPI.",
    description="As a pet project I decided to develop ToDo List for my own usage."
)

app.include_router(api_router)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
