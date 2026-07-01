"""FastAPI application factory and configuration."""

import logging
import logging.config
import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.routes import logs, anomalies, alerts, health

# Configure logging
logging_config_path = "config/logging.yaml"
try:
    with open(logging_config_path) as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
except Exception:
    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager for startup and shutdown."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
    
    yield
    
    logger.info(f"Shutting down {settings.app_name}")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        description="AI-Powered Intelligent Observability & Event Watchdog",
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(logs.router)
    app.include_router(anomalies.router)
    app.include_router(alerts.router)
    app.include_router(health.router)
    
    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "endpoints": {
                "logs": "/api/logs",
                "anomalies": "/api/anomalies",
                "alerts": "/api/alerts",
                "health": "/api/health",
                "docs": "/docs",
                "openapi": "/openapi.json",
            }
        }
    
    @app.get("/status")
    async def status() -> dict:
        """Get application status."""
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
        }
    
    logger.info(f"{settings.app_name} application created successfully")
    return app


app = create_app()
