"""
Yeelight Adapter - Implementation for Yeelight smart bulbs.

YAGNI: Start with power on/off only, expand later with brightness, color, etc.
"""

import asyncio
from datetime import datetime
from yeelight import Bulb

from app.services.device_adapter import DeviceAdapter
from app.schemas.device import Device, DeviceStatus, DeviceCapabilities


class YeelightAdapter(DeviceAdapter):
    """
    Adapter for Yeelight smart bulbs.

    Uses yeelight library for communication.
    """

    def __init__(self, device_id: str, ip: str, model: str):
        """Initialize Yeelight adapter."""
        super().__init__(device_id, ip, model)
        # Create Bulb instance (yeelight library)
        # auto_on=False - don't automatically turn on when connecting
        self.bulb = Bulb(ip, auto_on=False)

    def _get_type(self) -> str:
        """Return device type."""
        return "yeelight"

    async def get_status(self) -> Device:
        """
        Get current device status from Yeelight bulb.

        Uses yeelight library to query device properties.
        """
        # Get properties from bulb (sync call → run in executor)
        props = await self._run_in_executor(self.bulb.get_properties)

        # Create status (YAGNI: only power for now)
        status = DeviceStatus(
            power=props.get("power", "off"),  # "on" | "off"
            online=True,  # If we got here, device is online
            last_seen=datetime.now()
        )

        # Create Device object
        return Device(
            id=self.device_id,
            name=f"Yeelight {self.model}",  # Default name, can be changed later
            type=self.type,
            model=self.model,
            ip=self.ip,
            capabilities=["power"],  # YAGNI: only power on/off for now
            status=status,
            firmware=props.get("fw_ver")  # Firmware version
        )

    async def get_capabilities(self) -> DeviceCapabilities:
        """
        Get detailed capabilities for GUI rendering.

        Returns metadata about what controls to show:
        - power: toggle button
        """
        status = await self.get_status()

        return DeviceCapabilities(
            device_id=self.device_id,
            type=self.type,
            model=self.model,
            capabilities={
                "power": {
                    "widget": "toggle",  # GUI: render toggle button
                    "label": "Power",
                    "states": ["on", "off", "toggle"],
                    "current": status.status.power
                }
                # Future: add brightness, color_temp, rgb when implemented
            },
            metadata={
                "firmware": status.firmware,
                "online": status.status.online,
                "last_seen": status.status.last_seen.isoformat()
            }
        )

    async def set_power(self, state: str) -> bool:
        """
        Set power state of Yeelight bulb.

        Args:
            state: "on" | "off" | "toggle"

        Returns:
            True if successful

        Raises:
            Exception if command fails
        """
        if state == "toggle":
            await self._run_in_executor(self.bulb.toggle)
        elif state == "on":
            await self._run_in_executor(self.bulb.turn_on)
        elif state == "off":
            await self._run_in_executor(self.bulb.turn_off)
        else:
            raise ValueError(f"Invalid power state: {state}. Use 'on', 'off', or 'toggle'")

        return True

    # Helper methods

    async def _run_in_executor(self, func, *args):
        """
        Run synchronous yeelight methods in thread pool.

        This prevents blocking the async event loop.

        Args:
            func: Synchronous function to run
            *args: Arguments for the function

        Returns:
            Function result
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)