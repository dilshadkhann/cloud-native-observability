"""FastAPI application: health, readiness and demonstration endpoints."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query, Request
from fastapi.responses import JSONResponse

from app.config import Settings, load_settings

ITEMS: dict[int, str] = {
    1: "keyboard",
    2: "monitor",
    3: "headset",
    4: "webcam",
    5: "dock",
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.ready = True
    yield
    app.state.ready = False


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    app = FastAPI(title="Cloud-Native Observability", lifespan=lifespan)
    app.state.ready = False

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready")
    async def ready(request: Request) -> JSONResponse:
        if request.app.state.ready:
            return JSONResponse({"status": "ready"})
        return JSONResponse({"status": "not ready"}, status_code=503)

    @app.get("/items/{item_id}")
    async def get_item(item_id: Annotated[int, Path(ge=1)]) -> dict[str, int | str]:
        name = ITEMS.get(item_id)
        if name is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"id": item_id, "name": name}

    if settings.enable_fault_endpoints:

        @app.get("/slow")
        async def slow(
            delay: Annotated[float, Query(ge=0, le=settings.max_slow_seconds)] = 1.0,
        ) -> dict[str, float]:
            await asyncio.sleep(delay)
            return {"delayed_seconds": delay}

        @app.get("/error")
        async def error(
            status: Annotated[int, Query(ge=400, le=599)] = 500,
        ) -> None:
            raise HTTPException(status_code=status, detail="Simulated error")

    return app
