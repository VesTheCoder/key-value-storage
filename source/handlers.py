from aiohttp import web
from setup_db import engine, Base
from models import KeyValue
from setup_db import client_db_call
from sqlalchemy import select
from datetime import datetime


routes = web.RouteTableDef()


@routes.get("/")
async def init_db(request):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return web.Response(text="Database created, yey!")

@routes.get("/add_instance")
async def add_instance(request):
    async for db in client_db_call():
        dbinstance = KeyValue(key="key1", value="test_value", expiration_time=None)
        db.add(dbinstance)
        await db.commit()
    return web.json_response({"status": "Database entry created"})

@routes.delete("/{key}")
async def delete_record(request):
    key = request.match_info.get("key")

    async for db in client_db_call():
        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
        record_found = record.scalar_one_or_none()

        if record_found:
            await db.delete(record_found)
            await db.commit()
            return web.json_response({"status": f"Record with the key '{key}' deleted"})
        else:
            return web.json_response({"status": f"Record with the key '{key}' not found"}, status=404)
        
@routes.get("/{key}")
async def get_record(request):
    key = request.match_info.get("key")

    async for db in client_db_call():
        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
        record_found = record.scalar_one_or_none()

        if record_found:
            if record_found.expiration_time and record_found.expiration_time < datetime.now():
                await db.delete(record_found)
                await db.commit()
                return web.json_response({"status": f"Record with the key '{key}' not found"}, status=404)
            else:
                return web.json_response({"key": record_found.key, "value": record_found.value})    
        return web.json_response({"status": f"Record with the key '{key}' not found"}, status=404)
