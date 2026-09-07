# AAC IoT Hub

**Local IoT device control hub with REST API**

**Status:** ✅ MVP v2.0 Complete (2026-09-06)

Control your smart home devices locally without cloud dependency. Currently supports Yeelight bulbs with full color control, brightness, temperature, and effects.

## Quick Start

**This project is production-ready with comprehensive device control capabilities.**

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

### Get device capabilities
```bash
curl http://localhost:8765/api/v1/devices/{device_id}/capabilities
```

Returns full metadata for dynamic UI rendering including:
- Power control (toggle)
- Brightness (slider 1-100)
- Color palette (8 preset colors)
- Color temperature (3 presets: warm/neutral/cold)
- Light effects (6 animations)

### Control device properties

All device control uses a **single universal endpoint**: `PUT /devices/{device_id}/control`

```bash
# Turn on
curl -X PUT http://localhost:8765/api/v1/devices/{device_id}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on"}}'

# Set brightness
curl -X PUT http://localhost:8765/api/v1/devices/{device_id}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"brightness": 80}}'

# Set color (preset name)
curl -X PUT http://localhost:8765/api/v1/devices/{device_id}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"color": "red"}}'

# Set color temperature (preset name)
curl -X PUT http://localhost:8765/api/v1/devices/{device_id}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"temperature": "warm"}}'

# Combine multiple properties
curl -X PUT http://localhost:8765/api/v1/devices/{device_id}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on", "brightness": 100, "color": "blue"}}'
```

### Light effects

```bash
# Start effect (disco, pulse, strobe, rainbow, police, ocean)
curl -X POST http://localhost:8765/api/v1/devices/{device_id}/effect \
  -H "Content-Type: application/json" \
  -d '{"effect_name": "disco"}'

# Stop effect
curl -X POST http://localhost:8765/api/v1/devices/{device_id}/effect/stop
```

**Interactive API docs:** `http://localhost:8765/docs` (Swagger UI)

**Complete API examples:** See [docs/API_EXAMPLES.md](docs/API_EXAMPLES.md) for detailed usage guide.

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
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8765
```

### Run tests
```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_devices.py

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_devices.py::test_get_device_capabilities -v
```

**Test Summary:**
- **127 tests** covering all API endpoints and property handlers
- Mock-based testing (no real hardware required)
- Full coverage of error handling and edge cases
- Tests for power, brightness, color, temperature, and effects

## Architecture

### Strategy Pattern + Registry
Uses **Open/Closed Principle (OCP)** compliant architecture:
- Single universal control endpoint
- Property handlers for validation and execution
- Zero `if/elif` chains - fully extensible
- Adding new property requires **zero endpoint changes**

See [Architecture Decision Records](docs/adr/) for design decisions:
- [ADR-000](docs/adr/adr-000-device-type-selection.md) - Device type selection (Yeelight)
- [ADR-001](docs/adr/adr-001-containerization-and-deployment.md) - Docker deployment
- [ADR-002](docs/adr/adr-002-docker-network-configuration.md) - Network configuration
- [ADR-003](docs/adr/adr-003-http-api-protocol.md) - REST API design

**Implementation Plan:** See [docs/MVP_v2.0_PLAN.md](docs/MVP_v2.0_PLAN.md) for detailed architecture and implementation phases.

## Supported Devices

### Current
- **Yeelight** - Full control (power, brightness, 8 colors, 3 temperatures, 6 effects)

### Planned
- **Shelly** - RGBW bulbs (when discovery issues are resolved)

### Research
- [Device Expansion Research](docs/future-devices.md) - Analysis of additional IoT devices

## Features

### Device Control (MVP v2.0 ✅)
- ✅ Power on/off/toggle
- ✅ Brightness (1-100 slider)
- ✅ Color palette (8 preset colors: blue, green, orange, pink, purple, red, white, yellow)
- ✅ Color temperature (3 presets: cold 6500K, neutral 4000K, warm 2700K)
- ✅ Light effects (6 animations: disco, pulse, strobe, rainbow, police, ocean)

### API Architecture
- ✅ Universal control endpoint (Strategy Pattern)
- ✅ Property handlers with validation
- ✅ Dynamic capabilities endpoint for GUI
- ✅ Separate effect endpoints (start/stop)
- ✅ Full error handling and validation

## Project Status

**Current:** ✅ MVP v2.0 Complete (100% complete - 2026-09-06)

**Completed:**
- [x] MVP v1.0 - Basic power control
- [x] MVP v2.0 - Full device control:
  - [x] Property Handler System (Strategy Pattern + Registry)
  - [x] Brightness control (1-100)
  - [x] RGB color control (8 preset colors)
  - [x] Color temperature (3 presets)
  - [x] Flow effects (6 animations)
  - [x] Extended capabilities endpoint
- [x] 127 integration tests passing
- [x] Docker deployment with health checks
- [x] Interactive API documentation

**Next Phase (Post-MVP v2.0):**
- [ ] Scene presets (reading, movie, dinner modes)
- [ ] Favorites system (3 quick-access slots)
- [ ] Persistence (SQLite for devices/settings)
- [ ] WebSocket for real-time updates
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
- **pytest** - Testing framework

## License

MIT