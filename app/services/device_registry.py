"""
Device Registry - Central registry for discovered devices.

Global instance stores all devices in memory.
YAGNI: No persistence yet - devices rediscovered on restart.
"""

from typing import Dict, List, Optional
import logging

from app.services.device_adapter import DeviceAdapter
from app.schemas.device import Device

logger = logging.getLogger(__name__)


class DeviceRegistry:
    """
    Central registry for all discovered devices.

    Stores device adapters in memory (no persistence).
    Use the global instance at bottom of this file.
    """

    def __init__(self):
        """Initialize empty registry."""
        self._devices: Dict[str, DeviceAdapter] = {}

    def register(self, adapter: DeviceAdapter):
        """
        Register a device adapter.

        Args:
            adapter: DeviceAdapter instance to register

        Example:
            >>> adapter = YeelightAdapter("yeelight_123", "192.168.1.100", "color4")
            >>> device_registry.register(adapter)
        """
        self._devices[adapter.device_id] = adapter
        logger.info(f"Registered device: {adapter.device_id} ({adapter.type} at {adapter.ip})")

    def unregister(self, device_id: str):
        """
        Remove device from registry.

        Args:
            device_id: Device ID to remove
        """
        if device_id in self._devices:
            del self._devices[device_id]
            logger.info(f"Unregistered device: {device_id}")

    def get(self, device_id: str) -> Optional[DeviceAdapter]:
        """
        Get device adapter by ID.

        Args:
            device_id: Device ID to retrieve

        Returns:
            DeviceAdapter if found, None otherwise
        """
        return self._devices.get(device_id)

    def get_all(self) -> List[DeviceAdapter]:
        """
        Get all registered device adapters.

        Returns:
            List of all DeviceAdapter instances
        """
        return list(self._devices.values())

    async def get_all_status(self) -> List[Device]:
        """
        Get status of all registered devices.

        Queries each device for current status.
        Skips devices that are offline or fail to respond.

        Returns:
            List of Device objects with current status
        """
        statuses = []
        for adapter in self._devices.values():
            try:
                status = await adapter.get_status()
                statuses.append(status)
            except Exception as e:
                # Device offline or error - log and continue
                logger.warning(f"Failed to get status for {adapter.device_id}: {e}")
        return statuses

    def clear(self):
        """
        Clear all devices from registry.

        Used during shutdown or testing.
        """
        count = len(self._devices)
        self._devices.clear()
        logger.info(f"Cleared {count} devices from registry")

    def count(self) -> int:
        """
        Get number of registered devices.

        Returns:
            Number of devices in registry
        """
        return len(self._devices)


# Global instance - use this instead of creating new instances
device_registry = DeviceRegistry()