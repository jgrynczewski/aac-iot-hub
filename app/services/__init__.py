"""
Services for AAC IoT Hub.

Device adapters, registry, discovery, property handlers, and business logic.
"""

from .device_adapter import DeviceAdapter
from .yeelight_adapter import YeelightAdapter
from .device_registry import DeviceRegistry, device_registry
from .discovery import DiscoveryService, discovery_service
from .property_handlers import (
    PropertyHandler,
    PropertyHandlerRegistry,
    property_registry,
    PowerHandler,
    BrightnessHandler,
    RGBHandler,
    ColorTempHandler,
)

__all__ = [
    "DeviceAdapter",
    "YeelightAdapter",
    "DeviceRegistry",
    "device_registry",  # Global instance
    "DiscoveryService",
    "discovery_service",  # Global instance
    "PropertyHandler",
    "PropertyHandlerRegistry",
    "property_registry",  # Global instance
    "PowerHandler",
    "BrightnessHandler",
    "RGBHandler",
    "ColorTempHandler",
]