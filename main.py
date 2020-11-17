import json
import logging
import os
from typing import Any, Dict, Final, List

from aiocache import RedisCache
from fastapi import FastAPI, HTTPException, Response

Key = str
Value = Any

not_found: Final = object()  # Used as a default value for redis.get to properly handle retrieving of None values

logging.basicConfig(level=logging.INFO)
logger: Final = logging.getLogger("rest_storage")

app: Final = FastAPI(title="TGA Digital Rest Storage", version="1.0.0", openapi_tags=[{"name": "CRUD"}, {"name": "Bulk CRUD"}])
redis: Final = RedisCache(endpoint=os.environ["REDIS_HOST"], port=os.environ["REDIS_PORT"])


@app.put("/items/{key}", tags=["CRUD"], responses={201: {"content": {"application/json": {"example": {"stored": "/items/example_key"}}}}})
async def set_item(key: Key, value: Value) -> Response:
    """
    Store item to the key-value storage

    :returns: Path to the stored item
    """
    if (set_count := await redis.set(key, value)) != 1:
        logger.error(f"redis.set({key}, {value}) returned {set_count}. Expected 1")
        raise HTTPException(status_code=505, detail="Unexpected error has occurred. Please create issue at ...")
    return Response(status_code=201, media_type="application/json", headers={"Location": f"/items/{key}"}, content=json.dumps({"stored": f"/items/{key}"}))


@app.get("/items/{key}", tags=["CRUD"], responses={201: {"content": {"application/json": {"example": {"value": "example_value"}}}}})
async def get_item(key: Key) -> Response:
    """
    Retrieve item from the key-value storage

    :returns: Retrieved item
    """
    if (value := await redis.get(key, default=not_found)) is not_found:
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(status_code=201, media_type="application/json", content=json.dumps({"value": value}))


@app.delete("/items/{key}", tags=["CRUD"], responses={204: {}})
async def delete_item(key: Key) -> Response:
    """
    Delete item from the key-value storage
    """
    if not await redis.delete(key):
        raise HTTPException(status_code=404, detail="Item not found")
    return Response(status_code=204)


@app.put("/bulk/items", tags=["Bulk CRUD"], responses={201: {"content": {"application/json": {"example": {"stored": ["/items/example_key"]}}}}})
async def set_items(items: Dict[Key, Value]) -> Response:
    """
    Store items to the key-value storage

    :returns: Paths to the stored items
    """
    await redis.multi_set(items.items())
    return Response(status_code=201, media_type="application/json", content=json.dumps({"stored": [f"/items/{key}" for key in items.keys()]}))


@app.get("/bulk/items", tags=["Bulk CRUD"], responses={200: {"content": {"application/json": {"example": {"example_key": "example_value"}}}}})
async def get_items(keys: List[Key]) -> Response:
    """
    Retrieve items from the key-value storage

    :returns: Retrieved items
    """
    return Response(status_code=200, media_type="application/json", content=json.dumps({key: value for key, value in zip(keys, await redis.multi_get())}))


@app.delete("/bulk/items", tags=["Bulk CRUD"], responses={200: {"content": {"application/json": {"example": {"deleted_count": 5}}}}})
async def delete_items(keys: List[Key]) -> Response:
    """
    Delete items from the key-value storage

    :returns: Number of deleted items
    """
    # aiocache-0.11.1 does not provide multi_del method. Using redis-cli DEL instead
    if not (deleted_count := await redis.raw("execute", "DEL", *keys)):
        raise HTTPException(status_code=404, detail="No items found")
    return Response(status_code=200, media_type="application/json", content=json.dumps({"deleted_count": deleted_count}))
