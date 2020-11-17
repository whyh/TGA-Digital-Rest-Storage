from typing import Dict

from fastapi.testclient import TestClient

from app.main import Key, Value, app, redis
from tests.utils import get_random_string, sync, timed

client = TestClient(app)
sync(redis.clear)()  # Flush Redis database prior to the test


def positive_test(items: Dict[Key, Value]) -> None:
    response, execution_time = timed(client.put)("/bulk/items", json=items)
    assert response.status_code == 201
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"stored": [f"/items/{key}" for key in items.keys()]}
    assert 0.1 > execution_time


def test_positive() -> None:
    positive_test(items={"test_key": "test_value"})
    positive_test(items={"key1": "value1", "key2": "value2", "key3": "value3"})


def test_negative() -> None:
    response, execution_time = timed(client.put)("/bulk/items")
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": [{"loc": ["body"], "msg": "field required", "type": "value_error.missing"}]}
    assert 0.1 > execution_time

    response, execution_time = timed(client.put)("/bulk/items", json="not a dict")
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": [{"loc": ["body"], "msg": "value is not a valid dict", "type": "type_error.dict"}]}
    assert 0.1 > execution_time

    response, execution_time = timed(client.put)("/bulk/items", json={})
    assert response.status_code == 400
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": "No items specified"}
    assert 0.1 > execution_time

    response, execution_time = timed(client.put)("/bulk/items", json={"key": None})
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": [{"loc": ["body", "key"], "msg": "none is not an allowed value", "type": "type_error.none.not_allowed"}]}
    assert 0.1 > execution_time

    response, execution_time = timed(client.put)("/bulk/items", json={"key": []})
    assert response.status_code == 422
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": [{"loc": ["body", "key"], "msg": "str type expected", "type": "type_error.str"}]}
    assert 0.1 > execution_time


def test_destructive() -> None:
    positive_test(items={get_random_string(length=5): get_random_string(length=5) for _ in range(10_000)})

    positive_test(items={get_random_string(length=10_000): "v"})
    positive_test(items={"k": get_random_string(length=10_000)})
    positive_test(items={get_random_string(length=10_000): get_random_string(length=10_000)})


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    test_positive()
    test_negative()
    test_destructive()
