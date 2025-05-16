# Key-Value Storage Service

## DISCLAMER

- This project was made 98% manually. No LLM functional code, no autocomplete
- The whole process of me working on the project on record you can find here: (youtube link would be here when I'll edit the video - 30 hours recorded).
- What was written by LLM: docstrings, data type hints, this readme file, Dockerfiles. Every string was carefully checked manually.
- To easily start the project, you can use the docker-compose.yml, that is located in the main directory. For manual start install the dependincies and then just run the main.py file.

## Table of Contents

- [Project Description](#project-description)
- [API Handlers](#api-handlers)
  - [DELETE /{key}](#delete-key)
  - [GET /{key}](#get-key)
  - [PUT /{key}](#put-key)
  - [PUT /bulk](#put-bulk)

## Project Description

This project implements a simple asynchronous key-value storage service using aiohttp and SQLAlchemy with a database (desined to be PostgreSQL on prod and SQLight for local testing purposes). 
It provides basic CRUD operations for key-value pairs with an optional Time-To-Live (TTL) feature. Expired records are automatically cleaned up by a background scheduler.
It can be started on multiple servers to comunicate with one DB - distributed service.

## API Handlers

For testing purposes feel free to use Postman, or any other instrument/way of your choice.
The service has the following HTTP handlers:

### DELETE /{key}

Deletes a key-value record based on the provided key.

**Method:** `DELETE`
**Endpoint:** `/{key}` (where `{key}` is the key to delete)

**Example Request:**

```bash
curl -X DELETE http://localhost:6969/mykey
```

**Example Success Response (Status: 200):**

```json
{
  "status": "Sucess",
  "message": "Record with the key 'mykey' deleted"
}
```

**Example Error Response (Status: 404 - Not Found):**

```json
{
  "status": "Error",
  "message": "Record with the key 'nonexistent_key' not found"
}
```

### GET /{key}

Retrieves the value of a key-value record based on the provided key. If the record has expired based on its TTL, it will be deleted and not returned.

**Method:** `GET`
**Endpoint:** `/{key}` (where `{key}` is the key to retrieve)

**Example Request:**

```bash
curl http://localhost:6969/mykey
```

**Example Success Response (Status: 200):**

```json
{
  "key": "mykey",
  "value": "myvalue"
}
```

**Example Error Response (Status: 404 - Not Found):**

```json
{
  "status": "Error",
  "message": "Record with the key 'nonexistent_key' not found"
}
```

### PUT /{key}

Adds a new key-value record or updates an existing one with an optional Time-To-Live (TTL). If a record with the key already exists, the operation will fail as records cannot be modified, only added or deleted.

**Method:** `PUT`
**Endpoint:** `/{key}` (where `{key}` is the key to add or update)
**Request Body:** JSON object with a `value` field and an optional `tll` field.

**Request Body Schema:**

```json
{
  "value": "<any_value>",
  "tll": <optional_integer_minutes>
}
```

**Example Request (with TTL):**

```bash
curl -X PUT http://localhost:6969/anotherkey \
-H "Content-Type: application/json" \
-d '{"value": "anothervalue", "tll": 5}'
```

**Example Request (without TTL - uses default):**

```bash
curl -X PUT http://localhost:6969/defaultkey \
-H "Content-Type: application/json" \
-d '{"value": "defaultvalue"}'
```

**Example Success Response (Status: 200):**

```json
{
  "status": "Sucess",
  "message": "Record with the key 'anotherkey' was made successfully"
}
```

**Example Error Response (Status: 400 - Bad Request - Key Exists):**

```json
{
  "status": "Error",
  "message": "Record with the key 'existing_key' already exists and can not be modified"
}
```

**Example Error Response (Status: 400 - Bad Request - Invalid Body):**

```json
{
  "status": "Error",
  "message": "JSON Body misses the 'value' attribute. No changes were made"
}
```

### PUT /bulk

Performs multiple GET, PUT, or DELETE operations in a single request. The operations are processed sequentially (atomic transaction). If any operation in the bulk request fails, the entire transaction is rolled back, and no changes are made.

**Method:** `PUT`
**Endpoint:** `/bulk`
**Request Body:** JSON array of operation objects.

**Request Body Schema (Array of Objects):**

```json
[
  {
    "method": "GET" | "PUT" | "DELETE",
    "key": "<string_key>",
    "value": "<any_value>",   // Required for PUT method
    "tll": <optional_integer_minutes> // Optional for PUT method
  },
  // ... more operations
]
```

**Example Request:**

```bash
curl -X PUT http://localhost:6969/bulk \
-H "Content-Type: application/json" \
-d '[
  {"method": "PUT", "key": "bulk_key1", "value": "bulk_value1", "tll": 2},
  {"method": "GET", "key": "bulk_key1"},
  {"method": "DELETE", "key": "bulk_key2"}
]'
```

**Example Success Response (Status: 200):**

```json
{
  "status": "Success",
  "message": "All operations completed. Changes saved.",
  "details": [
    {
      "key": "bulk_key1",
      "result": "added successfully"
    },
    {
      "key": "bulk_key1",
      "value": "bulk_value1"
    },
    {
      "key": "bulk_key2",
      "result": "deleted successfully"}
  ]
}
```

**Example Error Response (Status: 400 - Bad Request - Operation Failed):**

```json
{
  "status": "Error",
  "message": "Not all operations were correct. No changes were made.",
  "details": [
    {
      "key": "nonexistent_key",
      "result": "Record with the key 'nonexistent_key' does not exists"
    }
  ]
}
```

## Thank you for your attention :-)