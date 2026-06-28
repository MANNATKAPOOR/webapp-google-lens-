from fastapi import APIRouter
from backend.models.schemas import HealthResponse, VersionResponse
from backend.core.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Basic health check endpoint to verify the API is running.
    """
    return HealthResponse(environment=settings.environment)

@router.get("/version", response_model=VersionResponse, tags=["System"])
async def version_check():
    """
    Returns the current API version and application name.
    """
    return VersionResponse(name=settings.app_name)
