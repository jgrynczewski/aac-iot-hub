"""
Property handlers for universal device control endpoint.

Uses Strategy Pattern + Registry for OCP compliance:
- Each property has its own handler (strategy)
- Handler validates + executes property change
- Endpoint delegates to handlers (no if/elif)
- Adding new property = create handler + register (zero endpoint changes)

Architecture:
    PropertyHandler (ABC)
        ├── PowerHandler
        ├── BrightnessHandler (future)
        ├── RGBHandler (future)
        └── ColorTempHandler (future)

    PropertyHandlerRegistry
        - register(name, handler)
        - get(name) -> handler
        - has(name) -> bool
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

from app.services.device_adapter import DeviceAdapter
from app.services.color_presets import get_rgb, get_color_names, get_temperature, get_temperature_names

logger = logging.getLogger(__name__)


class PropertyHandler(ABC):
    """
    Abstract base class for property handlers.

    Each handler implements Strategy Pattern for a specific device property.
    Handlers are responsible for both validation and execution.
    """

    @abstractmethod
    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """
        Handle property change.

        Args:
            adapter: Device adapter to execute on
            value: Property value from request

        Returns:
            Result value (for response)

        Raises:
            ValueError: If value is invalid
        """
        pass

    @abstractmethod
    def validate(self, value: Any) -> None:
        """
        Validate property value.

        Args:
            value: Value to validate

        Raises:
            ValueError: If value is invalid
        """
        pass


class PowerHandler(PropertyHandler):
    """
    Handler for 'power' property (on/off/toggle).

    Migrated from original endpoint implementation.
    Validates power states and delegates to adapter.set_power().
    """

    def validate(self, value: Any) -> None:
        """
        Validate power state.

        Args:
            value: Power state to validate

        Raises:
            ValueError: If value is not "on", "off", or "toggle"
        """
        if value not in ["on", "off", "toggle"]:
            raise ValueError(
                f"Power must be 'on', 'off', or 'toggle', got '{value}'"
            )

    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """
        Set power state.

        Args:
            adapter: Device adapter
            value: Power state ("on", "off", or "toggle")

        Returns:
            Applied power state

        Raises:
            ValueError: If value is invalid
        """
        self.validate(value)
        await adapter.set_power(value)
        return value


class BrightnessHandler(PropertyHandler):
    """
    Handler for 'brightness' property (1-100 slider).

    Validates brightness range and delegates to adapter.set_brightness().
    Yeelight doesn't support brightness=0, minimum is 1.
    """

    def validate(self, value: Any) -> None:
        """
        Validate brightness value.

        Args:
            value: Brightness to validate

        Raises:
            ValueError: If value is not integer or not in range 1-100
        """
        if not isinstance(value, int):
            raise ValueError(
                f"Brightness must be an integer, got {type(value).__name__}"
            )
        if not 1 <= value <= 100:
            raise ValueError(
                f"Brightness must be 1-100 (Yeelight doesn't support 0), got {value}"
            )

    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """
        Set brightness level.

        Args:
            adapter: Device adapter
            value: Brightness 1-100

        Returns:
            Applied brightness value

        Raises:
            ValueError: If value is invalid
        """
        self.validate(value)
        await adapter.set_brightness(value)
        return value


class RGBHandler(PropertyHandler):
    """
    Handler for 'color' property (8-color palette).

    AAC-optimized: Uses named colors instead of raw RGB values.
    Users select from accessible palette (red, blue, green, etc.).
    """

    def validate(self, value: Any) -> None:
        """
        Validate color name.

        Args:
            value: Color name to validate

        Raises:
            ValueError: If color name is not in palette
        """
        if not isinstance(value, str):
            raise ValueError(
                f"Color must be a string, got {type(value).__name__}"
            )
        # This will raise ValueError if color is unknown
        # (get_rgb validates against palette)
        try:
            get_rgb(value)
        except ValueError as e:
            # Re-raise with original message from color_presets
            raise e

    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """
        Set color using named palette.

        Args:
            adapter: Device adapter
            value: Color name (e.g., "red", "blue")

        Returns:
            Applied color name

        Raises:
            ValueError: If color name is invalid
        """
        self.validate(value)
        # Get RGB values from palette
        r, g, b = get_rgb(value)
        # Set RGB on device
        await adapter.set_rgb(r, g, b)
        return value


class ColorTempHandler(PropertyHandler):
    """
    Handler for 'temperature' property (color temperature presets).

    AAC-optimized: Uses named presets (warm/neutral/cold) instead of Kelvin values.
    Users select from 3 accessible temperature options.
    """

    def validate(self, value: Any) -> None:
        """
        Validate temperature preset name.

        Args:
            value: Temperature preset name to validate

        Raises:
            ValueError: If preset name is not valid
        """
        if not isinstance(value, str):
            raise ValueError(
                f"Temperature must be a string, got {type(value).__name__}"
            )
        # This will raise ValueError if preset is unknown
        # (get_temperature validates against presets)
        try:
            get_temperature(value)
        except ValueError as e:
            # Re-raise with original message from color_presets
            raise e

    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """
        Set color temperature using named preset.

        Args:
            adapter: Device adapter
            value: Temperature preset name (e.g., "warm", "cold")

        Returns:
            Applied preset name

        Raises:
            ValueError: If preset name is invalid
        """
        self.validate(value)
        # Get Kelvin value from preset
        kelvin = get_temperature(value)
        # Set temperature on device
        await adapter.set_color_temp(kelvin)
        return value


class PropertyHandlerRegistry:
    """
    Registry for property handlers.

    Maintains mapping of property names to their handlers.
    Allows dynamic lookup and validation of supported properties.

    Example:
        registry = PropertyHandlerRegistry()
        registry.register("power", PowerHandler())

        handler = registry.get("power")
        result = await handler.handle(adapter, "on")
    """

    def __init__(self):
        """Initialize empty registry."""
        self._handlers: Dict[str, PropertyHandler] = {}

    def register(self, property_name: str, handler: PropertyHandler):
        """
        Register a handler for a property.

        Args:
            property_name: Name of property (e.g., "power", "brightness")
            handler: Handler instance for this property
        """
        self._handlers[property_name] = handler
        logger.info(f"Registered property handler: {property_name}")

    def get(self, property_name: str) -> PropertyHandler:
        """
        Get handler for a property.

        Args:
            property_name: Name of property

        Returns:
            Handler instance

        Raises:
            ValueError: If property is not supported
        """
        if property_name not in self._handlers:
            supported = ", ".join(sorted(self._handlers.keys()))
            raise ValueError(
                f"Unknown property '{property_name}'. "
                f"Supported properties: {supported}"
            )
        return self._handlers[property_name]

    def has(self, property_name: str) -> bool:
        """
        Check if property is supported.

        Args:
            property_name: Name of property

        Returns:
            True if property has registered handler
        """
        return property_name in self._handlers

    def get_all(self) -> Dict[str, PropertyHandler]:
        """
        Get all registered handlers.

        Returns:
            Dictionary mapping property names to handlers
        """
        return self._handlers.copy()

    def get_supported_properties(self) -> list[str]:
        """
        Get list of supported property names.

        Returns:
            Sorted list of property names
        """
        return sorted(self._handlers.keys())


# Global registry instance
property_registry = PropertyHandlerRegistry()

# Register built-in handlers
property_registry.register("power", PowerHandler())
property_registry.register("brightness", BrightnessHandler())
property_registry.register("color", RGBHandler())
property_registry.register("temperature", ColorTempHandler())

logger.info(
    f"Property handler system initialized. "
    f"Supported properties: {property_registry.get_supported_properties()}"
)