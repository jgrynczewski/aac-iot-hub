"""
Health check API endpoints - AAC IoT Hub.

Basic health monitoring for API and device registry.
"""

from fastapi import APIRouter
from datetime import datetime
import time

router = APIRouter(tags=["health"])

# Track API start time for uptime calculation
start_time = time.time()


@router.get("/api/health")
async def health_check():
    """
    Basic health check endpoint.

    Returns simple status to verify API is running.
    Useful for Docker health checks and monitoring.

    Returns:
        status: "ok" if API is running
        version: API version
        timestamp: Current timestamp
    """
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/api/v1/status")
async def get_status():
    """
    Detailed API status with device registry info.

    Returns:
        devices_total: Number of registered devices
        uptime_seconds: API uptime in seconds
        timestamp: Current timestamp
    """
    from app.services import device_registry

    devices = device_registry.get_all()

    return {
        "devices_total": len(devices),
        "uptime_seconds": int(time.time() - start_time),
        "timestamp": datetime.now().isoformat()
    }