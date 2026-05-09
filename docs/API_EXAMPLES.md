# AAC IoT Hub - API Usage Examples

Quick reference for manual testing with real Yeelight devices.

## Prerequisites

1. Build and run the container:
```bash
docker compose up -d
```

2. Check container health:
```bash
docker compose ps
# Should show "healthy" status after ~5 seconds
```

3. View logs:
```bash
docker compose logs -f aac-iot-hub
```

---

## API Endpoints

Base URL: `http://localhost:8765`

Interactive docs: `http://localhost:8765/docs`

---

## 1. Health Check

Verify API is running:

```bash
curl http://localhost:8765/api/health
```

**Expected response:**
```json
{
  "status": "ok",
  "version": "0.1.0",
  "timestamp": "2026-05-03T12:34:56.789123"
}
```

---

## 2. Detailed Status

Get API status with device count:

```bash
curl http://localhost:8765/api/v1/status
```

**Expected response:**
```json
{
  "devices_total": 0,
  "uptime_seconds": 42,
  "timestamp": "2026-05-03T12:34:56.789123"
}
```

---

## 3. Device Discovery

**IMPORTANT**: Make sure your Yeelight bulb has:
- LAN Control enabled (in Yeelight app settings)
- Same network as the container (host network mode)

Trigger SSDP discovery:

```bash
curl -X POST "http://localhost:8765/api/v1/devices/discover?timeout=5"
```

**Expected response (with Yeelight found):**
```json
{
  "discovered": 1,
  "device_ids": ["yeelight_0x000000001234abcd"],
  "devices": [
    {
      "id": "yeelight_0x000000001234abcd",
      "name": "Yeelight color4",
      "type": "yeelight",
      "model": "color4",
      "ip": "192.168.1.100",
      "capabilities": ["power"],
      "status": {
        "power": "off",
        "online": true,
        "last_seen": "2026-05-03T12:34:56.789123"
      },
      "firmware": "2.0.6_0066"
    }
  ]
}
```

**Expected response (no devices found):**
```json
{
  "discovered": 0,
  "device_ids": [],
  "devices": []
}
```

**Troubleshooting if no devices found:**
- Check Yeelight app: Settings → Device Info → LAN Control (must be ON)
- Verify device is on same network
- Check container logs: `docker compose logs -f`
- Try increasing timeout: `?timeout=10`

---

## 4. List All Devices

Get all discovered devices:

```bash
curl http://localhost:8765/api/v1/devices
```

**Expected response:**
```json
{
  "devices": [
    {
      "id": "yeelight_0x000000001234abcd",
      "name": "Yeelight color4",
      "type": "yeelight",
      "model": "color4",
      "ip": "192.168.1.100",
      "capabilities": ["power"],
      "status": {
        "power": "off",
        "online": true,
        "last_seen": "2026-05-03T12:34:56.789123"
      },
      "firmware": "2.0.6_0066"
    }
  ],
  "count": 1
}
```

---

## 5. Get Device Status

Get specific device details (replace `DEVICE_ID` with actual ID from discovery):

```bash
DEVICE_ID="yeelight_0x000000003a12b002"
curl "http://localhost:8765/api/v1/devices/${DEVICE_ID}"
```

**Expected response:**
```json
{
  "id": "yeelight_0x000000001234abcd",
  "name": "Yeelight color4",
  "type": "yeelight",
  "model": "color4",
  "ip": "192.168.1.100",
  "capabilities": ["power"],
  "status": {
    "power": "off",
    "online": true,
    "last_seen": "2026-05-03T12:34:56.789123"
  },
  "firmware": "2.0.6_0066"
}
```

---

## 6. Get Device Capabilities

Get capabilities metadata for GUI rendering:

```bash
DEVICE_ID="yeelight_0x000000003a12b002"
curl "http://localhost:8765/api/v1/devices/${DEVICE_ID}/capabilities"
```

**Expected response:**
```json
{
  "device_id": "yeelight_0x000000001234abcd",
  "type": "yeelight",
  "model": "color4",
  "capabilities": {
    "power": {
      "widget": "toggle",
      "label": "Power",
      "states": ["on", "off", "toggle"],
      "current": "off"
    }
  },
  "metadata": {
    "firmware": "2.0.6_0066",
    "online": true,
    "last_seen": "2026-05-03T12:34:56.789123"
  }
}
```

---

## 7. Control Device - Turn ON

**MAIN ENDPOINT** - Universal control endpoint:

```bash
DEVICE_ID="yeelight_0x000000003a12b002"
curl -X PUT "http://localhost:8765/api/v1/devices/${DEVICE_ID}/control" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on"}}'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "device_id": "yeelight_0x000000001234abcd",
    "applied": {
      "power": "on"
    }
  }
}
```

**Note:** The bulb should turn ON immediately.

---

## 8. Control Device - Turn OFF

