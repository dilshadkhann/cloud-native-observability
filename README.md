# Cloud-Native Observability Platform

A locally runnable, containerized observability platform built with FastAPI, Prometheus, Grafana, and Docker Compose.

This project demonstrates application instrumentation, metrics collection, monitoring, dashboard provisioning, containerization, and automated code-quality checks.

## Project Status

The following components have been implemented and verified locally:

- FastAPI application with health and sample API endpoints.
- Prometheus application metrics and scraping.
- Grafana datasource and dashboard provisioning.
- Six-panel application observability dashboard.
- Docker Compose orchestration with persistent storage.
- Automated tests, Ruff checks, and GitHub Actions CI.

## Architecture

The platform provides an end-to-end monitoring pipeline:

1. FastAPI serves application endpoints and exposes `/metrics`.
2. Prometheus scrapes the FastAPI metrics endpoint.
3. Grafana queries Prometheus for monitoring data.
4. Grafana provisions the Prometheus datasource and application dashboard automatically.

```text
                  Docker Compose
                         |
          +--------------+--------------+
          |              |              |
          v              v              v
     FastAPI API     Prometheus       Grafana
       :8000            :9090           :3000
          |              ^              |
          |              |              |
          +-- /metrics --+              |
                         +--------------+
                           Prometheus
                           datasource
```

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Application runtime |
| FastAPI | REST API framework |
| Prometheus 3.5.0 | Metrics collection and monitoring |
| Grafana 12.2.1 | Metrics visualization |
| Docker | Application containerization |
| Docker Compose | Multi-container orchestration |
| uv | Python dependency management |
| pytest | Automated testing |
| Ruff | Linting and code formatting |
| GitHub Actions | Continuous integration |

## Features

- Health and readiness endpoints.
- Sample REST API endpoints.
- Prometheus metrics instrumentation.
- HTTP request counters.
- HTTP error counters.
- HTTP request latency monitoring.
- Grafana dashboard with six panels.
- Automatic Grafana datasource provisioning.
- Automatic Grafana dashboard provisioning.
- Persistent Prometheus and Grafana storage.
- Localhost-only service port bindings.
- Automated testing and CI checks.

## Project Structure

```text
cloud-native-observability/
├── .github/
│   └── workflows/
│       └── ci.yaml
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   └── metrics.py
├── monitoring/
│   ├── prometheus.yml
│   └── grafana/
│       ├── dashboards/
│       │   └── application-observability.json
│       └── provisioning/
│           ├── alerting/
│           │   └── .gitkeep
│           ├── dashboards/
│           │   └── dashboards.yml
│           ├── datasources/
│           │   └── prometheus.yml
│           └── plugins/
│               └── .gitkeep
├── tests/
├── .dockerignore
├── .gitignore
├── Dockerfile
├── compose.yaml
├── pyproject.toml
├── uv.lock
├── README.md
└── LICENSE
```

## Prerequisites

Install the following:

- Git
- Docker Desktop
- Docker Compose (included with Docker Desktop)

Docker Desktop must be running before starting the stack.

## Quick Start

Clone the repository:

```powershell
git clone https://github.com/dilshadkhann/cloud-native-observability.git
cd cloud-native-observability
```

Build and start all services:

```powershell
docker compose up --build -d
```

Check service status:

```powershell
docker compose ps
```

All three services should be running. The FastAPI container should become healthy.

## Access the Services

| Service | URL |
|---|---|
| FastAPI health | http://localhost:8000/health |
| FastAPI readiness | http://localhost:8000/ready |
| API documentation | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Prometheus targets | http://localhost:9090/targets |
| Prometheus metrics | http://localhost:8000/metrics |
| Grafana | http://localhost:3000 |

The services are bound to localhost for local development.

### Grafana Login

For a fresh Grafana data volume, the default initial credentials are:

- Username: `admin`
- Password: `admin`

Grafana normally prompts you to change the password after the first login.

