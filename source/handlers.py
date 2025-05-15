from aiohttp import web
from setup_db import client_db_call
from models import KeyValue
from sqlalchemy import select
from datetime import datetime, timedelta
from settings import TLL_DEFAULT
from scheduler import delete_record_timer, delete_on_tll_timeout
import json


routes = web.RouteTableDef()



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


@routes.put("/bulk")
async def bulk_operation(request):
    try:
        body = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"status": "Error", 
                                  "message": "JSON Body is invalid. No changes were made"}, 
                                  status=400)
    
    if not isinstance(body, list):
        return web.json_response({"status": "Error", 
                                  "message": "JSON Body must be a List. No changes were made"}, 
                                  status=400)

    valid_operations = []

    for operation in body:
        if not isinstance(operation, dict):
            return web.json_response({"status": "Error", 
                                      "message": "JSON Body is wrong format. No changes were made"}, 
                                      status=400)
        
        method: str | None = operation.get("method")
        if not method:
            return web.json_response({"status": "Error", 
                                      "message": "JSON Body lacks a 'method'. No changes were made"}, 
                                      status=400)
        
        method = method.upper()
        if method not in ("GET", "PUT", "DELETE"):
            return web.json_response({"status": "Error", 
                                      "message": "JSON Body 'method' is incorrect. No changes were made"}, 
                                      status=400)

        key: str| None = operation.get("key")
        if not key:
            return web.json_response({"status": "Error", 
                                      "message": "JSON Body 'key' is incorrect. No changes were made"}, 
                                      status=400)
        
        if method == "PUT":
            value: str | None = operation.get("value")
            if not value:
                return web.json_response({"status": "Error", 
                                          "message": "JSON Body 'value' is invalid (method PUT). No changes were made"}, 
                                          status=400)

            tll: str | None = operation.get("tll")
            if tll:
                try:
                    tll = int(tll)
                except (NameError, ValueError, TypeError):    
                    return web.json_response({"status": "Error",
                                              "message": "JSON Body 'tll' is invalid (method PUT). No changes were made"}, 
                                              status=400)
            valid_operations.append({"method": method, "key": key, "value": value, "tll": tll})
        else:
            valid_operations.append({"method": method, "key": key})

# body = [{"method": "put", "key": "key1", "value": "please work", "tll": "1"}, {"method": "delete", "key": "key1"}]
