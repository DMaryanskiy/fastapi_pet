import os
from typing import AsyncIterable

import sqlalchemy
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.curdir, '.env'))

SQLACHEMY_DATABASE_URL = os.environ.get("DB_URL")

engine = create_async_engine(SQLACHEMY_DATABASE_URL, future=True)
metadata = sqlalchemy.MetaData()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

async def get_session() -> AsyncIterable[AsyncSession]:
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session

async def session_commit(error, exception: HTTPException, session: AsyncSession) -> None:
    try:
        await session.commit()
    except error as _:
        await session.rollback()
        raise exception
