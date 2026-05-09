# ADR 003: HTTP API Protocol

## Status
Proposed

## Kontekst
Serwis AAC IoT Hub wymaga API do komunikacji synchronicznej z klientami. API musi obsługiwać:
- Discovery urządzeń (lista wszystkich znalezionych urządzeń Yeelight)
- Kontrolę poszczególnych urządzeń (on/off, kolor, jasność, efekty specjalne)
- Różnorodne funkcje urządzeń (od prostych toggle do zaawansowanych jak sync z muzyką)
- Prostą integrację z różnymi klientami (CLI, web UI, automacje)

## Rozważane opcje

### Opcja 1: REST API (ZALECANA)
**Charakterystyka:**
- Architektura oparta na zasobach (resources)
- Standardowe metody HTTP: GET, POST, PUT, PATCH, DELETE
- Stateless communication
- JSON jako format wymiany danych

**Przykładowa struktura:**
```
GET    /api/v1/devices              - Lista wszystkich urządzeń
GET    /api/v1/devices/discover     - Trigger discovery
GET    /api/v1/devices/{id}         - Szczegóły urządzenia
POST   /api/v1/devices/{id}/toggle  - Toggle on/off
PUT    /api/v1/devices/{id}/color   - Ustaw kolor
PUT    /api/v1/devices/{id}/brightness - Ustaw jasność
POST   /api/v1/devices/{id}/effect  - Aktywuj efekt (muzyka, fade, etc.)
```

**Zalety:**
- ✅ Najpopularniejszy standard (95%+ API w internecie)
- ✅ Intuicyjny i przewidywalny (resource-based)
- ✅ Doskonała obsługa cache (HTTP headers)
- ✅ Wbudowane w przeglądarki (można testować bezpośrednio)
- ✅ Ogromna liczba bibliotek klienckich (curl, requests, axios, fetch)
- ✅ Świetne narzędzia (Postman, Insomnia, Swagger/OpenAPI)
- ✅ Framework FastAPI ma automatyczną dokumentację OpenAPI
- ✅ Stateless = łatwe skalowanie (przyszłość)

**Wady:**
- ⚠️ Więcej verbosity niż RPC (czasem kilka requestów)
- ⚠️ Over-fetching lub under-fetching danych
- ⚠️ Brak standardu dla partial updates (różne podejścia)

**Framework: FastAPI**
- Nowoczesny, szybki (async)
- Automatyczna walidacja (Pydantic)
- Auto-generated OpenAPI docs (Swagger UI)
- Type hints = mniej bugów
- Doskonała dokumentacja

### Opcja 2: JSON-RPC 2.0
**Charakterystyka:**
- Protocol agnostic (HTTP jako transport)
- Wywołania procedur zdalnych (methods)
- Single endpoint `/rpc`
- JSON request/response

**Przykładowa struktura:**
```json
POST /rpc
{
  "jsonrpc": "2.0",
  "method": "devices.discover",
  "params": {},
  "id": 1
}

{
  "jsonrpc": "2.0",
  "method": "device.setColor",
  "params": {"device_id": "abc123", "rgb": [255, 0, 0]},
  "id": 2
}
```

**Zalety:**
- ✅ Prostsza struktura (tylko POST na jeden endpoint)
- ✅ Mniejszy payload niż REST
- ✅ Batch requests (wiele wywołań w jednym request)
- ✅ Jasna semantyka (method call)
- ✅ Dobra dla action-oriented API (nasze use case!)

**Wady:**
- ❌ Mniejsza popularność = mniej narzędzi
- ❌ Brak wykorzystania HTTP semantyki (wszystko POST)
- ❌ Trudniejsze cache'owanie
- ❌ Brak standardowej dokumentacji (nie ma odpowiednika OpenAPI)
- ❌ Mniej intuicyjny dla developerów przyzwyczajonych do REST
- ❌ Gorsza obsługa w przeglądarkach (nie można GET w URL bar)

**Framework:** Flask-JSONRPC lub custom FastAPI handler

### Opcja 3: GraphQL
**Charakterystyka:**
- Query language dla API
- Single endpoint `/graphql`
- Klient definiuje strukturę odpowiedzi
- Silnie typowany schema

**Przykładowa struktura:**
```graphql
query {
  devices {
    id
    name
    status
    capabilities
  }
}

mutation {
  toggleDevice(id: "abc123") {
    status
  }
}
```

**Zalety:**
- ✅ Klient dostaje dokładnie to czego potrzebuje (no over-fetching)
- ✅ Silne typowanie (schema)
- ✅ Introspection (self-documenting)
- ✅ Świetne dla złożonych zapytań z relacjami