Existing Grafana volumes retain their existing credentials.

## Grafana Dashboard

The dashboard contains these six panels:

1. HTTP Request Rate
2. HTTP Responses by Status Code
3. HTTP Error Rate
4. HTTP Request Latency (p50)
5. HTTP Request Latency (p95)
6. HTTP Request Latency (p99)

The Prometheus datasource and dashboard are provisioned from files in
`monitoring/grafana/provisioning/`.

The Prometheus datasource and dashboard are provisioned from files in `monitoring/grafana/provisioning/`.

The dashboard definition is stored in:

```text
monitoring/grafana/dashboards/application-observability.json
```

## Prometheus Metrics

The FastAPI application exposes metrics at:

```text
http://localhost:8000/metrics
```

Important application metrics include:

| Metric | Description |
|---|---|
| `http_requests_total` | Total HTTP requests |
| `http_errors_total` | Total HTTP error responses |

The HTTP error counter is created when an error response is recorded. Consequently, the HTTP Error Rate panel may initially show no data until the application has recorded an error.

### HTTP Error Rate Query

The dashboard uses this PromQL expression to calculate the percentage of HTTP requests resulting in errors over a five-minute rate window:

```promql
100 *
sum(rate(http_errors_total[5m]))
/
clamp_min(sum(rate(http_requests_total[5m])), 0.001)
```

To generate a test HTTP 500 response:

```powershell
try {
    Invoke-WebRequest -UseBasicParsing http://localhost:8000/error
} catch {
    "Expected test error: $($_.Exception.Message)"
}
```

Allow Prometheus time to scrape the updated metrics before checking the dashboard.

## Docker Compose Operations

Start or rebuild the stack:

```powershell
docker compose up --build -d
```

View running services:

```powershell
docker compose ps
```

View service logs:

```powershell
docker compose logs --tail 100
```

Follow logs continuously:

```powershell
docker compose logs -f
```

Restart services:

```powershell
docker compose restart
```

Stop and remove containers and the Compose network:

```powershell
docker compose down
```

Named data volumes are preserved by default when using `docker compose down`.

**Data protection:** Avoid `docker compose down -v` unless you intentionally want to delete the persistent Prometheus and Grafana volumes.

## Local Development and Testing

Install Python dependencies using uv:

```powershell
uv sync --frozen
```

Run tests:

```powershell
uv run --frozen pytest
```

Run Ruff lint checks:

```powershell
uv run --frozen ruff check app tests
```

Check code formatting:

```powershell
uv run --frozen ruff format --check app tests
```

Validate Docker Compose configuration:

```powershell
docker compose config -q
```

Validate dashboard JSON:

```powershell
python -m json.tool monitoring/grafana/dashboards/application-observability.json > $null
```

## Continuous Integration

GitHub Actions runs the project checks on pushes and pull requests targeting `main`.

The workflow includes:

- Python environment setup.
- uv dependency installation.
- Ruff lint checks.
- Ruff formatting checks.
- pytest execution.
- Docker image build.

Workflow definition:

```text
.github/workflows/ci.yaml
```

## Data Persistence

Docker Compose uses named volumes:

- `prometheus-data`
- `grafana-storage`

These preserve Prometheus time-series data and Grafana application data across container recreation.

A fresh clone creates its own Compose-managed volumes. Existing local data is not required for a fresh installation.

## Troubleshooting

### Docker is not running

Start Docker Desktop and verify:

```powershell
docker info
```

### A service is not healthy

Inspect its logs:

```powershell
docker compose logs observability-api
docker compose logs prometheus
docker compose logs grafana
```

### Prometheus target is down

Open:

```text
http://localhost:9090/targets
```

The FastAPI target should show `UP`.

### Grafana panel shows No data

Check that Prometheus is scraping the API and that the relevant metric has been recorded.

For HTTP Error Rate, generate a test HTTP 500 response and allow Prometheus to scrape it.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
