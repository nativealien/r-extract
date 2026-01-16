from fastapi import FastAPI
from loguru import logger

from routes import auth, update

app = FastAPI(title="r-extract", version="0.1.0")

app.include_router(auth.router)
app.include_router(update.router)

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting R-Extract API")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down R-Extract API")