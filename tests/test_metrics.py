"""Tests for Prometheus HTTP metrics."""

from fastapi.testclient import TestClient


def test_metrics_endpoint_exposes_prometheus_format(client: TestClient) -> None:
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "# HELP http_requests_total" in response.text
    assert "# TYPE http_requests_total counter" in response.text
    assert "# HELP http_request_duration_seconds" in response.text


def test_successful_request_increments_request_counter(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200

    metrics_response = client.get("/metrics")

    assert (
        'http_requests_total{method="GET",route="/health",status="200"} 1.0'
        in metrics_response.text
    )


def test_error_response_increments_error_counter(client: TestClient) -> None:
    response = client.get("/items/999")

    assert response.status_code == 404

    metrics_response = client.get("/metrics")

    assert (
        'http_requests_total{method="GET",route="/items/{item_id}",status="404"} 1.0'
        in metrics_response.text
    )
    assert (
        'http_errors_total{method="GET",route="/items/{item_id}",status="404"} 1.0'
        in metrics_response.text
    )


def test_histogram_records_request_duration(client: TestClient) -> None:
    client.get("/health")

    metrics_response = client.get("/metrics")

    assert (
        'http_request_duration_seconds_count{method="GET",route="/health"} 1.0'
        in metrics_response.text
    )


def test_in_progress_gauge_returns_to_zero(client: TestClient) -> None:
    client.get("/health")

    metrics_response = client.get("/metrics")

    assert 'http_requests_in_progress{method="GET"} 0.0' in metrics_response.text


def test_metrics_endpoint_does_not_count_its_own_scrapes(
    client: TestClient,
) -> None:
    client.get("/health")
    client.get("/metrics")
    metrics_response = client.get("/metrics")

    assert (
        'http_requests_total{method="GET",route="/health",status="200"} 1.0'
        in metrics_response.text
    )
    assert "/metrics" not in metrics_response.text
