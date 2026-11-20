# Cloud-Native Observability Platform

A locally runnable observability platform built with FastAPI, Prometheus,
Grafana, and Docker.

This project demonstrates how to instrument a Python application, collect
application metrics, monitor HTTP performance, and visualize service health
through Grafana dashboards.

> **Project status:** Active development. The FastAPI application,
> Prometheus integration, Docker image, and Grafana dashboards are implemented
> and running locally.

## Overview

The platform provides an end-to-end application monitoring pipeline:

1. A FastAPI application exposes HTTP endpoints.
2. Prometheus instrumentation collects application metrics.
3. Prometheus scrapes the application's `/metrics` endpoint.
4. Grafana queries Prometheus and visualizes the collected metrics.

The project is designed to demonstrate practical cloud-native monitoring
concepts using free and open-source tools.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Application runtime |
| FastAPI | REST API framework |
| Prometheus | Metrics collection and monitoring |
| Grafana OSS | Metrics visualization and dashboards |
| Docker | Application containerization |
| pytest | Automated testing |
| Ruff | Linting and code formatting |
| uv | Python dependency management |

## Features

- Health and readiness endpoints.
- REST API with sample item endpoints.
- Prometheus metrics instrumentation.
- HTTP request, error, and latency monitoring.
- Custom Grafana dashboard with six panels.
- Dockerized FastAPI application.
- Automated tests and code-quality checks.

## Project Structure
cloud-native-observability/
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- main.py
|   |-- metrics.py
|-- monitoring/
|   |-- grafana/
|   |   |-- dashboards/
|   |       |-- application-observability.json
|   |-- prometheus.yml
|-- tests/
|-- .dockerignore
|-- Dockerfile
|-- pyproject.toml
|-- uv.lock
|-- README.md
|-- LICENSE
