# Plan Implementacji AAC IoT Hub

## Status: Phase 1 Complete ✅ - Ready for Phase 2
**Data utworzenia**: 2026-04-26
**Ostatnia aktualizacja**: 2026-04-29
**Bazuje na**: ADR-000, ADR-001, ADR-002, ADR-003

## Przegląd

Implementacja MVP dla AAC IoT Hub - lokalny hub do kontroli urządzeń Yeelight przez REST API w kontenerze Docker.

### Główne cele MVP:
1. ✅ Discovery urządzeń Yeelight (SSDP)
2. ✅ REST API dla kontroli urządzeń
3. ✅ Ujednolicone API z abstrakcją (przygotowane na przyszłe typy urządzeń)
4. ✅ Docker deployment z host network mode
5. ✅ Dokumentacja API (Swagger)

## Fazy implementacji

### Faza 1: Setup projektu (1 dzień) ✅ UKOŃCZONA
**Cel**: Przygotować strukturę projektu, Docker, podstawowe zależności
**Status**: Ukończona 2026-04-29

#### Tasklist:
- [x] Struktura katalogów zgodna z ADR-003
- [x] `requirements.txt` z podstawowymi dependencies
- [x] `Dockerfile` (multi-stage build)
- [x] `docker-compose.yml` (host network mode)
- [x] `.dockerignore`
- [x] Basic `README.md` z instrukcjami
- [x] `app/config.py` - Configuration with pydantic-settings
- [x] `app/main.py` - Minimal FastAPI app with `/` and `/api/health`

#### Deliverables:
```
aac-iot-hub/
├── app/
│   ├── __init__.py
│   ├── main.py           # Minimal FastAPI app
│   ├── config.py         # Configuration (pydantic-settings)
│   ├── schemas/          # Pydantic schemas (not models/ - FastAPI convention)
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── api/
│       ├── __init__.py
│       └── v1/
│           └── __init__.py
├── tests/
│   └── __init__.py
├── docs/
│   ├── adr/  (ADRs created)
│   ├── future-devices.md  (research document)
│   ├── IMPLEMENTATION_PLAN.md
│   └── STATUS.md  (current progress)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .dockerignore
├── .gitignore
└── README.md
```

**requirements.txt**:
```txt
# Web framework
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.6.0
pydantic-settings>=2.2.0

# Device libraries
yeelight>=0.7.14

# Development
pytest>=8.1.0
httpx>=0.27.0  # dla testów FastAPI
black>=24.3.0
ruff>=0.3.0
```

**Weryfikacja**:
```bash
docker compose build
docker compose up
curl http://localhost:8765/docs  # Powinno pokazać Swagger UI
```

**Note:** Use `docker compose` (V2 plugin). For older standalone version, use `docker-compose`.

---

### Faza 2: Modele danych (1 dzień)
**Cel**: Zdefiniować Pydantic models dla urządzeń, capabilities, requests/responses
**Zasada**: YAGNI - start z on/off, potem dodawać kolejne features

#### Tasklist:
- [ ] `app/schemas/device.py` - Device base model (start: tylko power on/off)
- [ ] `app/schemas/requests.py` - Uniwersalny DeviceControlRequest
- [ ] `app/schemas/responses.py` - Response models (standardowy format)

**Note**: FastAPI generuje OpenAPI spec → klient Python można wygenerować automatycznie (działa Python 3.7+)

**IMPORTANT API Design Change (2026-05-02)**:
- ❌ **STARE**: Wiele osobnych endpointów (`POST /power`, `PUT /brightness`, `PUT /color`, etc.)
- ✅ **NOWE**: JEDEN uniwersalny endpoint `PUT /devices/{id}/control` + `DeviceControlRequest`
- **Dlaczego**: Prostszy dla klienta, mniej boilerplate, łatwiej dodać nowe capabilities
- **Przykład**: `PUT /devices/123/control` + `{"properties": {"power": "on", "brightness": 80}}`

#### Deliverables:

