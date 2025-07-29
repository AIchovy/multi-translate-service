"""
FastAPI application module for Multi Translate Service
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.routes.translation import router as translation_router
from src.models.base import engine
from src.utils.logger import get_logger

# Get logger for this module
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    """
    # Startup
    logger.info("Starting application...")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    # Close database connection pool
    await engine.dispose()
    logger.info("Application shutdown completed")

def create_app() -> FastAPI:
    """Create FastAPI application instance"""
    logger.info("Creating FastAPI application instance...")
    
    app = FastAPI(
        title="Multi Translate Service",
        description="Multi Translate Service API",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Register routes
    app.include_router(translation_router, tags=["translation"])
    logger.info("Routes registered successfully")
    
    return app

# Create application instance
app = create_app()
logger.info("Application instance created successfully") 