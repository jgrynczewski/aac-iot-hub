"""
Device Adapter - Abstract Base Class.

Defines the contract that all device adapters must implement.
YAGNI: Start with power on/off only, expand later.
"""

from abc import ABC, abstractmethod
from app.schemas.device import Device, DeviceCapabilities


class DeviceAdapter(ABC):
    """
    Abstract base class for all device adapters.

    Each device type (Yeelight, Shelly, etc.) implements this interface.
    This ensures consistent API across different device types.
    """

    def __init__(self, device_id: str, ip: str, model: str):
        """
        Initialize device adapter.

        Args:
            device_id: Unique device identifier (usually MAC address or UUID)
            ip: Device IP address on local network
            model: Device model string (e.g., "color4" for Yeelight)
        """
        self.device_id = device_id
        self.ip = ip
        self.model = model
        self.type = self._get_type()

    @abstractmethod
    def _get_type(self) -> str:
        """
        Return device type identifier.

        Returns:
            Type string (e.g., "yeelight", "shelly")
        """
        pass

    @abstractmethod
    async def get_status(self) -> Device:
        """
        Get current device status.

        Returns:
            Device object with current status
        """
        pass

    @abstractmethod
    async def get_capabilities(self) -> DeviceCapabilities:
        """
        Get detailed capability information for GUI rendering.

        Returns:
            DeviceCapabilities with widget metadata, min/max values, etc.
        """
        pass

    # Control methods - YAGNI: start with power only

    @abstractmethod
    async def set_power(self, state: str) -> bool:
        """
        Set device power state.

        Args:
            state: "on" | "off" | "toggle"

        Returns:
            True if successful

        Raises:
            Exception if device is offline or command fails
        """
        pass

    # Future expansion (add when needed):
    # - async def set_brightness(self, value: int) -> bool
    # - async def set_color_rgb(self, rgb: tuple[int, int, int]) -> bool
    # - async def set_color_temp(self, kelvin: int) -> bool

    # Utility methods

    async def is_online(self) -> bool:
        """
        Check if device is reachable.

        Returns:
            True if device responds
        """
        try:
            await self.get_status()
            return True
        except Exception:
            return False