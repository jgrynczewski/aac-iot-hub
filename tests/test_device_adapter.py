"""Tests for device adapter implementations."""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from app.services.yeelight_adapter import YeelightAdapter
from app.schemas import Device, DeviceStatus


@pytest.mark.asyncio
async def test_yeelight_adapter_get_type(mock_yeelight_adapter):
    """Test YeelightAdapter returns correct device type."""
    device_type = mock_yeelight_adapter._get_type()
    assert device_type == "yeelight"


@pytest.mark.asyncio
async def test_yeelight_adapter_get_status(mock_yeelight_adapter):
    """Test YeelightAdapter.get_status returns device info."""
    device = await mock_yeelight_adapter.get_status()

    assert isinstance(device, Device)
    assert device.status.power == "off"
    assert device.status.online is True
    assert isinstance(device.status.last_seen, datetime)

    # Verify bulb.get_properties was called
    mock_yeelight_adapter.bulb.get_properties.assert_called_once()


@pytest.mark.asyncio
async def test_yeelight_adapter_get_status_power_on(mock_yeelight_adapter):
    """Test YeelightAdapter.get_status with power on."""
    mock_yeelight_adapter.bulb.get_properties.return_value = {
        "power": "on",
        "bright": "50",
        "fw_ver": "2.0.6"
    }

    device = await mock_yeelight_adapter.get_status()

    assert device.status.power == "on"
    assert device.status.online is True


@pytest.mark.asyncio
async def test_yeelight_adapter_get_capabilities(mock_yeelight_adapter):
    """Test YeelightAdapter.get_capabilities returns capabilities metadata."""
    capabilities = await mock_yeelight_adapter.get_capabilities()

    assert "power" in capabilities.capabilities
    power_cap = capabilities.capabilities["power"]

    assert power_cap["widget"] == "toggle"
    assert power_cap["label"] == "Power"
    assert set(power_cap["states"]) == {"on", "off", "toggle"}
    assert power_cap["current"] == "off"

    # Verify metadata
    assert capabilities.metadata["online"] is True
    assert "firmware" in capabilities.metadata


@pytest.mark.asyncio
async def test_yeelight_adapter_set_power_on(mock_yeelight_adapter):
    """Test YeelightAdapter.set_power with 'on' state."""
    await mock_yeelight_adapter.set_power("on")

    mock_yeelight_adapter.bulb.turn_on.assert_called_once()
    mock_yeelight_adapter.bulb.turn_off.assert_not_called()
    mock_yeelight_adapter.bulb.toggle.assert_not_called()


@pytest.mark.asyncio
async def test_yeelight_adapter_set_power_off(mock_yeelight_adapter):
    """Test YeelightAdapter.set_power with 'off' state."""
    await mock_yeelight_adapter.set_power("off")

    mock_yeelight_adapter.bulb.turn_off.assert_called_once()
    mock_yeelight_adapter.bulb.turn_on.assert_not_called()
    mock_yeelight_adapter.bulb.toggle.assert_not_called()


@pytest.mark.asyncio
async def test_yeelight_adapter_set_power_toggle(mock_yeelight_adapter):
    """Test YeelightAdapter.set_power with 'toggle' state."""
    await mock_yeelight_adapter.set_power("toggle")

    mock_yeelight_adapter.bulb.toggle.assert_called_once()
    mock_yeelight_adapter.bulb.turn_on.assert_not_called()
    mock_yeelight_adapter.bulb.turn_off.assert_not_called()