**Wady:**
- ❌ **Overengineering dla prostego IoT API**
- ❌ Stroma krzywa uczenia (nowy język)
- ❌ Dodatkowa złożoność (resolver functions)
- ❌ Trudniejsze cache'owanie
- ❌ Problemy z rate limiting (wszystko jeden endpoint)
- ❌ Backend musi implementować cały resolver graph
- ❌ Nie ma sensu dla action-based API (toggle, set color)

**Framework:** Strawberry, Ariadne, Graphene

### Opcja 4: gRPC
**Charakterystyka:**
- Binary protocol (Protocol Buffers)
- HTTP/2 based
- Silnie typowany (protobuf schema)
- Bi-directional streaming

**Zalety:**
- ✅ Bardzo szybki (binary serialization)
- ✅ Małe payloady
- ✅ Silne typowanie
- ✅ Code generation dla klientów
- ✅ Streaming (przydatne dla real-time events)

**Wady:**
- ❌ Nie działa w przeglądarkach (wymaga gRPC-Web proxy)
- ❌ Binary = trudne debugowanie (nie można curl)
- ❌ Stroma krzywa uczenia (protobuf)
- ❌ **Overkill dla synchronicznego API**
- ❌ Słabe wsparcie dla starszych systemów
- ❌ Wymaga większego setup (protoc compiler)

**Framework:** grpcio

### Opcja 5: WebSocket
**Charakterystyka:**
- Full-duplex communication
- Persistent connection
- Real-time bi-directional

**Zalety:**
- ✅ Real-time updates
- ✅ Push notifications z serwera
- ✅ Niska latencja

**Wady:**
- ❌ **Nie spełnia wymagania "synchroniczna komunikacja"**
- ❌ Wymaga zarządzania połączeniami (connection pooling)
- ❌ Trudniejsze skalowanie (stateful)
- ❌ Overkill jeśli nie potrzeba real-time push
- ❌ Problemy z load balancing
- ❌ Większa złożoność klienta

## Decyzja

**Wybrano: REST API (Opcja 1) z FastAPI**

## Uzasadnienie szczegółowe

### 1. Zgodność z wymaganiami:
✅ **Komunikacja synchroniczna**: REST = request-response, perfect match
✅ **Prostota**: Intuicyjne endpointy, łatwe do zrozumienia
✅ **Różnorodność funkcji**: Elastyczna struktura endpoint + JSON body
✅ **Standardizacja**: Developerzy znają REST out-of-the-box

### 2. Dlaczego NIE JSON-RPC:
Mimo że JSON-RPC jest świetny dla action-oriented API (nasze urządzenia to głównie akcje: toggle, setColor), **wady przeważają**:
- Brak tooling (OpenAPI/Swagger to killer feature)
- Gorsza developer experience (trudniej testować)
- Mniejsza społeczność = mniej przykładów i tutoriali
- REST jest wystarczająco dobry dla naszego use case

### 3. Dlaczego FastAPI:
- **Auto-generated docs**: `/docs` (Swagger UI), `/redoc` (ReDoc) - out of the box
- **Pydantic validation**: Type-safe request/response models
- **Async support**: Nieblokujące I/O (ważne dla discovery operations)
- **Modern Python**: Type hints, Python 3.12 compatible
- **Performance**: Comparable to Node.js/Go (Starlette + Uvicorn)
- **Lightweight**: Nie wymaga dużo dependencies (vs Django)

### 4. Praktyczne korzyści:
```python
# Automatyczna walidacja i dokumentacja
class ColorRequest(BaseModel):
    rgb: tuple[int, int, int]
    brightness: int = 100

@app.put("/api/v1/devices/{device_id}/color")
async def set_color(device_id: str, color: ColorRequest):
    # FastAPI auto-validates:
    # - rgb to tuple trzech intów
    # - brightness ma default 100
    # - device_id jest stringiem
    return await device_service.set_color(device_id, color.rgb, color.brightness)
```

### 5. Testing & Development:
```bash
# Testowanie z curl
curl -X POST http://localhost:8765/api/v1/devices/abc123/toggle

# Lub przegladarka
http://localhost:8765/docs  # Interactive Swagger UI

# Lub Postman, HTTPie, etc.
http POST localhost:8765/api/v1/devices/abc123/color rgb:='[255,0,0]'
```

## Struktura API

### Wersjonowanie:
`/api/v1/...` - pozwala na przyszłe zmiany bez breaking changes

### API Standardization & Device Abstraction

