# AAC IoT Hub

**Local IoT device control hub with REST API**

**Status:** ✅ Production Ready (Manual Testing Passed - 2026-05-09)

Control your smart home devices locally without cloud dependency. Currently supports Yeelight bulbs with unified REST API.

## Quick Start

**This project is production-ready and has been tested with real Yeelight devices.**

### Prerequisites
- Docker & Docker Compose
- Yeelight bulbs with "LAN Control" enabled (see [Yeelight docs](docs/yeelight.md))

### Run

```bash
docker compose up -d
```

**Note:** Modern Docker uses `docker compose` (V2 plugin). If you have older standalone version, use `docker-compose` instead.

API available at: `http://localhost:8765`

### Verify

```bash
# Health check
curl http://localhost:8765/api/health

# API documentation
# In browser, open: http://localhost:8765/docs
```

## API Usage

### Discover devices
```bash
curl -X POST http://localhost:8765/api/v1/devices/discover
```

### List devices
```bash
curl http://localhost:8765/api/v1/devices
```

### Control device
```bash
# Turn on
curl -X PUT http://localhost:8765/api/v1/devices/{device_id}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on"}}'

# Turn off
curl -X PUT http://localhost:8765/api/v1/devices/{device_id}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "off"}}'

# Toggle power
curl -X PUT http://localhost:8765/api/v1/devices/{device_id}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "toggle"}}'
```

**Note:** Currently only power control is implemented. Brightness, color, and other features are planned for future releases.

### Get device capabilities
```bash
curl http://localhost:8765/api/v1/devices/{device_id}/capabilities
```

**Interactive API docs:** `http://localhost:8765/docs` (Swagger UI)

**Complete API examples:** See [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md) for detailed usage guide with all endpoints and error handling.

## Configuration

Use environment variables to configure:

```bash
# Custom port
AAC_API_PORT=9765 docker compose up -d

# Debug logging
AAC_LOG_LEVEL=debug docker compose up -d
```

Or create `.env` file:
```env
AAC_API_PORT=9765
AAC_LOG_LEVEL=debug
```

## Development

### Local setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8765
```

### Run tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_health.py

# Run with coverage
pytest --cov=app tests/
```

**Test Summary:**
- 39 integration tests covering all API endpoints
- Mock-based testing (no real hardware required)
- Full coverage of error handling and edge cases

## Architecture

See [Architecture Decision Records](docs/adr/) for design decisions:
- [ADR-000](docs/adr/adr-000-device-type-selection.md) - Device type selection (Yeelight)
- [ADR-001](docs/adr/adr-001-containerization-and-deployment.md) - Docker deployment
- [ADR-002](docs/adr/adr-002-docker-network-configuration.md) - Network configuration
- [ADR-003](docs/adr/adr-003-http-api-protocol.md) - REST API design

## Supported Devices

### Current
- **Yeelight** - Color bulbs, tunable white bulbs

### Planned
- **Shelly** - RGBW bulbs (when discovery issues are resolved)

### Research
- [Device Expansion Research](docs/future-devices.md) - Analysis of additional IoT devices (robots with cameras, drones, IP cameras, sensors) for potential integration

## POC Scripts

Early proof-of-concept scripts are available:

### Yeelight POC
```bash
pip install yeelight
python yeelight_toggle.py
```

### Shelly POC
```bash
pip install zeroconf requests
python shelly_toggle.py
```

See original device documentation:
- [Yeelight POC docs](docs/yeelight.md)
- [Shelly POC docs](docs/shelly.md)

## Project Status

**Current:** ✅ MVP Complete - Production Ready (100% complete)

**Completed:**
- [x] REST API for device control (power on/off/toggle)
- [x] Docker containerization with host network mode
- [x] Unified API architecture for multiple device types
- [x] SSDP discovery for Yeelight devices
- [x] Manual testing passed (2026-05-09)
- [x] Integration tests - 39 tests passing (2026-05-09)

**Next Phase (Post-MVP):**
- [ ] Additional capabilities (brightness, color, effects)
- [ ] WebSocket for real-time updates
- [ ] Persistence (device registry storage)
- [ ] Web UI
- [ ] Additional device types (Shelly, etc.)

See [docs/STATUS.md](docs/STATUS.md) for detailed implementation status.

## Technologies

- **Python 3.12**
- **FastAPI** - REST API framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Docker** - Containerization
- **yeelight** - Yeelight device library

## License

MIT