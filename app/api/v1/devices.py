"""
Device API endpoints - AAC IoT Hub.

Universal control endpoint design:
- ONE endpoint for all capabilities: PUT /devices/{id}/control
- Client sends: {"properties": {"power": "on", ...}}
- YAGNI: Start with power only, expand later
"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

from app.schemas import (
    Device,
    DeviceCapabilities,
    DeviceControlRequest,
    SuccessResponse,
    ErrorResponse,
    ErrorDetail,
)
from app.services import device_registry, discovery_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


@router.get("", response_model=dict)
async def list_devices():
    """
    List all discovered devices.

    Returns device count and list of all devices with their current status.
    """
    devices = await device_registry.get_all_status()
    return {
        "devices": devices,
        "count": len(devices),
    }


@router.post("/discover", response_model=dict)
async def discover_devices(timeout: int = 5):
    """
    Trigger device discovery.

    Starts SSDP discovery for Yeelight devices.
    Discovered devices are automatically registered.

    Args:
        timeout: Discovery timeout in seconds (default: 5)

    Returns:
        Number of discovered devices and their details
    """
    logger.info(f"Starting device discovery (timeout: {timeout}s)")
    discovered_ids = await discovery_service.discover_all(timeout=timeout)
    devices = await device_registry.get_all_status()

    logger.info(f"Discovery complete: {len(discovered_ids)} device(s) found")
    return {
        "discovered": len(discovered_ids),
        "device_ids": discovered_ids,
        "devices": devices
    }


@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str):
    """
    Get specific device details and current status.

    Args:
        device_id: Device identifier

    Returns:
        Device object with current status

    Raises:
        404: Device not found
    """
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found"
        )

    return await adapter.get_status()


@router.get("/{device_id}/capabilities", response_model=DeviceCapabilities)
async def get_capabilities(device_id: str):
    """
    Get device capabilities for GUI rendering.

    Returns detailed metadata about device capabilities:
    - Widget types (toggle, slider, color picker, etc.)
    - Valid ranges and values
    - Current state

    Client uses this to build dynamic UI.

    Args:
        device_id: Device identifier

    Returns:
        DeviceCapabilities object with widget metadata

    Raises:
        404: Device not found
    """
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found"
        )

    return await adapter.get_capabilities()


@router.put("/{device_id}/control", response_model=SuccessResponse)
async def control_device(device_id: str, request: DeviceControlRequest):
    """
    Universal control endpoint - controls ANY device capability.

    This is the MAIN control endpoint. Client sends any capability changes
    in a single request.

    Examples:
        - {"properties": {"power": "on"}}
        - {"properties": {"power": "toggle"}}
        - Future: {"properties": {"power": "on", "brightness": 80}}
        - Future: {"properties": {"rgb": [255, 0, 0]}}

    YAGNI: Currently only "power" is implemented.
    Future capabilities will be added as needed.

    Args:
        device_id: Device identifier
        request: DeviceControlRequest with properties dict

    Returns:
        SuccessResponse with applied changes

    Raises:
        404: Device not found
        400: Invalid capability or value
        500: Device control failed
    """
    # Get device adapter
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found"
        )

    logger.info(f"Control request for {device_id}: {request.properties}")

    # Apply each property change
    applied_changes = {}

    for capability, value in request.properties.items():
        try:
            # Route to appropriate adapter method based on capability
            if capability == "power":
                # YAGNI: Only power control for now
                await adapter.set_power(value)
                applied_changes[capability] = value

            # Future capabilities (add when implemented):
            # elif capability == "brightness":
            #     await adapter.set_brightness(value)
            #     applied_changes[capability] = value
            # elif capability == "rgb":
            #     await adapter.set_color_rgb(value)
            #     applied_changes[capability] = value
            # elif capability == "color_temp":
            #     await adapter.set_color_temp(value)
            #     applied_changes[capability] = value

            else:
                # Unknown capability - check if device supports it
                caps = await adapter.get_capabilities()
                if capability not in caps.capabilities:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Device {device_id} doesn't support capability: {capability}"
                    )
                else:
                    # Capability exists but not implemented yet
                    raise HTTPException(
                        status_code=501,
                        detail=f"Capability '{capability}' not yet implemented"
                    )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except ValueError as e:
            # Invalid value for capability
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value for {capability}: {str(e)}"
            )
        except Exception as e:
            # Device communication error
            logger.error(f"Failed to set {capability} on {device_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to control device: {str(e)}"
            )

    logger.info(f"Successfully applied changes to {device_id}: {applied_changes}")

    return SuccessResponse(
        success=True,
        data={
            "device_id": device_id,
            "applied": applied_changes
        }
    )