**Kluczowe wymaganie**: API musi być ujednolicone dla wszystkich typów urządzeń (Yeelight, przyszły Shelly, etc.).

#### Powód standardyzacji:

**Use case klienta**:
1. Klient wywołuje `GET /api/v1/devices` → otrzymuje listę wszystkich urządzeń
2. Dla każdego urządzenia klient widzi `type` (yeelight, shelly, etc.) i `capabilities`
3. Klient tworzy UI bazując na `capabilities` - przyciski, slidery, color pickers
4. Po wybraniu urządzenia klient wywołuje `GET /api/v1/devices/{id}/capabilities` dla szczegółów
5. Klient wywołuje standardowe endpointy: `/power`, `/brightness`, `/color`, etc.

**Standardowe operacje muszą mieć te same nazwy i semantykę** niezależnie od typu urządzenia.

#### Standard Operations (wspólne dla wszystkich urządzeń)

Operacje z jednolitą semantyką między typami urządzeń:

| Operacja | Endpoint | Body | Opis | Wszystkie typy |
|----------|----------|------|------|----------------|
| **power** | `POST /devices/{id}/power` | `{"state": "on"\|"off"\|"toggle"}` | Włącz/wyłącz urządzenie | ✅ Universal |
| **brightness** | `PUT /devices/{id}/brightness` | `{"value": 0-100}` | Ustaw jasność (%) | ✅ Lights only |
| **color** | `PUT /devices/{id}/color` | `{"rgb": [R,G,B]}` | Ustaw kolor RGB | ✅ Color lights |
| **color_temp** | `PUT /devices/{id}/color_temp` | `{"value": 1700-6500}` | Temperatura barwowa (K) | ✅ Tunable white |

#### Device-Specific Operations

Operacje unikalne dla konkretnych typów urządzeń:

**Yeelight-specific**:
- `POST /devices/{id}/effect` - Efekty specjalne (disco, pulse, music_sync)
- `POST /devices/{id}/flow` - Custom light flow sequences

**Shelly-specific (przyszłość)**:
- `POST /devices/{id}/timer` - Hardware timer
- `GET /devices/{id}/energy` - Energy consumption stats

#### Capabilities Endpoint - Szczegóły

**Główny endpoint dla klienta**:
```
GET /api/v1/devices/{device_id}/capabilities
```

**Response format**:
```json
{
  "device_id": "yeelight_abc123",
  "type": "yeelight",
  "model": "color_bulb",
  "capabilities": {
    "standard": {
      "power": {
        "available": true,
        "states": ["on", "off", "toggle"],
        "current": "on"
      },
      "brightness": {
        "available": true,
        "type": "integer",
        "min": 1,
        "max": 100,
        "current": 80,
        "unit": "%"
      },
      "color": {
        "available": true,
        "modes": ["rgb", "temperature"],
        "rgb": {
          "type": "array",
          "items": {"type": "integer", "min": 0, "max": 255},
          "current": [255, 200, 100]
        },
        "temperature": {
          "type": "integer",
          "min": 1700,
          "max": 6500,
          "current": 4000,
          "unit": "K"
        }
      }
    },
    "device_specific": {
      "effects": {
        "available": true,
        "supported": [
          {
            "name": "disco",
            "description": "Disco lights effect",
            "params": {}
          },
          {
            "name": "pulse",
            "description": "Smooth pulsing",
            "params": {
              "speed": {"type": "integer", "min": 1, "max": 100, "default": 50}
            }
          },
          {
            "name": "music_sync",
            "description": "Sync with music (Yeelight-specific)",
            "params": {}
          }
        ]
      },
      "flow": {
        "available": true,
        "description": "Custom light flow sequences"
      }
    }
  },
  "metadata": {
    "firmware": "2.1.6_0099",
    "online": true,
    "last_seen": "2026-04-25T10:35:00Z"
  }
}
```

#### Przykład dla różnych typów urządzeń

**Yeelight Color Bulb**:
```json
{
  "id": "yeelight_abc123",
  "type": "yeelight",
  "capabilities": ["power", "brightness", "color", "color_temp", "effects", "flow"]
}
```

**Shelly Bulb RGBW (przyszłość)**:
```json
{
  "id": "shelly_xyz789",
  "type": "shelly",
  "capabilities": ["power", "brightness", "color", "timer", "energy"]
}
```

**Klient wie**:
- Oba mają `power`, `brightness`, `color` → Może użyć tych samych komponentów UI
- Yeelight ma `effects` → Pokaż przycisk "Effects"
- Shelly ma `energy` → Pokaż widget energy consumption

