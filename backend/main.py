from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.routers import health, analyze
from backend.core.config import settings
from backend.core.logging import logger
from contextlib import asynccontextmanager
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} in {settings.environment} mode...")
    # Pre-initialize services (this will download PaddleOCR models on first run if not present)
    from backend.services.ocr_service import get_ocr_service
    get_ocr_service()
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.app_name,
    description="API for AI Vision OCR Platform - Google Lens style image analysis",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router)
app.include_router(analyze.router)

# Serve Flutter Web frontend if a frontend path is configured
# This allows the backend to serve the entire app for local dev / ngrok sharing
if settings.frontend_path and os.path.isdir(settings.frontend_path):
    logger.info(f"Serving frontend from: {settings.frontend_path}")
    app.mount("/", StaticFiles(directory=settings.frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.port, reload=True)
