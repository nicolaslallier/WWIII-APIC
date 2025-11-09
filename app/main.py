"""FastAPI application factory."""

import signal
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.core.config import get_settings

settings = get_settings()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("application_starting", app_name=settings.app_name)
    yield
    # Shutdown
    logger.info("application_shutting_down", app_name=settings.app_name)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        FastAPI: Configured application instance
    """
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url="/redoc" if settings.environment != "production" else None,
        openapi_url="/openapi.json" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoints
    @app.get("/healthz", tags=["health"])
    async def healthz() -> dict[str, str]:
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.get("/readyz", tags=["health"])
    async def readyz() -> dict[str, str]:
        """Readiness check endpoint."""
        # TODO: Add database connectivity check
        return {"status": "ready"}

    # Prometheus metrics
    if settings.prometheus_enabled:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)

    # Register API routers
    from app.api.v1 import router as v1_router

    app.include_router(v1_router, prefix=settings.api_v1_prefix)

    return app


# Create app instance
app = create_app()


# Graceful shutdown handler
def signal_handler(sig: int, frame: object) -> None:
    """Handle shutdown signals gracefully."""
    logger.info("shutdown_signal_received", signal=sig)
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower(),
    )
