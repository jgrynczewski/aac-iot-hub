"""
Discovery Service - SSDP discovery for Yeelight devices.

Uses yeelight library's discover_bulbs() to find devices on local network.
YAGNI: Only Yeelight for now, no abstraction for other device types.
"""

import asyncio
import logging
from typing import List

from yeelight import discover_bulbs

from app.services.device_registry import device_registry
from app.services.yeelight_adapter import YeelightAdapter

logger = logging.getLogger(__name__)


class DiscoveryService:
    """
    Service for discovering Yeelight devices on local network.

    Uses SSDP (Simple Service Discovery Protocol) multicast:
    - Sends UDP broadcast to 239.255.255.250:1900
    - Waits for device responses
    - Creates adapters and registers discovered devices
    """

    async def discover_all(self, timeout: int = 5) -> List[str]:
        """
        Discover all Yeelight devices and register them.

        Args:
            timeout: How long to wait for responses in seconds (default: 5)

        Returns:
            List of discovered device IDs

        Example:
            >>> service = DiscoveryService()
            >>> device_ids = await service.discover_all(timeout=5)
            >>> print(f"Found {len(device_ids)} devices")
        """
        logger.info(f"Starting Yeelight discovery (timeout: {timeout}s)...")

        # Discover Yeelight devices (sync call → run in executor)
        discovered_ids = await self._discover_yeelight(timeout)

        logger.info(f"Discovery complete. Found {len(discovered_ids)} Yeelight device(s)")
        return discovered_ids

    async def _discover_yeelight(self, timeout: int) -> List[str]:
        """
        Discover Yeelight devices using SSDP.

        Args:
            timeout: Discovery timeout in seconds

        Returns:
            List of discovered device IDs
        """
        loop = asyncio.get_event_loop()

        # Run sync discover_bulbs in thread pool
        # discover_bulbs sends SSDP multicast and waits for responses
        bulbs = await loop.run_in_executor(None, discover_bulbs, timeout)

        if not bulbs:
            logger.warning("No Yeelight devices found")
            return []

        discovered_ids = []

        for bulb_info in bulbs:
            try:
                # Extract device info from discovery response
                ip = bulb_info['ip']
                port = bulb_info.get('port', 55443)  # Default Yeelight port
                capabilities = bulb_info.get('capabilities', {})

                # Generate device ID from capabilities ID (MAC address)
                device_id = f"yeelight_{capabilities.get('id', ip.replace('.', '_'))}"
                model = capabilities.get('model', 'unknown')

                logger.info(f"Found Yeelight: {device_id} at {ip}:{port} (model: {model})")

                # Create adapter for this device
                adapter = YeelightAdapter(
                    device_id=device_id,
                    ip=ip,
                    model=model
                )

                # Register in global registry
                device_registry.register(adapter)
                discovered_ids.append(device_id)

            except Exception as e:
                logger.error(f"Failed to process discovered device: {e}")
                continue

        return discovered_ids


# Global discovery service instance
discovery_service = DiscoveryService()