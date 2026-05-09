"""
API v1 routers for AAC IoT Hub.

All API routers exported for easy importing.
"""

from .devices import router as devices_router
from .health import router as health_router

__all__ = [
    "devices_router",
    "health_router",
]