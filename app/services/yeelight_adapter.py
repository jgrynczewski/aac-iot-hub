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
        - brightness: slider (1-100)
        - color: color picker (8 preset colors)
        - temperature: selector (3 presets: warm/neutral/cold)
        - effects: available flow effects
        """
        from app.services.color_presets import get_color_names, get_temperature_names
        from app.services.flow_effects import get_effect_names

        status = await self.get_status()

        # Get current bulb properties for detailed state
        props = await self._run_in_executor(self.bulb.get_properties)

        return DeviceCapabilities(
            device_id=self.device_id,
            type=self.type,
            model=self.model,
            capabilities={
                "power": {
                    "widget": "toggle",
                    "label": "Power",
                    "states": ["on", "off", "toggle"],
                    "current": status.status.power
                },
                "brightness": {
                    "widget": "slider",
                    "label": "Brightness",
                    "min": 1,
                    "max": 100,
                    "step": 1,
                    "unit": "%",
                    "current": int(props.get("bright", 100))
                },
                "color": {
                    "widget": "color_picker",
                    "label": "Color",
                    "presets": get_color_names(),  # ["blue", "green", "orange", "pink", ...]
                    "current": None  # Could decode RGB from props.get("rgb") if needed
                },
                "temperature": {
                    "widget": "selector",
                    "label": "Color Temperature",
                    "options": get_temperature_names(),  # ["cold", "neutral", "warm"]
                    "current": None  # Could map from props.get("ct") to preset if needed
                },
                "effects": {
                    "widget": "effect_buttons",
                    "label": "Light Effects",
                    "available": get_effect_names(),  # ["disco", "ocean", "police", ...]
                    "description": "Animated light effects (loop until stopped)"
                }
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

    async def set_brightness(self, value: int) -> bool:
        """
        Set brightness level.

        Args:
            value: Brightness 1-100 (Yeelight doesn't support 0)

        Returns:
            True if successful

        Raises:
            Exception if command fails

        Note:
            Validation (1-100 range) is done in BrightnessHandler.
            Adapter just executes the command.
        """
        await self._run_in_executor(self.bulb.set_brightness, value)
        return True

    async def set_rgb(self, r: int, g: int, b: int) -> bool:
        """
        Set RGB color.

        Args:
            r: Red component 0-255
            g: Green component 0-255
            b: Blue component 0-255

        Returns:
            True if successful

        Raises:
            Exception if command fails

        Note:
            Yeelight library expects three separate r, g, b arguments
            Validation is done in RGBHandler.
        """
        # Yeelight library expects three separate arguments
        await self._run_in_executor(lambda: self.bulb.set_rgb(r, g, b))
        return True

    async def set_color_temp(self, kelvin: int) -> bool:
        """
        Set color temperature.

        Args:
            kelvin: Color temperature in Kelvin (1700-6500 for Yeelight)

        Returns:
            True if successful

        Raises:
            Exception if command fails

        Note:
            Validation (temperature presets) is done in ColorTempHandler.
            Adapter just executes the command.
        """
        await self._run_in_executor(self.bulb.set_color_temp, kelvin)
        return True

    async def start_flow(self, flow) -> bool:
        """
        Start a flow effect.

        Args:
            flow: yeelight.Flow object with effect definition

        Returns:
            True if successful

        Raises:
            Exception if command fails

        Note:
            Flow runs in a loop until stop_flow() is called.
            Use flow_effects.create_flow() to create Flow objects.
        """
        await self._run_in_executor(self.bulb.start_flow, flow)
        return True

    async def stop_flow(self) -> bool:
        """
        Stop currently running flow effect.

        Returns:
            True if successful

        Raises:
            Exception if command fails

        Note:
            Returns device to state before flow started (Flow.actions.recover).
        """
        await self._run_in_executor(self.bulb.stop_flow)
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