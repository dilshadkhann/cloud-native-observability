from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_returns_ready_after_startup(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_returns_503_before_startup(settings: Settings) -> None:
    # Without the context manager the lifespan does not run, so startup
    # has not completed.
    client = TestClient(create_app(settings))

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not ready"}


def test_not_ready_after_shutdown(settings: Settings) -> None:
    app = create_app(settings)

    with TestClient(app) as client:
        assert client.get("/ready").status_code == 200

    assert app.state.ready is False
