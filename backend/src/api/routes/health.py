"""
Health check and system status routes
"""

from fastapi import APIRouter
from datetime import datetime
from pydantic import BaseModel
import logging

from models.base import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


class HealthStatus(BaseModel):
    """Health status response model"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"


@router.get("/health", response_model=APIResponse[HealthStatus])
async def health_check():
    """Basic health check endpoint"""
    return APIResponse(
        success=True,
        data=HealthStatus(
            status="healthy",
            timestamp=datetime.now(),
            version="1.0.0"
        ),
        message="Service is healthy"
    )


@router.get("/", response_model=APIResponse[dict])
async def root():
    """Root endpoint"""
    return APIResponse(
        success=True,
        data={
            "service": "CCM2 Backend API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        },
        message="CCM2 Backend API is running"
    )