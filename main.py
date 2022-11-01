from fastapi import FastAPI

from routers.routers import api_router

app = FastAPI(
    title="Pet ToDo List using FastAPI."
    description="As a pet project I decided to develop ToDo List for my own usage."
)

app.include_router(api_router)
