"""
Device API endpoints - AAC IoT Hub.

Universal control endpoint design:
- ONE endpoint for all capabilities: PUT /devices/{id}/control
- Client sends: {"properties": {"power": "on", ...}}
- Uses Strategy Pattern + Registry for OCP compliance
- Each property delegated to its handler (zero if/elif)
"""

from fastapi import APIRouter, HTTPException
from typing import List
import logging

from app.schemas import (
    Device,
    DeviceCapabilities,
    DeviceControlRequest,
    EffectStartRequest,
    SuccessResponse,
    ErrorResponse,
    ErrorDetail,
)
from app.services import device_registry, discovery_service
from app.services.property_handlers import property_registry
from app.services import flow_effects

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

    Uses Strategy Pattern + Registry for OCP compliance:
    - Each property delegated to its handler
    - Zero if/elif chains
    - New properties require ZERO changes to this endpoint

    To add new property:
    1. Create PropertyHandler subclass in property_handlers.py
    2. Register in property_registry
    3. Done - this endpoint requires NO modifications

    Examples:
        - {"properties": {"power": "on"}}
        - {"properties": {"power": "toggle"}}
        - {"properties": {"power": "on", "brightness": 80}}
        - {"properties": {"rgb": [255, 0, 0]}}

    Currently supported: power
    Future: brightness, rgb, color_temp (added via handlers)

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

    # Delegate each property to its handler
    applied_changes = {}

    for property_name, value in request.properties.items():
        try:
            # Get handler for this property (raises ValueError if unknown)
            handler = property_registry.get(property_name)

            # Handle property (validates + executes)
            result = await handler.handle(adapter, value)
            applied_changes[property_name] = result

        except ValueError as e:
            # Validation error or unknown property
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

        except Exception as e:
            # Unexpected error (device communication, etc.)
            logger.error(
                f"Error handling property {property_name} for {device_id}: {e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set {property_name}: {str(e)}"
            )

    logger.info(f"Successfully applied changes to {device_id}: {applied_changes}")

    return SuccessResponse(
        success=True,
        data={
            "device_id": device_id,
            "applied": applied_changes
        }
    )


@router.post("/{device_id}/effect", response_model=SuccessResponse)
async def start_effect(device_id: str, request: EffectStartRequest):
    """
    Start a flow effect on the device.

    Flow effects are predefined light animations that loop infinitely
    until stopped via the stop_effect endpoint.

    Available effects:
    - disco: Fast color changes (party mode)
    - pulse: Breathing effect (red)
    - strobe: Fast flashing (white)
    - rainbow: Smooth rainbow cycle
    - police: Red/blue alternating (alert)
    - ocean: Calm ocean waves

    Args:
        device_id: Device identifier
        request: EffectStartRequest with effect_name

    Returns:
        SuccessResponse confirming effect started

    Raises:
        404: Device not found
        400: Invalid effect name
        500: Failed to start effect

    Example:
        POST /devices/{id}/effect
        {"effect_name": "disco"}
    """
    # Get device adapter
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found"
        )

    logger.info(f"Starting effect '{request.effect_name}' on {device_id}")

    try:
        # Create flow object for the requested effect
        flow = flow_effects.create_flow(request.effect_name)

        # Start the flow on the device
        await adapter.start_flow(flow)

        logger.info(f"Successfully started effect '{request.effect_name}' on {device_id}")

        return SuccessResponse(
            success=True,
            data={
                "device_id": device_id,
                "effect": request.effect_name,
                "status": "started"
            }
        )

    except ValueError as e:
        # Invalid effect name
        available_effects = flow_effects.get_effect_names()
        raise HTTPException(
            status_code=400,
            detail=f"{str(e)}. Available effects: {', '.join(available_effects)}"
        )

    except Exception as e:
        # Unexpected error (device communication, etc.)
        logger.error(
            f"Error starting effect '{request.effect_name}' on {device_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start effect: {str(e)}"
        )


@router.post("/{device_id}/effect/stop", response_model=SuccessResponse)
async def stop_effect(device_id: str):
    """
    Stop the currently running flow effect.

    Stops any running flow effect and returns the device to the state
    it was in before the effect started (Flow.actions.recover).

    Args:
        device_id: Device identifier

    Returns:
        SuccessResponse confirming effect stopped

    Raises:
        404: Device not found
        500: Failed to stop effect

    Example:
        POST /devices/{id}/effect/stop
    """
    # Get device adapter
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found"
        )

    logger.info(f"Stopping flow effect on {device_id}")

    try:
        # Stop the flow
        await adapter.stop_flow()

        logger.info(f"Successfully stopped flow effect on {device_id}")

        return SuccessResponse(
            success=True,
            data={
                "device_id": device_id,
                "status": "stopped"
            }
        )

    except Exception as e:
        # Unexpected error (device communication, etc.)
        logger.error(
            f"Error stopping flow effect on {device_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to stop effect: {str(e)}"
        )