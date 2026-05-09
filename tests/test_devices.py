"""Tests for device API endpoints."""
import pytest
from unittest.mock import patch

from app.services import device_registry


def test_list_devices_empty(client):
    """Test GET /api/v1/devices with no devices."""
    response = client.get("/api/v1/devices")

    assert response.status_code == 200
    data = response.json()

    assert data["devices"] == []
    assert data["count"] == 0


def test_list_devices_with_devices(client, mock_yeelight_adapter):
    """Test GET /api/v1/devices with registered devices."""
    # Register a mock device
    device_registry.register(mock_yeelight_adapter)

    response = client.get("/api/v1/devices")

    assert response.status_code == 200
    data = response.json()

    assert data["count"] == 1
    assert len(data["devices"]) == 1

    device = data["devices"][0]
    assert device["id"] == "yeelight_0x000000001234abcd"
    assert device["type"] == "yeelight"
    assert device["ip"] == "192.168.1.100"


def test_get_device_not_found(client):
    """Test GET /api/v1/devices/{id} with non-existent device."""
    response = client.get("/api/v1/devices/nonexistent_device")

    assert response.status_code == 404
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["error"]["message"].lower()


def test_get_device_details(client, mock_yeelight_adapter):
    """Test GET /api/v1/devices/{id} returns device details."""
    device_registry.register(mock_yeelight_adapter)
    device_id = mock_yeelight_adapter.device_id

    response = client.get(f"/api/v1/devices/{device_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == device_id
    assert data["type"] == "yeelight"
    assert data["ip"] == "192.168.1.100"
    assert "status" in data
    assert data["status"]["power"] == "off"


def test_get_device_capabilities(client, mock_yeelight_adapter):
    """Test GET /api/v1/devices/{id}/capabilities."""
    device_registry.register(mock_yeelight_adapter)
    device_id = mock_yeelight_adapter.device_id

    response = client.get(f"/api/v1/devices/{device_id}/capabilities")

    assert response.status_code == 200
    data = response.json()

    assert data["device_id"] == device_id
    assert data["type"] == "yeelight"
    assert "capabilities" in data
    assert "power" in data["capabilities"]

    power_capability = data["capabilities"]["power"]
    assert power_capability["widget"] == "toggle"
    assert power_capability["label"] == "Power"
    assert "on" in power_capability["states"]
    assert "off" in power_capability["states"]
    assert "toggle" in power_capability["states"]


def test_get_capabilities_device_not_found(client):
    """Test GET /api/v1/devices/{id}/capabilities with non-existent device."""
    response = client.get("/api/v1/devices/nonexistent/capabilities")

    assert response.status_code == 404
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["error"]["message"].lower()


def test_control_device_power_on(client, mock_yeelight_adapter):
    """Test PUT /api/v1/devices/{id}/control with power on."""
    device_registry.register(mock_yeelight_adapter)
    device_id = mock_yeelight_adapter.device_id

    response = client.put(
        f"/api/v1/devices/{device_id}/control",
        json={"properties": {"power": "on"}}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["device_id"] == device_id
    assert data["data"]["applied"]["power"] == "on"

    # Verify the bulb method was called
    mock_yeelight_adapter.bulb.turn_on.assert_called_once()


def test_control_device_power_off(client, mock_yeelight_adapter):
    """Test PUT /api/v1/devices/{id}/control with power off."""
    device_registry.register(mock_yeelight_adapter)
    device_id = mock_yeelight_adapter.device_id

    response = client.put(
        f"/api/v1/devices/{device_id}/control",
        json={"properties": {"power": "off"}}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["applied"]["power"] == "off"

    mock_yeelight_adapter.bulb.turn_off.assert_called_once()


def test_control_device_power_toggle(client, mock_yeelight_adapter):
    """Test PUT /api/v1/devices/{id}/control with power toggle."""
    device_registry.register(mock_yeelight_adapter)
    device_id = mock_yeelight_adapter.device_id

    response = client.put(
        f"/api/v1/devices/{device_id}/control",
        json={"properties": {"power": "toggle"}}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["applied"]["power"] == "toggle"

    mock_yeelight_adapter.bulb.toggle.assert_called_once()


def test_control_device_invalid_power_value(client, mock_yeelight_adapter):
    """Test PUT /api/v1/devices/{id}/control with invalid power value."""
    device_registry.register(mock_yeelight_adapter)
    device_id = mock_yeelight_adapter.device_id

    response = client.put(
        f"/api/v1/devices/{device_id}/control",
        json={"properties": {"power": "invalid_state"}}
    )

    assert response.status_code == 400
    data = response.json()

    assert data["success"] is False
    assert "invalid" in data["error"]["message"].lower()


def test_control_device_not_found(client):
    """Test PUT /api/v1/devices/{id}/control with non-existent device."""
    response = client.put(
        "/api/v1/devices/nonexistent/control",
        json={"properties": {"power": "on"}}
    )

    assert response.status_code == 404
    data = response.json()

    assert data["success"] is False
    assert "not found" in data["error"]["message"].lower()


def test_control_device_unsupported_capability(client, mock_yeelight_adapter):
    """Test PUT /api/v1/devices/{id}/control with unsupported capability."""
    device_registry.register(mock_yeelight_adapter)
    device_id = mock_yeelight_adapter.device_id

    response = client.put(
        f"/api/v1/devices/{device_id}/control",
        json={"properties": {"brightness": 80}}
    )

    assert response.status_code == 400
    data = response.json()

    assert data["success"] is False


def test_discover_devices(client, mock_yeelight_discovery, mock_yeelight_bulb):
    """Test POST /api/v1/devices/discover."""
    with patch("app.services.discovery.discover_bulbs", return_value=mock_yeelight_discovery), \
         patch("app.services.yeelight_adapter.Bulb", return_value=mock_yeelight_bulb):
        response = client.post("/api/v1/devices/discover?timeout=2")

        assert response.status_code == 200
        data = response.json()

        assert data["discovered"] == 1
        assert len(data["device_ids"]) == 1
        assert len(data["devices"]) == 1

        device = data["devices"][0]
        assert device["type"] == "yeelight"
        assert device["ip"] == "192.168.1.100"
        assert "yeelight_0x000000001234abcd" in device["id"]


def test_discover_devices_custom_timeout(client, mock_yeelight_discovery):
    """Test POST /api/v1/devices/discover with custom timeout."""
    with patch("app.services.discovery.discover_bulbs", return_value=mock_yeelight_discovery) as mock_discover:
        response = client.post("/api/v1/devices/discover?timeout=10")

        assert response.status_code == 200

        # Verify discover_bulbs was called with correct timeout (positional arg)
        mock_discover.assert_called_once_with(10)


def test_discover_devices_no_devices_found(client):
    """Test POST /api/v1/devices/discover when no devices found."""
    with patch("app.services.discovery.discover_bulbs", return_value=[]):
        response = client.post("/api/v1/devices/discover")

        assert response.status_code == 200
        data = response.json()

        assert data["discovered"] == 0
        assert data["device_ids"] == []
        assert data["devices"] == []
