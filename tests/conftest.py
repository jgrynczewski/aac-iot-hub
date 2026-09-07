"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.services import device_registry


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear device registry before each test."""
    device_registry.clear()
    yield
    device_registry.clear()


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_yeelight_bulb():
    """Mock Yeelight bulb object."""
    bulb = Mock()
    bulb.get_properties.return_value = {
        "power": "off",
        "bright": "100",
        "ct": "4000",
        "rgb": "16711680",
        "hue": "359",
        "sat": "100",
        "name": "Yeelight Test Bulb",
        "fw_ver": "2.0.6_0066"
    }
    bulb.turn_on.return_value = ["ok"]
    bulb.turn_off.return_value = ["ok"]
    bulb.toggle.return_value = ["ok"]
    bulb.set_brightness.return_value = ["ok"]
    bulb.set_rgb.return_value = ["ok"]
    bulb.set_color_temp.return_value = ["ok"]
    bulb.start_flow.return_value = ["ok"]
    bulb.stop_flow.return_value = ["ok"]
    return bulb


@pytest.fixture
def mock_yeelight_discovery():
    """Mock yeelight.discover_bulbs response."""
    return [
        {
            "ip": "192.168.1.100",
            "port": 55443,
            "capabilities": {
                "id": "0x000000001234abcd",
                "model": "color4",
                "fw_ver": "2.0.6_0066",
                "support": "get_prop set_default set_power toggle",
                "power": "off",
                "bright": "100",
                "color_mode": "2",
                "ct": "4000",
                "rgb": "16711680",
                "hue": "359",
                "sat": "100",
                "name": "Yeelight Test"
            }
        }
    ]


@pytest.fixture
def mock_yeelight_adapter(mock_yeelight_bulb):
    """Mock YeelightAdapter with a mock bulb."""
    from app.services.yeelight_adapter import YeelightAdapter

    # Patch Bulb constructor to return our mock
    with patch('app.services.yeelight_adapter.Bulb', return_value=mock_yeelight_bulb):
        adapter = YeelightAdapter(
            device_id="yeelight_0x000000001234abcd",
            ip="192.168.1.100",
            model="color4"
        )
        yield adapter
