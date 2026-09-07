"""
Request schemas for AAC IoT Hub API.

Universal control request - one endpoint for all device capabilities.
"""

from pydantic import BaseModel
from typing import Dict, Any


class DeviceControlRequest(BaseModel):
    """
    Universal control request for all device capabilities.

    Client sends any capability changes in a single request.

    Examples:
        - {"properties": {"power": "on"}}
        - {"properties": {"power": "on", "brightness": 80}}
        - {"properties": {"rgb": [255, 0, 0], "brightness": 100}}

    Validation happens in adapter based on device capabilities.
    """
    properties: Dict[str, Any]  # Capability name -> value pairs


class EffectStartRequest(BaseModel):
    """
    Request to start a flow effect.

    Examples:
        - {"effect_name": "disco"}
        - {"effect_name": "rainbow"}

    Available effects: disco, pulse, strobe, rainbow, police, ocean
    """
    effect_name: str  # Name of the effect to start