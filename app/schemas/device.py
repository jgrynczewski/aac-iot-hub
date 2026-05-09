"""
Device data models for AAC IoT Hub.

YAGNI: Start with power on/off only. Add more fields later.
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class DeviceStatus(BaseModel):
    """
    Current status of a device.

    Start: only power on/off. Add more fields later (brightness, rgb, color_temp).
    """
    power: str  # "on" | "off"
    online: bool = True
    last_seen: datetime


class Device(BaseModel):
    """Main device model."""
    id: str
    name: str
    type: str  # "yeelight" (more later: "shelly", etc.)
    model: str
    ip: str
    capabilities: List[str]  # Simple list: ["power"] initially, later: ["power", "brightness", "rgb"]
    status: DeviceStatus
    firmware: Optional[str] = None


class DeviceCapabilities(BaseModel):
    """
    Detailed capabilities info for GUI client.
    Returned by GET /devices/{id}/capabilities endpoint.

    Client uses this to render appropriate widgets:
    - "power" -> toggle button
    - "brightness" -> slider (min/max from metadata)
    - "rgb" -> color picker
    """
    device_id: str
    type: str
    model: str
    capabilities: Dict[str, Any]  # Nested structure with widget info, min/max, current values
    metadata: Dict[str, Any]  # firmware, online status, etc.