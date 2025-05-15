from aiohttp import web
from sqlalchemy import select
from datetime import datetime, timedelta
import json
from typing import Any, Dict, List, Optional, Union

from settings import TLL_DEFAULT
from setup_db import client_db_call
from models import KeyValue
from scheduler import delete_record_timer, delete_on_tll_timeout

routes = web.RouteTableDef()





@routes.delete("/{key}")
async def delete_record(request: web.Request) -> web.Response:
    """
    Deletes a key-value record by key.
    Check README.md to know how to call API handlers correctly.
    """
    key: str = request.match_info.get("key")

    async for db in client_db_call():
        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
        record_found: Optional[KeyValue] = record.scalar_one_or_none()

        if record_found:
            await db.delete(record_found)
            await db.commit()
            return web.json_response({"status": "Success",
                                      "message": f"Record with the key '{key}' deleted"},
                                      status=200)
        else:
            return web.json_response({"status": "Error",
                                      "message": f"Record with the key '{key}' not found"},
                                      status=404)





@routes.get("/{key}")
async def get_record(request: web.Request) -> web.Response:
    """
    Retrieves a key-value record by key.
    Handles expired records by deleting them.
    Check README.md to know how to call API handlers correctly.
    """
    key: str = request.match_info.get("key")

    async for db in client_db_call():
        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
        record_found: Optional[KeyValue] = record.scalar_one_or_none()

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
async def add_record(request: web.Request) -> web.Response:
    """
    Adds a new key-value record.
    Check README.md to know how to call API handlers correctly.
    """
    key: str = request.match_info.get("key")

    try:
        body: Dict[str, Any] = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"status": "Error",
                                  "message": "JSON Body is invalid. No changes were made"},
                                  status=400)

    try:
        value: Any = body["value"]
    except KeyError:
        return web.json_response({"status": "Error",
                                  "message": "JSON Body misses the 'value' attribute. No changes were made"},
                                  status=400)

    tll: Optional[Union[str, int]] = body.get("tll")
    expiration_time: datetime
    if tll is not None:
        try:
            tll: int = int(tll)
            expiration_time = datetime.now() + timedelta(minutes=tll)
        except (ValueError, TypeError):
            return web.json_response({"status": "Error",
                                      "message": "TLL is invalid. No changes were made"},
                                      status=400)
    else:
        expiration_time = datetime.now() + timedelta(minutes=TLL_DEFAULT)

    async for db in client_db_call():
        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
        record_found: Optional[KeyValue] = record.scalar_one_or_none()

        if record_found:
            return web.json_response({"status": "Error",
                                      "message": f"Record with the key '{key}' already exists and can not be modified"},
                                      status=400)
        else:
            record = KeyValue(key=key, value=value, expiration_time=expiration_time)
            db.add(record)
            await db.commit()

            delete_record_timer.add_job(delete_on_tll_timeout, 'date', run_date=expiration_time, args=[key])

            return web.json_response({"status": "Success",
                                      "message": f"Record with the key '{key}' was made successfully"},
                                      status=200)





@routes.put("/bulk")
async def bulk_operation(request: web.Request) -> web.Response:
    """
    Handles bulk GET, PUT, and DELETE operations.
    Processes a list of operations in a single request.
    Check README.md to know how to call API handlers correctly.
    """
    try:
        body: List[Dict[str, Any]] = await request.json()
    except json.JSONDecodeError:
        return web.json_response({"status": "Error",
                                  "message": "JSON Body is invalid. No changes were made"},
                                  status=400)

    if not isinstance(body, list):
        return web.json_response({"status": "Error",
                                  "message": "JSON Body must be a List. No changes were made"},
                                  status=400)

    valid_operations: List[Dict[str, Any]] = []


    for operation in body:
        if not isinstance(operation, dict):
            return web.json_response({"status": "Error",
                                      "message": "JSON Body is wrong format. No changes were made"},
                                      status=400)

        method: Optional[str] = operation.get("method")
        if not method:
            return web.json_response({"status": "Error",
                                      "message": "JSON Body lacks a 'method'. No changes were made"},
                                      status=400)

        method = method.upper()
        if method not in ("GET", "PUT", "DELETE"):
            return web.json_response({"status": "Error",
                                      "message": "JSON Body 'method' is incorrect. No changes were made"},
                                      status=400)

        key: Optional[str] = operation.get("key")
        if not key:
            return web.json_response({"status": "Error",
                                      "message": "JSON Body 'key' is incorrect. No changes were made"},
                                      status=400)

        if method == "PUT":
            value: Optional[Any] = operation.get("value")
            if not value:
                return web.json_response({"status": "Error",
                                          "message": "JSON Body 'value' is invalid (method PUT). No changes were made"},
                                          status=400)

            tll: Optional[Union[str, int]] = operation.get("tll")
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


    async for db in client_db_call():
            errors: List[Dict[str, Any]] = []
            tll_timers: List[tuple[datetime, str]] = []
            successfull_results: List[Dict[str, Any]] = []

            for operation in valid_operations:
                    method: str = operation["method"]
                    key: str = operation["key"]

                    if method == "GET":
                        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
                        record_found: Optional[KeyValue] = record.scalar_one_or_none()
                        if not record_found:
                            errors.append({"key": key, "result": f"Record with the key '{key}' does not exists"})
                        elif record_found.expiration_time and record_found.expiration_time < datetime.now():
                            await db.delete(record_found)
                            errors.append({"key": key, "result": f"Record with the key '{key}' has expired"})
                        else:
                            successfull_results.append({"key": key, "value": record_found.value})

                    if method == "DELETE":
                        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
                        record_found: Optional[KeyValue] = record.scalar_one_or_none()

                        if not record_found:
                            errors.append({"key": key, "result": f"Record with the key '{key}' does not exists"})
                        else:
                            await db.delete(record_found)
                            successfull_results.append({"key": key, "result": "deleted successfully"})

                    if method == "PUT":
                        record = await db.execute(select(KeyValue).where(KeyValue.key == key))
                        record_found: Optional[KeyValue] = record.scalar_one_or_none()

                        if record_found:
                            errors.append({"key": key,
                                           "result": f"Record with the key '{key}' already exists and can not be modified"})
                        else:
                            tll: Optional[int]  = operation.get("tll")
                            if not tll:
                                tll: Optional[int] = TLL_DEFAULT
                            expiration_time = datetime.now() + timedelta(minutes=tll)

                            record = KeyValue(key=key, value=value, expiration_time=expiration_time)
                            db.add(record)
                            tll_timers.append((expiration_time, key))
                            successfull_results.append({"key": key, "result": "added successfully"})

            if errors:
                    await db.rollback()
                    return web.json_response({"status": "Error",
                                              "message": "Not all operations were correct. No changes were made.",
                                              "details": errors},
                                              status=400)
            else:
                    await db.commit()
                    for expiration_time, key in tll_timers:
                        delete_record_timer.add_job(delete_on_tll_timeout, 'date', run_date=expiration_time, args=[key])
                    return web.json_response({"status": "Success",
                                              "message": "All operations completed. Changes saved.",
                                              "details": successfull_results},
                                              status=200)     