**`app/schemas/device.py`** (YAGNI - start tylko z on/off):
```python
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class DeviceStatus(BaseModel):
    """Start: only power on/off. Add more fields later (brightness, rgb, color_temp)."""
    power: str  # "on" | "off"
    online: bool = True
    last_seen: datetime

class Device(BaseModel):
    """Main device model."""
    id: str
    name: str
    type: str  # "yeelight" (more later: "shelly", etc.)
    model: str
    ip: str
    capabilities: List[str]  # Simple list: ["power"] initially, later: ["power", "brightness", "rgb"]
    status: DeviceStatus
    firmware: Optional[str] = None

class DeviceCapabilities(BaseModel):
    """
    Detailed capabilities info for GUI client.
    Returned by GET /devices/{id}/capabilities endpoint.

    Client uses this to render appropriate widgets:
    - "power" -> toggle button
    - "brightness" -> slider (min/max from metadata)
    - "rgb" -> color picker
    """
    device_id: str
    type: str
    model: str
    capabilities: Dict[str, Any]  # Nested structure with widget info, min/max, current values
    metadata: Dict[str, Any]  # firmware, online status, etc.
```

**`app/schemas/requests.py`** (Jeden uniwersalny endpoint):
```python
from pydantic import BaseModel
from typing import Dict, Any

class DeviceControlRequest(BaseModel):
    """
    Universal control request for all device capabilities.

    Client sends any capability changes in a single request.
    Examples:
    - {"power": "on"}
    - {"power": "on", "brightness": 80}
    - {"rgb": [255, 0, 0], "brightness": 100}

    Validation happens in adapter based on device capabilities.
    """
    properties: Dict[str, Any]  # Capability name -> value pairs

# Example valid requests:
# PUT /devices/{id}/control
# {"properties": {"power": "on"}}
# {"properties": {"power": "on", "brightness": 80}}
# {"properties": {"rgb": [255, 0, 0]}}
```

**`app/schemas/responses.py`**:
```python
from pydantic import BaseModel
from typing import Any, Optional

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
```

**Testy**:
```python
# tests/test_models.py
def test_device_model():
    device = Device(
        id="test_123",
        type="yeelight",
        # ...
    )
    assert device.type == "yeelight"
```

---

### Faza 3: Device Abstraction Layer (2 dni)
**Cel**: Implementować abstrakcję urządzeń - DeviceAdapter interface + YeelightAdapter

#### Tasklist:
- [ ] `app/services/device_adapter.py` - Abstract base class
- [ ] `app/services/yeelight_adapter.py` - Implementacja dla Yeelight
- [ ] `app/services/device_registry.py` - Registry dla zarządzania urządzeniami
- [ ] Testy jednostkowe dla adapterów

#### Deliverables:

**`app/services/device_adapter.py`**:
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.device import Device, DeviceCapabilities
from app.models.requests import PowerRequest, BrightnessRequest, ColorRGBRequest

class DeviceAdapter(ABC):
    """Abstrakcja dla wszystkich typów urządzeń"""

    def __init__(self, device_id: str, ip: str, model: str):
        self.device_id = device_id
        self.ip = ip
        self.model = model
        self.type = self._get_type()

    @abstractmethod
    def _get_type(self) -> str:
        """Zwraca typ urządzenia (yeelight, shelly, etc.)"""
        pass

    @abstractmethod
    async def get_status(self) -> Device:
        """Pobiera aktualny status urządzenia"""
        pass

    @abstractmethod
    async def get_capabilities(self) -> DeviceCapabilities:
        """Zwraca capabilities urządzenia"""
        pass

    # Standard operations - MUST implement
    @abstractmethod
    async def set_power(self, state: str) -> bool:
        """on | off | toggle"""
        pass

    @abstractmethod
    async def set_brightness(self, value: int) -> bool:
        """0-100"""
        pass

    @abstractmethod
    async def set_color_rgb(self, rgb: tuple[int, int, int]) -> bool:
        """RGB color"""
        pass

    @abstractmethod
    async def set_color_temp(self, kelvin: int) -> bool:
        """Color temperature in Kelvin"""
        pass

    # Device-specific operations - optional
    async def execute_effect(self, name: str, params: dict) -> bool:
        """Optional: effects support"""
        raise NotImplementedError(
            f"{self.type} doesn't support effects"
        )

    async def start_flow(self, flow_data: dict) -> bool:
        """Optional: flow support"""
        raise NotImplementedError(
            f"{self.type} doesn't support flows"
        )

    # Utility methods
    async def is_online(self) -> bool:
        """Check if device is reachable"""
        try:
            await self.get_status()
            return True
        except Exception:
            return False
```

**`app/services/yeelight_adapter.py`**:
```python
from yeelight import Bulb, BulbException
from app.services.device_adapter import DeviceAdapter
from app.models.device import Device, DeviceStatus, DeviceCapabilities
from datetime import datetime
import asyncio

