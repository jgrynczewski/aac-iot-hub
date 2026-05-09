"""Tests for health check endpoints."""
import pytest
from datetime import datetime


def test_basic_health_check(client):
    """Test GET /api/health returns correct status."""
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert "timestamp" in data

    # Verify timestamp is valid ISO format
    timestamp = datetime.fromisoformat(data["timestamp"])
    assert isinstance(timestamp, datetime)


def test_detailed_status(client):
    """Test GET /api/v1/status returns detailed information."""
    response = client.get("/api/v1/status")

    assert response.status_code == 200

    data = response.json()
    assert "devices_total" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data

    # Initially no devices registered
    assert data["devices_total"] == 0
    assert data["uptime_seconds"] >= 0

    # Verify timestamp is valid ISO format
    timestamp = datetime.fromisoformat(data["timestamp"])
    assert isinstance(timestamp, datetime)


def test_root_endpoint(client):
    """Test GET / returns basic API information."""
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "AAC IoT Hub"
    assert data["version"] == "0.1.0"
    assert data["status"] == "running"
    assert data["docs"] == "/docs"
    assert data["api"] == "/api/v1/devices"


def test_favicon_endpoint(client):
    """Test GET /favicon.ico returns 204 No Content."""
    response = client.get("/favicon.ico")

    assert response.status_code == 204
    assert response.content == b""
