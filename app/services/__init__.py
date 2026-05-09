"""
Services for AAC IoT Hub.

Device adapters, registry, discovery, and business logic.
"""

from .device_adapter import DeviceAdapter
from .yeelight_adapter import YeelightAdapter
from .device_registry import DeviceRegistry, device_registry
from .discovery import DiscoveryService, discovery_service

__all__ = [
    "DeviceAdapter",
    "YeelightAdapter",
    "DeviceRegistry",
    "device_registry",  # Global instance
    "DiscoveryService",
    "discovery_service",  # Global instance
]