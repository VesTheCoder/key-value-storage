from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import settings

engine = create_async_engine(settings.DB_URL)

session_client = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)
session_scheduler = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


async def client_db_call():
    db = session_client()
    try:
        yield db
    finally:
        await db.close()

async def scheduler_db_call():
    db = session_scheduler()
    try:
        yield db
    finally:
        await db.close()
