import time

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_get_item_returns_item(client: TestClient) -> None:
    response = client.get("/items/1")

    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "keyboard"}


def test_get_item_unknown_id_returns_404(client: TestClient) -> None:
    response = client.get("/items/99")

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


@pytest.mark.parametrize("item_id", ["0", "-1", "abc"])
def test_get_item_invalid_id_returns_422(client: TestClient, item_id: str) -> None:
    assert client.get(f"/items/{item_id}").status_code == 422


@pytest.mark.parametrize("status", [400, 404, 500, 503, 599])
def test_error_endpoint_returns_requested_status(
    client: TestClient, status: int
) -> None:
    response = client.get("/error", params={"status": status})

    assert response.status_code == status
    assert response.json() == {"detail": "Simulated error"}


@pytest.mark.parametrize("status", ["200", "399", "600", "abc"])
def test_error_endpoint_rejects_invalid_status(client: TestClient, status: str) -> None:
    assert client.get("/error", params={"status": status}).status_code == 422


def test_slow_endpoint_waits_requested_delay(client: TestClient) -> None:
    started = time.perf_counter()
    response = client.get("/slow", params={"delay": 0.2})
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert response.json() == {"delayed_seconds": 0.2}
    # Tolerance for timer resolution, which is coarse on Windows.
    assert elapsed >= 0.15


@pytest.mark.parametrize("delay", ["-1", "1.5", "nan", "inf", "abc"])
def test_slow_endpoint_rejects_invalid_delay(client: TestClient, delay: str) -> None:
    assert client.get("/slow", params={"delay": delay}).status_code == 422


def test_fault_endpoints_are_absent_when_disabled() -> None:
    settings = Settings(
        environment="production",
        enable_fault_endpoints=False,
        max_slow_seconds=5.0,
    )

    with TestClient(create_app(settings)) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/slow").status_code == 404
        assert client.get("/error").status_code == 404
