"""FastAPI application entrypoint."""

from __future__ import annotations

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse

from src.api.case_studies import router as case_studies_router
from src.api.chat import router as chat_router
from src.api.ingest import router as ingest_router
from src.api.insights import router as insights_router
from src.api.media import router as media_router
from src.api.seed import router as seed_router
from src.config.settings import get_settings
from src.dependencies import get_vector_store
from src.jobs.scheduler import Scheduler
from src.limiter import limiter
from src.services.content_service import ContentService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize dependencies required at startup."""

    settings = get_settings()
    get_vector_store().initialize(vector_size=settings.embedding_dimensions)
    ContentService(settings.database_url).initialize()
    # Ensure the shared media directory exists before StaticFiles tries to serve it.
    Path(settings.media_root).mkdir(parents=True, exist_ok=True)
    (Path(settings.media_root) / "images").mkdir(parents=True, exist_ok=True)
    Scheduler().start()
    yield


def create_app() -> FastAPI:
    """Create the FastAPI application."""

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    allowed_origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["*"],
    )
    app.state.limiter = limiter

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded. Please slow down."},
        )

    app.include_router(chat_router)
    app.include_router(ingest_router)
    app.include_router(case_studies_router)
    app.include_router(insights_router)
    app.include_router(seed_router)
    app.include_router(media_router)

    # Serve uploaded media files as static assets at /media
    media_dir = Path(settings.media_root)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount(settings.media_url, StaticFiles(directory=str(media_dir)), name="media")

    @app.get("/health", tags=["system"])
    def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
