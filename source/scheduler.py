from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from models import KeyValue
from sqlalchemy import select
from setup_db import scheduler_db_call

executors = {'default': AsyncIOExecutor()}
delete_record_timer = AsyncIOScheduler(executors=executors)

async def start_scheduler(app):
    if not delete_record_timer.running:
        delete_record_timer.start()

async def delete_on_tll_timeout(key):
    async for db in scheduler_db_call():
        result = await db.execute(select(KeyValue).where(KeyValue.key == key))
        record = result.scalar_one_or_none()
        if record:
            await db.delete(record)
            await db.commit()
    return None