"""Prometheus metrics and ASGI middleware for HTTP instrumentation."""

from dataclasses import dataclass
from time import perf_counter

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from starlette.types import ASGIApp, Message, Receive, Scope, Send


@dataclass(frozen=True, slots=True)
class AppMetrics:
    """Container for application-specific Prometheus metrics."""

    registry: CollectorRegistry
    requests_total: Counter
    errors_total: Counter
    request_duration: Histogram
    requests_in_progress: Gauge


def create_metrics() -> AppMetrics:
    """Create an isolated Prometheus registry and its metrics."""

    registry = CollectorRegistry()

    requests_total = Counter(
        "http_requests",
        "Total number of HTTP requests.",
        ["method", "route", "status"],
        registry=registry,
    )

    errors_total = Counter(
        "http_errors",
        "Total number of HTTP error responses.",
        ["method", "route", "status"],
        registry=registry,
    )

    request_duration = Histogram(
        "http_request_duration_seconds",
        "HTTP request duration in seconds.",
        ["method", "route"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
        registry=registry,
    )

    requests_in_progress = Gauge(
        "http_requests_in_progress",
        "Number of HTTP requests currently being processed.",
        ["method"],
        registry=registry,
    )

    return AppMetrics(
        registry=registry,
        requests_total=requests_total,
        errors_total=errors_total,
        request_duration=request_duration,
        requests_in_progress=requests_in_progress,
    )


class PrometheusMiddleware:
    """ASGI middleware that records HTTP request metrics."""

    def __init__(self, app: ASGIApp, metrics: AppMetrics) -> None:
        self.app = app
        self.metrics = metrics

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http" or scope.get("path") == "/metrics":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "UNKNOWN")
        self.metrics.requests_in_progress.labels(method=method).inc()

        start_time = perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            route = scope.get("route")
            route_label = getattr(route, "path", "unmatched")
            duration = perf_counter() - start_time
            status = str(status_code)

            self.metrics.requests_total.labels(
                method=method,
                route=route_label,
                status=status,
            ).inc()

            if status_code >= 400:
                self.metrics.errors_total.labels(
                    method=method,
                    route=route_label,
                    status=status,
                ).inc()

            self.metrics.request_duration.labels(
                method=method,
                route=route_label,
            ).observe(duration)

            self.metrics.requests_in_progress.labels(method=method).dec()
