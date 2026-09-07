"""
Pydantic schemas for AAC IoT Hub.

All schemas exported for convenient importing.
"""

# Device models
from .device import (
    Device,
    DeviceStatus,
    DeviceCapabilities,
)

# Request models
from .requests import (
    DeviceControlRequest,
    EffectStartRequest,
)

# Response models
from .responses import (
    SuccessResponse,
    ErrorDetail,
    ErrorResponse,
)

__all__ = [
    # Device models
    "Device",
    "DeviceStatus",
    "DeviceCapabilities",
    # Request models
    "DeviceControlRequest",
    "EffectStartRequest",
    # Response models
    "SuccessResponse",
    "ErrorDetail",
    "ErrorResponse",
]