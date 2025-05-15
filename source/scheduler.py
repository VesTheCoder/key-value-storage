from sqlalchemy import select, delete
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from datetime import datetime
from aiohttp.web import Application
from typing import Dict

from models import KeyValue
from setup_db import scheduler_db_call


executors: Dict[str, AsyncIOExecutor] = {'default': AsyncIOExecutor()}
delete_record_timer: AsyncIOScheduler = AsyncIOScheduler(executors=executors)

async def start_scheduler(app: Application) -> None:
    """
    Starts the scheduler with the server startup.
    1. Checks for expired keys in the key-value storage and deletes those.
    2. Runs the scheduler daemon to schedule the tasks during the session.
    """
    await delete_expired_records()

    if not delete_record_timer.running:
        delete_record_timer.start()

async def delete_on_tll_timeout(key: str) -> None:
    """
    Deletes a single record on its TTL expiration.
    """
    async for db in scheduler_db_call():
        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
        record_found = record.scalar_one_or_none()
        if record_found:
            await db.delete(record_found)
            await db.commit()
    return None

async def delete_expired_records() -> None:
    """
    Deletes all expired records on server startup.
    """
    async for db in scheduler_db_call():
        await db.execute(delete(KeyValue).where(KeyValue.expiration_time <= datetime.now()))
        await db.commit()