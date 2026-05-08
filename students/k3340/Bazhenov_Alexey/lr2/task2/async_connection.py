import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel


ENV_PATH = (
    Path(__file__).resolve().parents[2]
    / "lr1"
    / ".env"
)

load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

ASYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True
)


async def init_async_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
