import logging
from fastapi import FastAPI
import uvicorn

from app.core.config import settings
from app.core.logging_conf import logger
from app.api.v1.endpoints import webhook
from app.bot.setup import initialize_app, cleanup_app

# Initialize logs as early as possible
logger.info("Starting application")

# Create FastAPI instance
app = FastAPI(
    title="Telegram Bot API",
    description="FastAPI application for Telegram bot services",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Application startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Runs on application startup.
    Initialize the bot, set webhook, and preload data.
    """
    logger.info("Running application startup tasks")
    await initialize_app()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs on application shutdown.
    Perform cleanup tasks.
    """
    logger.info("Running application shutdown tasks")
    await cleanup_app()

# Root endpoint for health checks
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Service is running"}

# Include API routers
app.include_router(webhook.router, prefix=settings.WEBHOOK_PATH, tags=["Telegram"])

if __name__ == "__main__":
    # Run the application directly when this file is executed
    logger.info(f"Running server on {settings.APP_HOST}:{settings.APP_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        workers=settings.APP_WORKERS,
        reload=settings.DEBUG,
    )
