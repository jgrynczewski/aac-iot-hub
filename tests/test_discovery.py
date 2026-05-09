"""Tests for discovery service."""
import pytest
from unittest.mock import patch, Mock

from app.services import discovery_service, device_registry
from app.services.yeelight_adapter import YeelightAdapter


@pytest.mark.asyncio
async def test_discover_all_with_devices(mock_yeelight_discovery):
    """Test DiscoveryService.discover_all finds and registers devices."""
    with patch("app.services.discovery.discover_bulbs", return_value=mock_yeelight_discovery):
        device_ids = await discovery_service.discover_all(timeout=2)

        assert len(device_ids) == 1
        assert "yeelight_0x000000001234abcd" in device_ids[0]

        # Verify device was registered
        assert device_registry.count() == 1

        # Verify registered device is correct type
        registered_device = device_registry.get(device_ids[0])
        assert isinstance(registered_device, YeelightAdapter)
        assert registered_device.ip == "192.168.1.100"
        assert registered_device.model == "color4"


@pytest.mark.asyncio
async def test_discover_all_no_devices():
    """Test DiscoveryService.discover_all when no devices found."""
    with patch("app.services.discovery.discover_bulbs", return_value=[]):
        device_ids = await discovery_service.discover_all(timeout=2)

        assert device_ids == []
        assert device_registry.count() == 0


@pytest.mark.asyncio
async def test_discover_all_custom_timeout(mock_yeelight_discovery):
    """Test DiscoveryService.discover_all with custom timeout."""
    with patch("app.services.discovery.discover_bulbs", return_value=mock_yeelight_discovery) as mock_discover:
        await discovery_service.discover_all(timeout=10)

        # Verify discover_bulbs was called with custom timeout
        mock_discover.assert_called_once_with(10)


@pytest.mark.asyncio
async def test_discover_all_multiple_devices():
    """Test DiscoveryService.discover_all with multiple devices."""
    mock_devices = [
        {
            "ip": "192.168.1.100",
            "port": 55443,
            "capabilities": {
                "id": "0x000000001234abcd",
                "model": "color4",
                "fw_ver": "2.0.6",
            }
        },
        {
            "ip": "192.168.1.101",
            "port": 55443,
            "capabilities": {
                "id": "0x000000005678efgh",
                "model": "color4",
                "fw_ver": "2.0.6",
            }
        }
    ]

    with patch("app.services.discovery.discover_bulbs", return_value=mock_devices):
        device_ids = await discovery_service.discover_all(timeout=5)

        assert len(device_ids) == 2
        assert device_registry.count() == 2

        # Verify both devices were registered
        for device_id in device_ids:
            adapter = device_registry.get(device_id)
            assert isinstance(adapter, YeelightAdapter)


@pytest.mark.asyncio
async def test_discover_all_error_handling():
    """Test DiscoveryService.discover_all propagates discovery errors."""
    with patch("app.services.discovery.discover_bulbs", side_effect=Exception("Network error")):
        # Exception should propagate from discover_bulbs
        with pytest.raises(Exception, match="Network error"):
            await discovery_service.discover_all(timeout=2)


@pytest.mark.asyncio
async def test_discover_all_invalid_device_data():
    """Test DiscoveryService.discover_all with invalid device data."""
    # Device with missing required fields
    invalid_devices = [
        {
            "ip": "192.168.1.100",
            # Missing port and capabilities
        }
    ]

    with patch("app.services.discovery.discover_bulbs", return_value=invalid_devices):
        device_ids = await discovery_service.discover_all(timeout=2)

        # Should handle gracefully, either skip invalid device or register with defaults
        assert isinstance(device_ids, list)


@pytest.mark.asyncio
async def test_discover_yeelight_integration(mock_yeelight_discovery):
    """Test _discover_yeelight internal method."""
    with patch("app.services.discovery.discover_bulbs", return_value=mock_yeelight_discovery):
        # Access internal method
        device_ids = await discovery_service._discover_yeelight(timeout=3)

        assert len(device_ids) == 1
        assert device_registry.count() == 1


@pytest.mark.asyncio
async def test_discover_all_duplicate_devices(mock_yeelight_discovery):
    """Test DiscoveryService.discover_all handles duplicate device IDs."""
    # Run discovery twice
    with patch("app.services.discovery.discover_bulbs", return_value=mock_yeelight_discovery):
        device_ids_1 = await discovery_service.discover_all(timeout=2)
        device_ids_2 = await discovery_service.discover_all(timeout=2)

        # Second discovery should update existing device, not duplicate
        assert len(device_ids_1) == len(device_ids_2)
        assert device_registry.count() == 1  # Still only one device
