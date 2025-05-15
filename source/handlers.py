from aiohttp import web
from setup_db import engine, Base, client_db_call
from models import KeyValue
from sqlalchemy import select
from datetime import datetime, timedelta
from settings import TLL_DEFAULT
from scheduler import delete_record_timer, delete_on_tll_timeout
import json


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
            return web.json_response({"status": "Sucess", 
                                      "message": f"Record with the key '{key}' deleted"},
                                      status=200)
        else:
            return web.json_response({"status": "Error", 
                                      "message": f"Record with the key '{key}' not found"}, 
                                      status=404)
        
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
                return web.json_response({"status": "Error", 
                                          "message": f"Record with the key '{key}' not found"},
                                          status=404)
            else:
                return web.json_response({"key": record_found.key, "value": record_found.value})    
        return web.json_response({"status": "Error", 
                                  "message": f"Record with the key '{key}' not found"}, 
                                  status=404)

@routes.put("/{key}")
async def add_record(request):
    key = request.match_info.get("key")

    try:
        body = await request.json()
        print(body)
    except json.JSONDecodeError:
        return web.json_response({"status": "Error", 
                                  "message": "JSON Body is invalid. No changes were made"}, 
                                  status=400)
    
    try:
        value = body["value"]
    except NameError:
        return web.json_response({"status": "Error", 
                                  "message": "JSON Body misses the 'value' attribute. No changes were made"}, 
                                  status=400)

    tll = body.get("tll")
    if tll:
        try:
            tll = int(tll)
            expiration_time = datetime.now() + timedelta(minutes=tll)
        except (NameError, ValueError, TypeError):    
            return web.json_response({"status": "Error",
                                      "message": "TLL is invalid. No changes were made"}, 
                                      status=400)
    else:
        expiration_time = datetime.now() + timedelta(minutes=TLL_DEFAULT)

    async for db in client_db_call():
        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
        record_found = record.scalar_one_or_none()

        if record_found:
            return web.json_response({"status": "Error",
                                      "message": f"Record with the key '{key}' already exists and can not be modified"}, 
                                      status=400)
        else:
            record = KeyValue(key=key, value=value, expiration_time=expiration_time)
            db.add(record)
            await db.commit()

            delete_record_timer.add_job(delete_on_tll_timeout, 'date', run_date=expiration_time, args=[key])

            return web.json_response({"status": "Sucess",
                                      "message": f"Record with the key '{key}' was made successfully"}, 
                                      status=200)
