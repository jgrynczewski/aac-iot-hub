# Changelog

All notable changes to AAC IoT Hub project.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] - 2026-05-09 - MVP v1.0 Complete ✅

### Added
- **Complete REST API** for IoT device control
  - `GET /api/health` - Health check endpoint
  - `GET /api/v1/status` - Detailed status endpoint
  - `GET /api/v1/devices` - List all discovered devices
  - `POST /api/v1/devices/discover` - Trigger SSDP discovery
  - `GET /api/v1/devices/{id}` - Get specific device details
  - `GET /api/v1/devices/{id}/capabilities` - Get device capabilities
  - `PUT /api/v1/devices/{id}/control` - Universal control endpoint
  - `GET /favicon.ico` - Favicon endpoint (suppress 404 warnings)

- **Device Support**
  - Yeelight smart bulbs (WiFi RGB/tunable white)
  - SSDP discovery protocol
  - Power control (on/off/toggle)

- **Architecture**
  - Device abstraction layer (adapter pattern)
  - Global device registry (in-memory)
  - FastAPI framework with Pydantic validation
  - Docker containerization (multi-stage build)
  - Host network mode for SSDP multicast

- **Testing**
  - 39 integration tests (all passing)
  - `tests/test_health.py` - 4 tests
  - `tests/test_devices.py` - 15 tests
  - `tests/test_device_adapter.py` - 12 tests
  - `tests/test_discovery.py` - 8 tests
  - pytest configuration with asyncio support
  - Mock-based testing (no hardware required)

- **Documentation**
  - README.md - Quick start guide
  - docs/STATUS.md - Implementation status (100%)
  - docs/API_EXAMPLES.md - Complete curl examples
  - docs/GUI_REQUIREMENTS.md - GUI project specification
  - docs/IMPLEMENTATION_PLAN.md - Original 7-phase plan
  - docs/MANUAL_TESTING.md - Manual test procedures
  - docs/INDEX.md - Documentation navigation
  - NEXT_STEPS.md - Development roadmap for v2.0
  - 4x Architecture Decision Records (ADR)

- **Configuration**
  - Environment variables via pydantic-settings
  - `AAC_API_PORT` - API port (default: 8765)
  - `AAC_LOG_LEVEL` - Logging level (default: info)
  - `AAC_API_HOST` - API host (default: 0.0.0.0)
  - `AAC_DISCOVERY_TIMEOUT` - Discovery timeout (default: 5s)

### Fixed
- Logging configuration now respects `AAC_LOG_LEVEL` environment variable
- Added favicon endpoint to suppress browser 404 warnings

### Manual Testing
- ✅ Tested with real Yeelight devices
- ✅ SSDP discovery verified working
- ✅ Power control (on/off/toggle) verified
- ✅ All API endpoints tested
- ✅ Error handling verified

### Dependencies
- Python 3.12
- FastAPI 0.110.0+
- Uvicorn 0.29.0+
- Pydantic 2.6.0+
- pydantic-settings 2.2.0+
- yeelight 0.7.14+
- pytest 8.1.0+
- pytest-asyncio 0.23.0+
- httpx 0.27.0+

---

## [Unreleased] - MVP v2.0 Roadmap

### Planned Features

#### Priority 1: Extended Control
- [ ] Brightness control (1-100)
- [ ] RGB color control
- [ ] Color temperature control (1700-6500K)
- [ ] 8 preset colors (white, yellow, red, green, blue, purple, orange, pink)
- [ ] 3 color temperature presets (warm, neutral, cool)

#### Priority 2: Animations
- [ ] Flow animations system
- [ ] Police effect (blue-red flashing)
- [ ] Rainbow effect (color cycle)
- [ ] Disco effect (random colors)
- [ ] Strobe effect (white flash)
- [ ] Candle effect (flicker simulation)
- [ ] Romantic effect (warm transitions)
- [ ] Magic effect (slow color mix)

#### Priority 3: Scenes & Presets
- [ ] Reading scene (bright, neutral)
- [ ] Movie scene (dim, warm)
- [ ] Night scene (very dim, red)
- [ ] Work scene (bright, cool)
- [ ] Dinner scene (medium, warm)
- [ ] Favorites system (3 slots)
- [ ] Save/restore custom settings

#### Future Enhancements
- [ ] Persistence layer (SQLite)
- [ ] WebSocket support for real-time updates
- [ ] Multi-device control
- [ ] Room/group management
- [ ] Scheduled scenes (timer, sunrise/sunset)
- [ ] Additional device types (Shelly, etc.)

---

## Version History Summary

| Version | Date | Status | Description |
|---------|------|--------|-------------|
| 1.0.0 | 2026-05-09 | ✅ Released | MVP v1.0 - Power control only |
| 2.0.0 | TBD | 🔄 Planned | Full color/brightness control + animations |

---

## Development Timeline

**Phase 1: Project Setup** (2026-04-29)
- Initial project structure
- Docker setup
- FastAPI hello-world

**Phase 2: Data Models** (2026-05-02)
- Pydantic schemas
- Device, DeviceStatus, DeviceCapabilities

**Phase 3: Device Abstraction** (2026-05-02)
- Abstract DeviceAdapter class
- YeelightAdapter implementation
- Device registry

**Phase 4: Discovery Service** (2026-05-02)
- SSDP discovery for Yeelight
- Automatic device registration

**Phase 5: REST API Endpoints** (2026-05-03)
- All API endpoints implemented
- Error handling
- Logging

**Phase 6: Docker & Manual Testing** (2026-05-09)
- Final Docker configuration
- Manual testing with real devices
- Bug fixes (logging, favicon)

**Phase 7: Integration Tests** (2026-05-09)
- 39 integration tests implemented
- All tests passing
- Documentation updated

**Total Development Time:** ~10 days

---

## Breaking Changes

### v1.0.0
- Initial release - no breaking changes

### Future v2.0.0 (planned)
- No breaking changes planned
- All new features will extend existing `/control` endpoint
- Backward compatible with v1.0 API

---

## Migration Guide

### From Nothing to v1.0.0

1. Install Docker & Docker Compose
2. Clone repository
3. Enable "LAN Control" in Yeelight app
4. Run `docker compose up -d`
5. Test with `curl http://localhost:8765/api/health`

See README.md for detailed setup.

### From v1.0.0 to v2.0.0 (future)

No migration needed - v2.0 will be backward compatible.
New capabilities will be added to existing endpoints.

---

## Known Issues

### v1.0.0
- None - all known issues resolved

### Limitations
- In-memory storage only (devices lost on restart)
- Single device type support (Yeelight only)
- Power control only (no brightness/color yet)
- No persistence for favorites/settings

These limitations are by design for MVP v1.0 and will be addressed in v2.0.

---

## Contributors

- AAC IoT Hub Team (2026)

---

## References

- [Yeelight Python Library](https://yeelight.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)

---

**Last Updated:** 2026-05-09