@pytest.mark.asyncio
async def test_yeelight_adapter_set_power_invalid_state(mock_yeelight_adapter):
    """Test YeelightAdapter.set_power with invalid state raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        await mock_yeelight_adapter.set_power("invalid_state")

    assert "Invalid power state" in str(exc_info.value)
    assert "invalid_state" in str(exc_info.value)

    # Verify no bulb methods were called
    mock_yeelight_adapter.bulb.turn_on.assert_not_called()
    mock_yeelight_adapter.bulb.turn_off.assert_not_called()
    mock_yeelight_adapter.bulb.toggle.assert_not_called()


@pytest.mark.asyncio
async def test_yeelight_adapter_is_online(mock_yeelight_adapter):
    """Test YeelightAdapter.is_online returns True when device responds."""
    is_online = await mock_yeelight_adapter.is_online()
    assert is_online is True


@pytest.mark.asyncio
async def test_yeelight_adapter_is_online_error(mock_yeelight_adapter):
    """Test YeelightAdapter.is_online returns False when device errors."""
    mock_yeelight_adapter.bulb.get_properties.side_effect = Exception("Connection error")

    is_online = await mock_yeelight_adapter.is_online()
    assert is_online is False


@pytest.mark.asyncio
async def test_yeelight_adapter_get_status_error_handling(mock_yeelight_adapter):
    """Test YeelightAdapter.get_status propagates errors."""
    mock_yeelight_adapter.bulb.get_properties.side_effect = Exception("Device offline")

    with pytest.raises(Exception, match="Device offline"):
        await mock_yeelight_adapter.get_status()


def test_yeelight_adapter_initialization():
    """Test YeelightAdapter initialization with valid parameters."""
    with patch('app.services.yeelight_adapter.Bulb'):
        adapter = YeelightAdapter(
            device_id="yeelight_test",
            ip="192.168.1.100",
            model="color4"
        )

        assert adapter.device_id == "yeelight_test"
        assert adapter.ip == "192.168.1.100"
        assert adapter.model == "color4"
        assert adapter._get_type() == "yeelight"


@pytest.mark.asyncio
async def test_yeelight_adapter_set_brightness_50(mock_yeelight_adapter):
    """Test YeelightAdapter.set_brightness with 50%."""
    mock_yeelight_adapter.bulb.set_brightness = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_brightness(50)

    assert result is True
    mock_yeelight_adapter.bulb.set_brightness.assert_called_once_with(50)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_brightness_min(mock_yeelight_adapter):
    """Test YeelightAdapter.set_brightness with minimum value (1)."""
    mock_yeelight_adapter.bulb.set_brightness = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_brightness(1)

    assert result is True
    mock_yeelight_adapter.bulb.set_brightness.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_brightness_max(mock_yeelight_adapter):
    """Test YeelightAdapter.set_brightness with maximum value (100)."""
    mock_yeelight_adapter.bulb.set_brightness = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_brightness(100)

    assert result is True
    mock_yeelight_adapter.bulb.set_brightness.assert_called_once_with(100)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_rgb_red(mock_yeelight_adapter):
    """Test YeelightAdapter.set_rgb with red color (255, 0, 0)."""
    mock_yeelight_adapter.bulb.set_rgb = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_rgb(255, 0, 0)

    assert result is True
    mock_yeelight_adapter.bulb.set_rgb.assert_called_once_with(255, 0, 0)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_rgb_green(mock_yeelight_adapter):
    """Test YeelightAdapter.set_rgb with green color (0, 255, 0)."""
    mock_yeelight_adapter.bulb.set_rgb = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_rgb(0, 255, 0)

    assert result is True
    mock_yeelight_adapter.bulb.set_rgb.assert_called_once_with(0, 255, 0)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_rgb_blue(mock_yeelight_adapter):
    """Test YeelightAdapter.set_rgb with blue color (0, 0, 255)."""
    mock_yeelight_adapter.bulb.set_rgb = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_rgb(0, 0, 255)

    assert result is True
    mock_yeelight_adapter.bulb.set_rgb.assert_called_once_with(0, 0, 255)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_rgb_purple(mock_yeelight_adapter):
    """Test YeelightAdapter.set_rgb with purple color (128, 0, 128)."""
    mock_yeelight_adapter.bulb.set_rgb = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_rgb(128, 0, 128)

    assert result is True
    mock_yeelight_adapter.bulb.set_rgb.assert_called_once_with(128, 0, 128)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_color_temp_warm(mock_yeelight_adapter):
    """Test YeelightAdapter.set_color_temp with warm temperature (2700K)."""
    mock_yeelight_adapter.bulb.set_color_temp = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_color_temp(2700)

    assert result is True
    mock_yeelight_adapter.bulb.set_color_temp.assert_called_once_with(2700)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_color_temp_neutral(mock_yeelight_adapter):
    """Test YeelightAdapter.set_color_temp with neutral temperature (4000K)."""
    mock_yeelight_adapter.bulb.set_color_temp = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_color_temp(4000)

    assert result is True
    mock_yeelight_adapter.bulb.set_color_temp.assert_called_once_with(4000)


@pytest.mark.asyncio
async def test_yeelight_adapter_set_color_temp_cold(mock_yeelight_adapter):
    """Test YeelightAdapter.set_color_temp with cold temperature (6500K)."""
    mock_yeelight_adapter.bulb.set_color_temp = Mock(return_value=["ok"])

    result = await mock_yeelight_adapter.set_color_temp(6500)

    assert result is True
    mock_yeelight_adapter.bulb.set_color_temp.assert_called_once_with(6500)
