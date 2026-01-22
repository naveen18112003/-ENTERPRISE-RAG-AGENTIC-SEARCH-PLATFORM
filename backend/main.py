"""
FastAPI Application Entry Point

WHAT: Initializes and configures FastAPI application
WHY: Main entry point for the backend server
HOW: Sets up middleware, routes, CORS, and app initialization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import get_settings
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.query import router as query_router

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    FastAPI application factory
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description="Enterprise RAG + Agentic Search Platform",
        debug=settings.debug,
    )

    # -----------------------------------------------------------------------------
    # CORS Middleware
    # -----------------------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -----------------------------------------------------------------------------
    # Routers
    # -----------------------------------------------------------------------------
    app.include_router(health_router)   # /health
    app.include_router(auth_router)     # /auth/*
    app.include_router(query_router)    # /api/query

    # -----------------------------------------------------------------------------
    # Root Endpoint
    # -----------------------------------------------------------------------------
    @app.get("/")
    async def root():
        return {
            "message": "Enterprise RAG + Agentic Search Platform",
            "version": settings.api_version,
            "docs": "/docs"
        }

    # -----------------------------------------------------------------------------
    # Global Exception Handler
    # -----------------------------------------------------------------------------
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        logger.exception("Unhandled exception")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

    # -----------------------------------------------------------------------------
    # Lifecycle Events
    # -----------------------------------------------------------------------------
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.api_title} v{settings.api_version}")
        logger.info(f"Environment: {settings.environment}")
        logger.info(f"Debug mode: {settings.debug}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Shutting down application")

    return app


# -----------------------------------------------------------------------------
# App Instance
# -----------------------------------------------------------------------------
app = create_app()

# -----------------------------------------------------------------------------
# Local Development Runner
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    settings = get_settings()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
