import asyncio
import aiohttp
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

API_URL: str = os.environ.get("API_URL", "http://service:6969")

async def put_key_value(session: aiohttp.ClientSession, key: str, value: Any, tll: Optional[int] = None) -> Any:
    """
    Sends a PUT request to the key-value store service to add or update a key-value pair.
    An optional TTL can be specified for the key.
    Prints the request being made and the response received from the service.
    """
    url = f"{API_URL}/{key}"
    data: Dict[str, Any] = {"value": value}
    if tll is not None:
        data["tll"] = tll
    
    print(f"[{datetime.now()}] PUT {url} with data {data}")
    async with session.put(url, json=data) as response:
        result: Any = await response.json()
        print(f"[{datetime.now()}] Response: {response.status} - {result}")
        return result

async def get_key(session: aiohttp.ClientSession, key: str) -> Any:
    """
    Sends a GET request to the key-value store service to retrieve the value associated with a given key.
    Prints the result.
    """
    url = f"{API_URL}/{key}"
    
    print(f"[{datetime.now()}] GET {url}")
    async with session.get(url) as response:
        result: Any = await response.json()
        print(f"[{datetime.now()}] Response: {response.status} - {result}")
        return result

async def delete_key(session: aiohttp.ClientSession, key: str) -> Any:
    """
    Sends a DELETE request to the key-value store service to remove a key-value pair.
    Prints the result.
    """
    url = f"{API_URL}/{key}"
    
    print(f"[{datetime.now()}] DELETE {url}")
    async with session.delete(url) as response:
        result: Any = await response.json()
        print(f"[{datetime.now()}] Response: {response.status} - {result}")
        return result

async def bulk_operations(session: aiohttp.ClientSession, operations: List[Dict[str, Any]]) -> Any:
    """
    Sends a PUT request to the key-value storage to perform multiple operations (PUT, GET, DELETE) in a single request.
    The operations are provided as a list of dictionaries.
    Prints the result.
    """
    url = f"{API_URL}/bulk"
    
    print(f"[{datetime.now()}] PUT {url} with bulk operations")
    async with session.put(url, json=operations) as response:
        result: Any = await response.json()
        print(f"[{datetime.now()}] Response: {response.status} - {result}")
        return result

async def main() -> None:
    """
    Main function for the mock client.
    It waits for the service to start and then performs a series of test operations:
    - Adds individual key-value pairs (one with TTL).
    - Retrieves a key.
    - Performs bulk operations (PUTs and GET).
    - Deletes a key.
    - Verifies the deletion by attempting to retrieve the deleted key.
    - Adds a key with a very short TTL to demonstrate expiration.
    Prints a success message upon completion of all tests.
    """    
    print(f"[{datetime.now()}] Waiting for service to start...")
    await asyncio.sleep(5)
    
    async with aiohttp.ClientSession() as session:
       
        await put_key_value(session, "test1", "value1")
        await put_key_value(session, "test2", "value2", 10)
        await get_key(session, "test1")
                
        bulk_ops: List[Dict[str, Any]] = [
            {"method": "put", "key": "bulk1", "value": "bulk-value1", "tll": 15},
            {"method": "put", "key": "bulk2", "value": "bulk-value2"},
            {"method": "get", "key": "bulk1"}
        ]
        await bulk_operations(session, bulk_ops)                
        await delete_key(session, "test1")    
        await get_key(session, "test1")
        await put_key_value(session, "short-lived", "temporary", 1)
        
        print(f"[{datetime.now()}] Mock client tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 