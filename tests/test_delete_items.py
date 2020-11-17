from typing import List

from fastapi.testclient import TestClient

from app.main import Key, Value, app, redis
from tests.utils import get_random_string, sync, timed

client = TestClient(app)
sync(redis.clear)()  # Flush Redis database prior to the test


def positive_test(keys: List[Key], *, value: Value = "v") -> None:
    # Add keys to the storage
    sync(redis.multi_set)([(key, value) for key in keys])
    assert len(sync(redis.multi_get)(keys)) == len(keys)

    response, execution_time = timed(client.delete)("/bulk/items", json=keys)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"deleted_count": len(set(keys))}
    assert 0.1 > execution_time


def test_positive() -> None:
    positive_test(keys=["test_key"])
    positive_test(keys=["key1", "key2", "key3"])


def test_negative() -> None:
    response, execution_time = timed(client.delete)("/bulk/items")
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": [{"loc": ["body"], "msg": "field required", "type": "value_error.missing"}]}
    assert 0.1 > execution_time

    response, execution_time = timed(client.delete)("/bulk/items", json="not a list")
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": [{"loc": ["body"], "msg": "value is not a valid list", "type": "type_error.list"}]}
    assert 0.1 > execution_time

    response, execution_time = timed(client.delete)("/bulk/items", json=[])
    assert response.status_code == 404
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": "No items found"}
    assert 0.1 > execution_time

    response, execution_time = timed(client.delete)("/bulk/items", json=[None])
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": [{"loc": ["body", 0], "msg": "none is not an allowed value", "type": "type_error.none.not_allowed"}]}
    assert 0.1 > execution_time

    response, execution_time = timed(client.delete)("/bulk/items", json=[{}])
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": [{"loc": ["body", 0], "msg": "str type expected", "type": "type_error.str"}]}
    assert 0.1 > execution_time

    response, execution_time = timed(client.delete)("/bulk/items", json=["invalid_key"])
    assert response.status_code == 404
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": "No items found"}
    assert 0.1 > execution_time

    response, execution_time = timed(client.delete)("/bulk/items", json=["invalid_key1", "invalid_key2"])
    assert response.status_code == 404
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": "No items found"}
    assert 0.1 > execution_time


def test_destructive() -> None:
    positive_test(keys=[get_random_string(length=10_000)])
    positive_test(keys=["v" for _ in range(10_000)])
    positive_test(keys=[get_random_string(length=1) for _ in range(10_000)])


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    test_positive()
    test_negative()
    test_destructive()
