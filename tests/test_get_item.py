from fastapi.testclient import TestClient

from app.main import Key, Value, app, redis
from tests.utils import get_random_string, sync, timed

client = TestClient(app)
sync(redis.clear)()  # Flush Redis database prior to the test


def positive_test(key: Key, value: Value) -> None:
    # Add key to the storage
    sync(redis.set)(key, value)
    assert sync(redis.get)(key) == value

    response, execution_time = timed(client.get)(f"/items/{key}")
    assert response.status_code == 201
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"value": value}
    assert 0.1 > execution_time


def test_positive() -> None:
    positive_test(key="test_key", value="test_value")
    positive_test(key="key@1", value="key@1_value")


def test_negative() -> None:
    response, execution_time = timed(client.get)("/items")
    assert response.status_code == 404
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": "Not Found"}
    assert 0.1 > execution_time

    assert sync(redis.get)("invalid_key") is None
    response, execution_time = timed(client.get)("/items/invalid_key")
    assert response.status_code == 404
    assert response.headers.get("content-type") == "application/json"
    assert response.json() == {"detail": "Item not found"}
    assert 0.1 > execution_time


def test_destructive() -> None:
    positive_test(key="k" * 10_000, value="v")
    positive_test(key="k", value="v" * 10_000)
    positive_test(key="k" * 10_000, value="v" * 10_000)

    positive_test(key=get_random_string(length=10_000), value="v")
    positive_test(key="k", value=get_random_string(length=10_000))
    positive_test(key=get_random_string(length=10_000), value=get_random_string(length=10_000))


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    test_positive()
    test_negative()
    test_destructive()
