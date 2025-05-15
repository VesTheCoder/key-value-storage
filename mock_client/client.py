import asyncio
import aiohttp
import os
from datetime import datetime

# Get environment variables
API_URL = os.environ.get("API_URL", "http://service:6969")

async def put_key_value(session, key, value, tll=None):
    """Add a new key-value pair"""
    url = f"{API_URL}/{key}"
    data = {"value": value}
    if tll is not None:
        data["tll"] = tll
    
    print(f"[{datetime.now()}] PUT {url} with data {data}")
    async with session.put(url, json=data) as response:
        result = await response.json()
        print(f"[{datetime.now()}] Response: {response.status} - {result}")
        return result

async def get_key(session, key):
    """Get a value by key"""
    url = f"{API_URL}/{key}"
    
    print(f"[{datetime.now()}] GET {url}")
    async with session.get(url) as response:
        result = await response.json()
        print(f"[{datetime.now()}] Response: {response.status} - {result}")
        return result

async def delete_key(session, key):
    """Delete a key-value pair"""
    url = f"{API_URL}/{key}"
    
    print(f"[{datetime.now()}] DELETE {url}")
    async with session.delete(url) as response:
        result = await response.json()
        print(f"[{datetime.now()}] Response: {response.status} - {result}")
        return result

async def bulk_operations(session, operations):
    """Perform bulk operations"""
    url = f"{API_URL}/bulk"
    
    print(f"[{datetime.now()}] PUT {url} with bulk operations")
    async with session.put(url, json=operations) as response:
        result = await response.json()
        print(f"[{datetime.now()}] Response: {response.status} - {result}")
        return result

async def main():
    # Wait for the service to start
    print(f"[{datetime.now()}] Waiting for service to start...")
    await asyncio.sleep(5)
    
    async with aiohttp.ClientSession() as session:
        # Test single operations
        await put_key_value(session, "test1", "value1")
        await put_key_value(session, "test2", "value2", 10)  # 10 minutes TTL
        await get_key(session, "test1")
        
        # Test bulk operations
        bulk_ops = [
            {"method": "put", "key": "bulk1", "value": "bulk-value1", "tll": 15},
            {"method": "put", "key": "bulk2", "value": "bulk-value2"},
            {"method": "get", "key": "bulk1"}
        ]
        await bulk_operations(session, bulk_ops)
        
        # Test deletion
        await delete_key(session, "test1")
        
        # Verify deletion
        await get_key(session, "test1")
        
        # Test TTL expiration (set a very short TTL)
        await put_key_value(session, "short-lived", "temporary", 1)  # 1 minute TTL
        
        print(f"[{datetime.now()}] Mock client tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 