#### Abstrakcja w implementacji

**Backend** (dla deweloperów):
```python
# Abstrakcja - każdy typ urządzenia implementuje ten interface
class DeviceAdapter(ABC):
    @abstractmethod
    async def get_capabilities(self) -> DeviceCapabilities:
        """Zwraca capabilities w standardowym formacie"""
        pass

    @abstractmethod
    async def set_power(self, state: PowerState) -> bool:
        """Standardowa operacja - power"""
        pass

    @abstractmethod
    async def set_brightness(self, value: int) -> bool:
        """Standardowa operacja - brightness"""
        pass

    # Device-specific operations jako optional methods
    async def execute_effect(self, effect_name: str, params: dict) -> bool:
        """Optional: tylko dla urządzeń z effects capability"""
        raise NotImplementedError(f"{self.type} doesn't support effects")

class YeelightAdapter(DeviceAdapter):
    """Implementacja dla Yeelight"""
    async def get_capabilities(self):
        return DeviceCapabilities(
            standard=["power", "brightness", "color", "color_temp"],
            device_specific=["effects", "flow"]
        )

    async def execute_effect(self, effect_name: str, params: dict):
        # Yeelight-specific implementation
        await self.bulb.start_flow(...)

class ShellyAdapter(DeviceAdapter):
    """Przyszła implementacja dla Shelly"""
    async def get_capabilities(self):
        return DeviceCapabilities(
            standard=["power", "brightness", "color"],
            device_specific=["timer", "energy"]
        )

    async def execute_effect(self, effect_name: str, params: dict):
        raise NotImplementedError("Shelly doesn't support effects")
```

**API layer** (FastAPI):
```python
@app.post("/api/v1/devices/{device_id}/power")
async def set_power(device_id: str, request: PowerRequest):
    """Uniwersalny endpoint - działa dla wszystkich typów"""
    device = await device_registry.get(device_id)
    # device może być YeelightAdapter lub ShellyAdapter
    # API wywołuje tę samą metodę set_power()
    result = await device.set_power(request.state)
    return {"success": True, "state": result}

@app.post("/api/v1/devices/{device_id}/effect")
async def execute_effect(device_id: str, request: EffectRequest):
    """Device-specific endpoint - sprawdza capabilities"""
    device = await device_registry.get(device_id)

    # Sprawdź czy urządzenie wspiera effects
    caps = await device.get_capabilities()
    if "effects" not in caps.device_specific:
        raise HTTPException(
            status_code=400,
            detail=f"Device {device.type} doesn't support effects"
        )

    result = await device.execute_effect(request.name, request.params)
    return {"success": True, "effect": request.name}
```

#### Client-side flow (przykład)

**JavaScript/TypeScript client**:
```typescript
// 1. Pobierz listę urządzeń
const devices = await fetch('/api/v1/devices').then(r => r.json());

// 2. Dla każdego urządzenia renderuj UI bazując na capabilities
devices.forEach(device => {
  // Standardowe kontrolki (dostępne dla wszystkich)
  if (device.capabilities.includes('power')) {
    renderPowerButton(device.id);
  }
  if (device.capabilities.includes('brightness')) {
    renderBrightnessSlider(device.id);
  }
  if (device.capabilities.includes('color')) {
    renderColorPicker(device.id);
  }

  // Device-specific kontrolki
  if (device.capabilities.includes('effects')) {
    renderEffectsButton(device.id); // Tylko Yeelight
  }
  if (device.capabilities.includes('energy')) {
    renderEnergyWidget(device.id); // Tylko Shelly
  }
});

// 3. Po kliknięciu na urządzenie - pokaż szczegóły
async function showDeviceDetails(deviceId: string) {
  const caps = await fetch(`/api/v1/devices/${deviceId}/capabilities`)
    .then(r => r.json());

  // Renderuj UI bazując na szczegółowych capabilities
  renderDetailedControls(caps);
}

// 4. Wywołania API - te same dla wszystkich typów
async function togglePower(deviceId: string) {
  await fetch(`/api/v1/devices/${deviceId}/power`, {
    method: 'POST',
    body: JSON.stringify({ state: 'toggle' })
  });
}
```

### Endpoints:

#### Discovery & Listing
```
GET /api/v1/devices
Response: {
  "devices": [
    {
      "id": "yeelight_abc123",
      "name": "Living Room Bulb",
      "type": "yeelight",
      "model": "color_bulb",
      "ip": "192.168.1.100",
      "capabilities": ["power", "color", "brightness", "color_temp", "effects"],
      "status": {
        "power": "on",
        "brightness": 80,
        "rgb": [255, 200, 100]
      }
    }
  ],
  "last_discovery": "2026-04-25T10:30:00Z"
}

POST /api/v1/devices/discover
Response: {
  "discovered": 3,
  "devices": [...]
}
```