```bash
DEVICE_ID="yeelight_0x000000003a12b002"
curl -X PUT "http://localhost:8765/api/v1/devices/${DEVICE_ID}/control" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "off"}}'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "device_id": "yeelight_0x000000001234abcd",
    "applied": {
      "power": "off"
    }
  }
}
```

---

## 9. Control Device - Toggle

```bash
DEVICE_ID="yeelight_0x000000003a12b002"
curl -X PUT "http://localhost:8765/api/v1/devices/${DEVICE_ID}/control" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "toggle"}}'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "device_id": "yeelight_0x000000001234abcd",
    "applied": {
      "power": "toggle"
    }
  }
}
```

**Note:** The bulb should switch state (off→on or on→off).

---

## Error Responses

### Device Not Found (404)

```bash
curl "http://localhost:8765/api/v1/devices/invalid_id"
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "HTTP_404",
    "message": "Device invalid_id not found"
  }
}
```

### Invalid Capability (400)

```bash
DEVICE_ID="yeelight_0x000000003a12b002"
curl -X PUT "http://localhost:8765/api/v1/devices/${DEVICE_ID}/control" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"brightness": 80}}'
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "HTTP_501",
    "message": "Capability 'brightness' not yet implemented"
  }
}
```

### Invalid Power Value (400)

```bash
DEVICE_ID="yeelight_0x000000003a12b002"
curl -X PUT "http://localhost:8765/api/v1/devices/${DEVICE_ID}/control" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "invalid"}}'
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "HTTP_400",
    "message": "Invalid value for power: Invalid power state: invalid. Use 'on', 'off', or 'toggle'"
  }
}
```

---

## Complete Test Sequence

Full end-to-end test with real Yeelight:

```bash
# 1. Health check
curl http://localhost:8765/api/health

# 2. Discover devices (wait 5 seconds)
curl -X POST "http://localhost:8765/api/v1/devices/discover?timeout=5"

# 3. Get device ID from response, then list all
curl http://localhost:8765/api/v1/devices

# 4. Set DEVICE_ID from step 3
DEVICE_ID="yeelight_0x000000001234abcd"  # Replace with actual ID

# 5. Get device status
curl "http://localhost:8765/api/v1/devices/${DEVICE_ID}"

# 6. Get capabilities
curl "http://localhost:8765/api/v1/devices/${DEVICE_ID}/capabilities"

# 7. Turn ON (bulb should light up)
curl -X PUT "http://localhost:8765/api/v1/devices/${DEVICE_ID}/control" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on"}}'

# Wait 2 seconds, then verify status changed
sleep 2
curl "http://localhost:8765/api/v1/devices/${DEVICE_ID}" | grep '"power"'

# 8. Turn OFF (bulb should turn off)
curl -X PUT "http://localhost:8765/api/v1/devices/${DEVICE_ID}/control" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "off"}}'

# 9. Toggle (bulb should turn back on)
curl -X PUT "http://localhost:8765/api/v1/devices/${DEVICE_ID}/control" \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "toggle"}}'
```

---

## Swagger UI

For interactive testing, open in browser:

```
http://localhost:8765/docs
```

Features:
- Try out all endpoints interactively
- See request/response schemas
- Automatic validation
- Copy curl commands

---

## Container Management

```bash
# Start container
docker compose up -d

# View logs
docker compose logs -f aac-iot-hub

# Check health status
docker compose ps

# Restart container
docker compose restart

# Stop container
docker compose down

# Rebuild after code changes
docker compose up -d --build

# View container stats
docker stats aac-iot-hub
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose logs aac-iot-hub

# Common issues:
# - Port 8765 already in use: `lsof -i :8765`
# - Build errors: `docker compose build --no-cache`
```

### Discovery finds no devices

1. **Check Yeelight LAN Control:**
   - Open Yeelight app
   - Select device → Settings (⚙️)
   - Enable "LAN Control"

2. **Verify network:**
   - Device and container must be on same network
   - Host network mode should handle this automatically

3. **Check SSDP multicast:**
   ```bash
   # From container
   docker exec -it aac-iot-hub python3 -c "from yeelight import discover_bulbs; print(discover_bulbs(timeout=5))"
   ```

4. **Increase timeout:**
   ```bash
   curl -X POST "http://localhost:8765/api/v1/devices/discover?timeout=10"
   ```

### Control commands fail

1. **Device offline:**
   - Check device status: `GET /devices/{id}`
   - Ping device: `ping <device_ip>`

2. **Check container logs:**
   ```bash
   docker compose logs -f aac-iot-hub
   ```

3. **Verify device capabilities:**
   ```bash
   curl "http://localhost:8765/api/v1/devices/${DEVICE_ID}/capabilities"
   ```

---

## Next Steps

After successful manual testing:
- Phase 7: Write integration tests
- Phase 7: Update README with production configuration
- Future: Add brightness, color, color_temp controls
- Future: Add persistence (SQLite)
- Future: Add WebSocket for real-time updates