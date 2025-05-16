from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncIterator
from aiohttp.web import Application

from settings import DB_URL

engine: AsyncEngine = create_async_engine(DB_URL)

session_client: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)
session_scheduler: async_sessionmaker[AsyncSession] = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """
    Base class for declarative models.
    Used to be inherited by your custom models.
    """
    pass

async def init_database(app: Application) -> None:
    """
    Initializes the database tables if they don't exist already.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return None

async def client_db_call() -> AsyncIterator[AsyncSession]:
    """
    Provides an asynchronous database session for client operations.
    Any database operations within "async for db in client_db_call()" would be
    processed through yield and the connection would be automatically closed in the
    "finally" block.
    """
    db: AsyncSession = session_client()
    try:
        yield db
    finally:
        await db.close()

async def scheduler_db_call() -> AsyncIterator[AsyncSession]:
    """
    Provides an asynchronous database session for scheduler operations.
    Resommended to use as "async for db in client_db_call()".
    The DB connection would be automatically closed in the "finally" block.
    """
    db: AsyncSession = session_scheduler()
    try:
        yield db
    finally:
        await db.close()