#### Device Control
```
POST /api/v1/devices/{device_id}/power
Body: {"state": "on"|"off"|"toggle"}

PUT /api/v1/devices/{device_id}/brightness
Body: {"value": 0-100}

PUT /api/v1/devices/{device_id}/color
Body: {
  "rgb": [255, 0, 0],  # lub
  "temperature": 3000  # Kelvin
}

POST /api/v1/devices/{device_id}/effect
Body: {
  "name": "disco" | "pulse" | "strobe" | "music_sync",
  "params": {...}  # effect-specific parameters
}

GET /api/v1/devices/{device_id}/capabilities
Response: {
  "power": {"type": "boolean"},
  "brightness": {"type": "integer", "min": 1, "max": 100},
  "color": {
    "rgb": {"type": "array", "items": "integer[0-255]"},
    "temperature": {"type": "integer", "min": 1700, "max": 6500}
  },
  "effects": ["disco", "pulse", "strobe", "music_sync"]
}
```

#### Health & Status
```
GET /api/health
Response: {"status": "ok", "version": "0.1.0"}

GET /api/v1/status
Response: {
  "devices_online": 3,
  "last_discovery": "2026-04-25T10:30:00Z",
  "uptime_seconds": 3600
}
```

### Error Handling (standardowe HTTP status codes):
```
200 OK - Success
201 Created - Device discovered/added
400 Bad Request - Invalid parameters
404 Not Found - Device not found
422 Unprocessable Entity - Validation error (FastAPI default)
500 Internal Server Error - Server error
503 Service Unavailable - Device offline/unreachable
```

### Response Format (consistent):
```json
// Success
{
  "success": true,
  "data": {...}
}

// Error
{
  "success": false,
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "Device yeelight_abc123 not found",
    "details": {...}
  }
}
```

## Implementacja techniczna

### Dependencies:
```txt
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
pydantic>=2.6.0
yeelight>=0.7.14
```

### Project Structure:
```
aac-iot-hub/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + routes
│   ├── models.py            # Pydantic models
│   ├── services/
│   │   ├── discovery.py     # Device discovery logic
│   │   └── device_control.py # Device control logic
│   └── api/
│       ├── v1/
│       │   ├── devices.py   # Device endpoints
│       │   └── health.py    # Health/status endpoints
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Przyszłe rozszerzenia (compatibility)

REST API łatwo rozszerzyć o:
1. **WebSocket dla events**: `ws://api/v1/devices/{id}/events` (live status updates)
2. **Server-Sent Events**: `GET /api/v1/devices/stream` (alternatywa dla WebSocket)
3. **Batch operations**: `POST /api/v1/batch` (wiele akcji w jednym request)
4. **Webhooks**: `POST /api/v1/webhooks` (powiadomienia o zmianach)
5. **GraphQL layer**: Optional GraphQL endpoint dla zaawansowanych klientów

## Konsekwencje

### Pozytywne:
- ✅ Standardowy, dobrze znany protokół
- ✅ Doskonały developer experience (Swagger docs, validation)
- ✅ Łatwe testowanie i debugging
- ✅ Szeroka kompatybilność z klientami
- ✅ Świetne narzędzia (Postman, curl, httpie)
- ✅ Możliwość rozbudowy (WebSocket, SSE, GraphQL)
- ✅ FastAPI = modern, fast, type-safe

### Negatywne:
- ⚠️ Nieznacznie więcej verbosity niż JSON-RPC
- ⚠️ Kilka requestów dla złożonych operacji (ale batch możliwy)

### Ryzyko i mitigation:
- **Ryzyko**: API może być trudne do wersjonowania
  **Mitigation**: Prefix `/api/v1/` od początku

- **Ryzyko**: Brak real-time updates
  **Mitigation**: Można dodać WebSocket endpoint w przyszłości

## Dokumentacja API

FastAPI automatycznie generuje:
- **OpenAPI 3.0 schema**: `/openapi.json`
- **Swagger UI**: `/docs` (interaktywna dokumentacja)
- **ReDoc**: `/redoc` (alternatywna dokumentacja)

## Powiązane ADR
- ADR-000: Wybór typu urządzenia IoT (Yeelight)
- ADR-001: Konteneryzacja i Deployment
- ADR-002: Docker Network Configuration

## Data
2026-04-25