class YeelightAdapter(DeviceAdapter):
    """Adapter dla urządzeń Yeelight"""

    def __init__(self, device_id: str, ip: str, model: str):
        super().__init__(device_id, ip, model)
        self.bulb = Bulb(ip, auto_on=True)

    def _get_type(self) -> str:
        return "yeelight"

    async def get_status(self) -> Device:
        """Pobiera status z Yeelight"""
        props = await self._run_in_executor(self.bulb.get_properties)

        status = DeviceStatus(
            power=props.get("power", "off"),
            brightness=int(props.get("bright", 0)),
            rgb=self._parse_rgb(props.get("rgb")),
            color_temp=int(props.get("ct", 0)),
            online=True,
            last_seen=datetime.now()
        )

        return Device(
            id=self.device_id,
            name=f"Yeelight {self.model}",
            type=self.type,
            model=self.model,
            ip=self.ip,
            capabilities=self._get_capabilities_list(),
            status=status,
            firmware=props.get("fw_ver")
        )

    async def get_capabilities(self) -> DeviceCapabilities:
        """Zwraca szczegółowe capabilities"""
        status = await self.get_status()

        return DeviceCapabilities(
            device_id=self.device_id,
            type=self.type,
            model=self.model,
            capabilities={
                "standard": {
                    "power": {
                        "available": True,
                        "states": ["on", "off", "toggle"],
                        "current": status.status.power
                    },
                    "brightness": {
                        "available": True,
                        "type": "integer",
                        "min": 1,
                        "max": 100,
                        "current": status.status.brightness,
                        "unit": "%"
                    },
                    "color": {
                        "available": True,
                        "modes": ["rgb", "temperature"],
                        "rgb": {
                            "type": "array",
                            "current": status.status.rgb
                        },
                        "temperature": {
                            "type": "integer",
                            "min": 1700,
                            "max": 6500,
                            "current": status.status.color_temp,
                            "unit": "K"
                        }
                    }
                },
                "device_specific": {
                    "effects": {
                        "available": True,
                        "supported": [
                            {"name": "disco", "description": "Disco effect"},
                            {"name": "pulse", "description": "Pulsing effect"},
                            {"name": "strobe", "description": "Strobe effect"}
                        ]
                    }
                }
            },
            metadata={
                "firmware": status.firmware,
                "online": True,
                "last_seen": status.status.last_seen.isoformat()
            }
        )

    async def set_power(self, state: str) -> bool:
        if state == "toggle":
            await self._run_in_executor(self.bulb.toggle)
        elif state == "on":
            await self._run_in_executor(self.bulb.turn_on)
        elif state == "off":
            await self._run_in_executor(self.bulb.turn_off)
        return True

    async def set_brightness(self, value: int) -> bool:
        await self._run_in_executor(self.bulb.set_brightness, value)
        return True

    async def set_color_rgb(self, rgb: tuple[int, int, int]) -> bool:
        await self._run_in_executor(self.bulb.set_rgb, *rgb)
        return True

    async def set_color_temp(self, kelvin: int) -> bool:
        await self._run_in_executor(self.bulb.set_color_temp, kelvin)
        return True

    async def execute_effect(self, name: str, params: dict) -> bool:
        # Map effect names to yeelight methods
        effects = {
            "disco": self.bulb.start_flow,
            "pulse": self.bulb.start_flow,
            "strobe": self.bulb.start_flow
        }

        if name not in effects:
            raise ValueError(f"Unknown effect: {name}")

        # Execute effect (simplified - real implementation needs flow specs)
        await self._run_in_executor(effects[name], self._get_flow_spec(name))
        return True

    # Helper methods
    async def _run_in_executor(self, func, *args):
        """Run sync yeelight methods in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args)

    def _parse_rgb(self, rgb_int: Optional[int]) -> Optional[tuple[int, int, int]]:
        if rgb_int is None:
            return None
        r = (rgb_int >> 16) & 0xFF
        g = (rgb_int >> 8) & 0xFF
        b = rgb_int & 0xFF
        return (r, g, b)

    def _get_capabilities_list(self) -> List[str]:
        return ["power", "brightness", "color", "color_temp", "effects"]

    def _get_flow_spec(self, effect_name: str):
        # Simplified - real implementation needs proper flow specs
        # Based on yeelight documentation
        return None  # TODO: implement proper flows
```

**`app/services/device_registry.py`**:
```python
from typing import Dict, List, Optional
from app.services.device_adapter import DeviceAdapter
from app.models.device import Device

class DeviceRegistry:
    """Central registry for all discovered devices"""

    def __init__(self):
        self._devices: Dict[str, DeviceAdapter] = {}

    def register(self, adapter: DeviceAdapter):
        """Register a device adapter"""
        self._devices[adapter.device_id] = adapter

    def unregister(self, device_id: str):
        """Remove device from registry"""
        if device_id in self._devices:
            del self._devices[device_id]

    def get(self, device_id: str) -> Optional[DeviceAdapter]:
        """Get device adapter by ID"""
        return self._devices.get(device_id)

    def get_all(self) -> List[DeviceAdapter]:
        """Get all registered devices"""
        return list(self._devices.values())

    async def get_all_status(self) -> List[Device]:
        """Get status of all devices"""
        statuses = []
        for adapter in self._devices.values():
            try:
                status = await adapter.get_status()
                statuses.append(status)
            except Exception as e:
                # Log error but continue
                print(f"Error getting status for {adapter.device_id}: {e}")
        return statuses

    def clear(self):
        """Clear all devices"""
        self._devices.clear()

# Global registry instance
device_registry = DeviceRegistry()
```

---

### Faza 4: Discovery Service (1 dzień)
**Cel**: Implementować SSDP discovery dla Yeelight

#### Tasklist:
- [ ] `app/services/discovery.py` - Discovery service
- [ ] Integracja z yeelight library
- [ ] Testy discovery

#### Deliverables:

**`app/services/discovery.py`**:
```python
from yeelight import discover_bulbs
from app.services.device_registry import device_registry
from app.services.yeelight_adapter import YeelightAdapter
from typing import List
import asyncio

class DiscoveryService:
    """Service for discovering IoT devices"""

    async def discover_all(self) -> List[str]:
        """
        Discover all devices and register them.
        Returns list of discovered device IDs.
        """
        discovered_ids = []

        # Discover Yeelight devices
        yeelight_ids = await self._discover_yeelight()
        discovered_ids.extend(yeelight_ids)

        # Future: discover Shelly, etc.

        return discovered_ids

    async def _discover_yeelight(self) -> List[str]:
        """Discover Yeelight devices using SSDP"""
        loop = asyncio.get_event_loop()

        # Run discovery in thread pool (yeelight lib is sync)
        bulbs = await loop.run_in_executor(None, discover_bulbs, 5)  # 5s timeout

        discovered_ids = []

        for bulb_info in bulbs:
            device_id = f"yeelight_{bulb_info['capabilities']['id']}"
            ip = bulb_info['ip']
            model = bulb_info['capabilities']['model']

            # Create adapter
            adapter = YeelightAdapter(
                device_id=device_id,
                ip=ip,
                model=model
            )

            # Register in global registry
            device_registry.register(adapter)
            discovered_ids.append(device_id)

        return discovered_ids

# Global discovery service instance
discovery_service = DiscoveryService()
```

---

### Faza 5: REST API Endpoints (2 dni)
**Cel**: Implementować wszystkie endpointy zgodnie z ADR-003

#### Tasklist:
- [ ] `app/api/v1/devices.py` - Device endpoints
- [ ] `app/api/v1/health.py` - Health endpoints
- [ ] `app/main.py` - FastAPI app z routing
- [ ] Exception handlers
- [ ] CORS configuration
- [ ] Testy API

#### Deliverables:

**`app/api/v1/devices.py`**:
```python
from fastapi import APIRouter, HTTPException
from typing import List
from app.models.device import Device, DeviceCapabilities
from app.models.requests import (
    PowerRequest,
    BrightnessRequest,
    ColorRGBRequest,
    ColorTempRequest,
    EffectRequest
)
from app.models.responses import SuccessResponse, ErrorResponse, ErrorDetail
from app.services.device_registry import device_registry
from app.services.discovery import discovery_service

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])

@router.get("", response_model=dict)
async def list_devices():
    """List all discovered devices"""
    devices = await device_registry.get_all_status()
    return {
        "devices": devices,
        "count": len(devices),
        "last_discovery": None  # TODO: track last discovery time
    }

@router.post("/discover", response_model=dict)
async def discover_devices():
    """Trigger device discovery"""
    discovered_ids = await discovery_service.discover_all()
    devices = await device_registry.get_all_status()

    return {
        "discovered": len(discovered_ids),
        "devices": devices
    }

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: str):
    """Get specific device details"""
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    return await adapter.get_status()

@router.get("/{device_id}/capabilities", response_model=DeviceCapabilities)
async def get_capabilities(device_id: str):
    """Get device capabilities"""
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    return await adapter.get_capabilities()

@router.post("/{device_id}/power", response_model=SuccessResponse)
async def set_power(device_id: str, request: PowerRequest):
    """Set device power state"""
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    await adapter.set_power(request.state)
    return SuccessResponse(data={"state": request.state})

@router.put("/{device_id}/brightness", response_model=SuccessResponse)
async def set_brightness(device_id: str, request: BrightnessRequest):
    """Set device brightness"""
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    await adapter.set_brightness(request.value)
    return SuccessResponse(data={"brightness": request.value})

@router.put("/{device_id}/color", response_model=SuccessResponse)
async def set_color(device_id: str, request: ColorRGBRequest):
    """Set device color (RGB)"""
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    await adapter.set_color_rgb(request.rgb)
    return SuccessResponse(data={"rgb": request.rgb})

@router.put("/{device_id}/color_temp", response_model=SuccessResponse)
async def set_color_temp(device_id: str, request: ColorTempRequest):
    """Set color temperature"""
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    await adapter.set_color_temp(request.value)
    return SuccessResponse(data={"temperature": request.value})

@router.post("/{device_id}/effect", response_model=SuccessResponse)
async def execute_effect(device_id: str, request: EffectRequest):
    """Execute device-specific effect"""
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

    # Check if device supports effects
    caps = await adapter.get_capabilities()
    if "effects" not in caps.capabilities.get("device_specific", {}):
        raise HTTPException(
            status_code=400,
            detail=f"Device {adapter.type} doesn't support effects"
        )

    await adapter.execute_effect(request.name, request.params)
    return SuccessResponse(data={"effect": request.name})
```

**`app/api/v1/health.py`**:
```python
from fastapi import APIRouter
from datetime import datetime
import time

router = APIRouter(tags=["health"])

start_time = time.time()

@router.get("/api/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/api/v1/status")
async def get_status():
    """Detailed status"""
    from app.services.device_registry import device_registry

    devices = device_registry.get_all()
    online_count = sum(1 for d in devices if asyncio.iscoroutinefunction(d.is_online) and await d.is_online())

    return {
        "devices_online": online_count,
        "devices_total": len(devices),
        "uptime_seconds": int(time.time() - start_time),
        "timestamp": datetime.now().isoformat()
    }
```

**`app/main.py`**:
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import devices, health
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AAC IoT Hub",
    description="Local IoT device control hub - REST API for Yeelight and more",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": str(exc) if app.debug else None
            }
        }
    )

# Include routers
app.include_router(devices.router)
app.include_router(health.router)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("AAC IoT Hub starting up...")
    # TODO: Auto-discovery on startup?

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("AAC IoT Hub shutting down...")
    from app.services.device_registry import device_registry
    device_registry.clear()

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "AAC IoT Hub",
        "version": "0.1.0",
        "docs": "/docs",
        "api": "/api/v1/devices"
    }
```

---

### Faza 6: Docker & Deployment (1 dzień)
**Cel**: Finalizacja Docker setup, testy deployment

#### Tasklist:
- [ ] Finalizacja Dockerfile
- [ ] Finalizacja docker-compose.yml
- [ ] `.dockerignore`
- [ ] Health check w Docker
- [ ] Testy deployment

#### Deliverables:

**`Dockerfile`**:
```dockerfile
# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application
COPY ./app ./app

# Non-root user for security
RUN useradd -m -u 1000 aac && \
    chown -R aac:aac /app
USER aac

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Expose port (documentational - host mode ignores this)
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8765/api/health')"

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8765", "--log-level", "info"]
```

**`docker-compose.yml`**:
```yaml
version: '3.8'

services:
  aac-iot-hub:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: aac-iot-hub
    network_mode: host  # Required for SSDP discovery
    restart: unless-stopped
    environment:
      - LOG_LEVEL=${LOG_LEVEL:-info}
      - API_PORT=${API_PORT:-8765}
    volumes:
      - ./logs:/app/logs  # Optional: for persistent logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8765/api/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 10s
```

**`.dockerignore`**:
```
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
.venv
.env
.git
.gitignore
.dockerignore
Dockerfile
docker-compose.yml
README.md
docs/
tests/
*.md
.pytest_cache
.coverage
htmlcov/
```

---

### Faza 7: Testy & Dokumentacja (2 dni)
**Cel**: Testy integracyjne, dokumentacja użytkownika

#### Tasklist:
- [ ] Testy integracyjne API (pytest)
- [ ] README.md z instrukcjami użytkownika
- [ ] CONTRIBUTING.md
- [ ] Przykłady użycia API (curl, Python client)

#### Deliverables:

**`tests/test_api.py`**:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_list_devices():
    response = client.get("/api/v1/devices")
    assert response.status_code == 200
    assert "devices" in response.json()

# TODO: More integration tests
```

**`README.md`** (aktualizacja):
```markdown
# AAC IoT Hub

Local IoT device control hub - REST API for Yeelight (and more in the future).

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Yeelight bulbs in LAN Control mode

### Run with Docker

```bash
docker compose up -d
```

API will be available at `http://localhost:8765`

### API Documentation

Interactive docs: `http://localhost:8765/docs`

### Usage Examples

**Discover devices:**
```bash
curl -X POST http://localhost:8765/api/v1/devices/discover
```

**List devices:**
```bash
curl http://localhost:8765/api/v1/devices
```

**Toggle power:**
```bash
curl -X POST http://localhost:8765/api/v1/devices/yeelight_123/power \
  -H "Content-Type: application/json" \
  -d '{"state": "toggle"}'
```

**Set brightness:**
```bash
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/brightness \
  -H "Content-Type: application/json" \
  -d '{"value": 80}'
```

**Set color:**
```bash
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/color \
  -H "Content-Type: application/json" \
  -d '{"rgb": [255, 0, 0]}'
```

## Architecture

See [docs/adr/](docs/adr/) for Architecture Decision Records.

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8765

# Run tests
pytest
```

## License

MIT
```

---

## Podsumowanie Timeline

| Faza | Czas | Deliverable |
|------|------|------------|
| 1. Setup projektu | 1 dzień | Struktura + Docker + FastAPI hello world |
| 2. Modele danych | 1 dzień | Pydantic models gotowe |
| 3. Device Abstraction | 2 dni | YeelightAdapter + DeviceRegistry |
| 4. Discovery Service | 1 dzień | SSDP discovery działające |
| 5. REST API | 2 dni | Wszystkie endpointy zaimplementowane |
| 6. Docker & Deployment | 1 dzień | Production-ready container |
| 7. Testy & Docs | 2 dni | Testy + dokumentacja |

**Total: 10 dni roboczych (~2 tygodnie)**

## Verification Checklist

Po każdej fazie:

### Faza 1:
- [x] `docker compose up` działa ✅
- [x] Swagger UI dostępne na http://localhost:8765/docs ✅
- [x] `/api/health` zwraca 200 ✅
- [x] Manual tests completed (2026-04-29) ✅

### Faza 2:
- [ ] Wszystkie modele mają testy
- [ ] Pydantic validation działa

### Faza 3:
- [ ] YeelightAdapter łączy się z żarówką
- [ ] DeviceRegistry przechowuje urządzenia
- [ ] Testy jednostkowe przechodzą

### Faza 4:
- [ ] Discovery znajduje żarówki Yeelight
- [ ] Żarówki są rejestrowane w registry

### Faza 5:
- [ ] Wszystkie endpointy działają
- [ ] Swagger docs pokazują wszystkie endpointy
- [ ] Error handling działa poprawnie

### Faza 6:
- [ ] Docker image buduje się
- [ ] Host network mode działa
- [ ] Discovery działa z kontenera

### Faza 7:
- [ ] Testy integracyjne przechodzą
- [ ] README jest kompletne
- [ ] Przykłady działają

## Next Steps (Post-MVP)

1. Persistence (SQLite) dla discovered devices
2. WebSocket endpoint dla real-time updates
3. Web UI (opcjonalnie)
4. Support dla Shelly (jeśli discovery zostanie naprawiony)
5. Docker Hub publication
6. CI/CD pipeline

## Questions & Decisions Needed

1. **Auto-discovery on startup?** - Czy discovery automatyczne przy starcie kontenera?
2. **Persistence?** - Czy zapisywać discovered devices do DB?
3. **Authentication?** - Czy MVP potrzebuje auth? (prawdopodobnie nie - local network only)
4. **Rate limiting?** - Czy potrzebne dla MVP?

**Rekomendacja**: Najpierw MVP bez tych features, dodać później jeśli potrzebne.