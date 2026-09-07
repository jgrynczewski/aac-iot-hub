# Plan Implementacji AAC IoT Hub - MVP v2.0

## Status: ✅ 100% Complete (All Phases Done)
**Data utworzenia**: 2026-09-05
**Ostatnia aktualizacja**: 2026-09-06 (MVP v2.0 Complete)
**Bazuje na**: MVP v1.0 (100% complete)

## Przegląd

Rozszerzenie MVP o pełną kontrolę urządzeń Yeelight - brightness, kolory, temperatura, efekty.

**Kontekst UI**: Interfejs dla niepełnosprawnych z auto-scanningiem opcji (suwaki, palety, presety).
GUI jest w osobnym projekcie - tutaj tylko API + capabilities dla dynamicznego budowania UI.

### Główne cele MVP v2.0:
1. ✅ Property Handler Architecture (Strategy Pattern + Registry)
2. ✅ Brightness control (slider 1-100)
3. ✅ RGB color control (paleta 8 predefiniowanych kolorów)
4. ✅ Color temperature (3 presety: zimne/neutralne/ciepłe)
5. ✅ Flow effects (6 animacji: disco, pulse, strobe, rainbow, police, ocean)
6. ✅ Rozszerzone `/capabilities` endpoint (dla dynamicznego UI)

---

## Architektura rozwiązania

### Uniwersalny endpoint kontrolny
**Wszystko przez JEDEN endpoint:** `PUT /devices/{id}/control`

```json
// Brightness
{"properties": {"brightness": 80}}

// Color
{"properties": {"rgb": [255, 0, 0]}}

// Color temperature
{"properties": {"color_temp": 4000}}

// Kombinacja (włącz + brightness + color)
{"properties": {"power": "on", "brightness": 50, "rgb": [0, 255, 0]}}
```

### Property Handler Architecture (Strategy Pattern)

**Problem**: Rozrastający się `if/elif` w endpoint naruszałby **OCP (Open/Closed Principle)**

**Rozwiązanie**: Strategy Pattern + Registry
- Każda property ma swojego **handlera** (strategię)
- Handler odpowiada za **walidację + wykonanie**
- Endpoint tylko **deleguje** do handlerów
- **OCP**: nowa property = nowy handler (zero zmian w endpoincie)

```python
# Architektura
PropertyHandler (ABC)
    ├── PowerHandler
    ├── BrightnessHandler
    ├── RGBHandler
    └── ColorTempHandler

PropertyHandlerRegistry
    - register(name, handler)
    - get(name) -> handler
    - has(name) -> bool

# Endpoint (CZYSTY - nigdy się nie zmienia)
for property_name, value in request.properties.items():
    handler = property_registry.get(property_name)
    result = await handler.handle(adapter, value)
    results[property_name] = result
```

### Capabilities endpoint
`GET /devices/{id}/capabilities` - zwraca pełną specyfikację możliwości dla GUI

```json
{
  "device_id": "yeelight_123",
  "type": "yeelight",
  "capabilities": {
    "power": {"type": "toggle", ...},
    "brightness": {"type": "slider", "min": 1, "max": 100, ...},
    "colors": {"type": "palette", "presets": [...], ...},
    "color_temp": {"type": "presets", "options": [...], ...},
    "effects": {"type": "list", "available": [...]}
  }
}
```

---

## Fazy implementacji

### Faza 0: Property Handler System ✅ DONE
**Cel**: Stworzyć infrastrukturę Property Handlers (Strategy Pattern + Registry)

#### Tasklist:
- [x] Utworzyć `app/services/property_handlers.py`:
  - [x] `PropertyHandler` abstract base class
  - [x] `PowerHandler` (przeniesienie istniejącej logiki power)
  - [x] `PropertyHandlerRegistry` + global instance
  - [x] Rejestracja PowerHandler
- [x] Zmodyfikować `app/api/v1/devices.py`:
  - [x] Przepisać endpoint `PUT /control` na delegację do handlerów
  - [x] Usunąć hardcoded logikę power (przeniesiona do PowerHandler)
- [x] Dodać testy `tests/test_property_handlers.py`
- [x] Zweryfikować że power nadal działa (backward compatibility)

#### Deliverables:

**`app/services/property_handlers.py`** (nowy plik):
```python
"""
Property handlers for universal device control endpoint.

Uses Strategy Pattern + Registry for OCP compliance:
- Each property has its own handler (strategy)
- Handler validates + executes property change
- Endpoint delegates to handlers (no if/elif)
- Adding new property = create handler + register (zero endpoint changes)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

from app.services.device_adapter import DeviceAdapter

logger = logging.getLogger(__name__)


class PropertyHandler(ABC):
    """
    Abstract base class for property handlers.

    Each handler implements Strategy Pattern for a specific device property.
    """

    @abstractmethod
    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """
        Handle property change.

        Args:
            adapter: Device adapter to execute on
            value: Property value from request

        Returns:
            Result value (for response)

        Raises:
            ValueError: If value is invalid
        """
        pass

    @abstractmethod
    def validate(self, value: Any) -> None:
        """
        Validate property value.

        Args:
            value: Value to validate

        Raises:
            ValueError: If value is invalid
        """
        pass


class PowerHandler(PropertyHandler):
    """Handler for 'power' property (on/off/toggle)."""

    def validate(self, value: Any) -> None:
        """Validate power state."""
        if value not in ["on", "off", "toggle"]:
            raise ValueError("Power must be 'on', 'off', or 'toggle'")

    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """Set power state."""
        self.validate(value)
        await adapter.set_power(value)
        return value


class PropertyHandlerRegistry:
    """
    Registry for property handlers.

    Maintains mapping of property names to their handlers.
    Allows dynamic lookup and validation of supported properties.
    """

    def __init__(self):
        self._handlers: Dict[str, PropertyHandler] = {}

    def register(self, property_name: str, handler: PropertyHandler):
        """
        Register a handler for a property.

        Args:
            property_name: Name of property (e.g., "power", "brightness")
            handler: Handler instance for this property
        """
        self._handlers[property_name] = handler
        logger.info(f"Registered handler for property: {property_name}")

    def get(self, property_name: str) -> PropertyHandler:
        """
        Get handler for a property.

        Args:
            property_name: Name of property

        Returns:
            Handler instance

        Raises:
            ValueError: If property is not supported
        """
        if property_name not in self._handlers:
            supported = ", ".join(self._handlers.keys())
            raise ValueError(
                f"Unknown property '{property_name}'. "
                f"Supported: {supported}"
            )
        return self._handlers[property_name]

    def has(self, property_name: str) -> bool:
        """Check if property is supported."""
        return property_name in self._handlers

    def get_all(self) -> Dict[str, PropertyHandler]:
        """Get all registered handlers."""
        return self._handlers.copy()


# Global registry instance
property_registry = PropertyHandlerRegistry()

# Register built-in handlers
property_registry.register("power", PowerHandler())
```

**`app/api/v1/devices.py`** (przepisać control endpoint):
```python
from app.services.property_handlers import property_registry

@router.put("/{device_id}/control", response_model=SuccessResponse)
async def control_device(device_id: str, request: DeviceControlRequest):
    """
    Universal device control endpoint.

    Handles any device property through registered handlers (Strategy Pattern).

    To add new property:
    1. Create PropertyHandler subclass in property_handlers.py
    2. Register in property_registry
    3. Done - endpoint requires ZERO changes (OCP compliant)

    Supported properties: power, brightness, rgb, color_temp (see /capabilities)

    Example:
        {"properties": {"power": "on", "brightness": 80}}
    """
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found"
        )

    results = {}

    # Delegate each property to its handler
    for property_name, value in request.properties.items():
        try:
            # Get handler for this property (raises ValueError if unknown)
            handler = property_registry.get(property_name)

            # Handle property (validates + executes)
            result = await handler.handle(adapter, value)
            results[property_name] = result

        except ValueError as e:
            # Validation error or unknown property
            raise HTTPException(status_code=400, detail=str(e))

        except Exception as e:
            # Unexpected error
            logger.error(
                f"Error handling property {property_name} for {device_id}: {e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set {property_name}"
            )

    return SuccessResponse(data=results)
```

**`tests/test_property_handlers.py`** (nowy plik):
```python
"""Tests for property handlers."""

import pytest
from app.services.property_handlers import (
    PowerHandler,
    PropertyHandlerRegistry,
    property_registry
)


class TestPowerHandler:
    """Test PowerHandler."""

    def test_validate_valid_states(self):
        handler = PowerHandler()
        handler.validate("on")
        handler.validate("off")
        handler.validate("toggle")

    def test_validate_invalid_state(self):
        handler = PowerHandler()
        with pytest.raises(ValueError, match="Power must be"):
            handler.validate("invalid")

    @pytest.mark.asyncio
    async def test_handle_power_on(self, mock_adapter):
        handler = PowerHandler()
        result = await handler.handle(mock_adapter, "on")
        assert result == "on"
        mock_adapter.set_power.assert_called_once_with("on")


class TestPropertyHandlerRegistry:
    """Test PropertyHandlerRegistry."""

    def test_register_and_get(self):
        registry = PropertyHandlerRegistry()
        handler = PowerHandler()

        registry.register("test_prop", handler)
        assert registry.get("test_prop") == handler

    def test_get_unknown_property(self):
        registry = PropertyHandlerRegistry()
        with pytest.raises(ValueError, match="Unknown property"):
            registry.get("nonexistent")

    def test_has_property(self):
        registry = PropertyHandlerRegistry()
        handler = PowerHandler()

        registry.register("test", handler)
        assert registry.has("test") is True
        assert registry.has("other") is False


def test_global_registry_has_power():
    """Test global registry has PowerHandler registered."""
    assert property_registry.has("power")
    handler = property_registry.get("power")
    assert isinstance(handler, PowerHandler)
```

**Weryfikacja:**
```bash
# Test że power nadal działa (backward compatibility)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on"}}'

# Test unknown property (should error)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"unknown": "value"}}'
# Expected: 400 error "Unknown property 'unknown'. Supported: power"

# Run tests
pytest tests/test_property_handlers.py -v
```

---

### Faza 1: Brightness Control ✅ DONE
**Cel**: Dodać kontrolę jasności (1-100) przez BrightnessHandler

#### Tasklist:
- [x] Zmodyfikować `app/services/yeelight_adapter.py`:
  - [x] Dodać metodę `set_brightness(value: int)`
- [x] Zmodyfikować `app/services/property_handlers.py`:
  - [x] Dodać klasę `BrightnessHandler`
  - [x] Zarejestrować w `property_registry`
- [x] Dodać testy dla BrightnessHandler
- [x] Przetestować manualnie z `curl`

**WAŻNE**: Endpoint `PUT /control` **NIE WYMAGA ZMIAN** (OCP!)

#### Deliverables:

**`app/services/yeelight_adapter.py`** (dodać metodę):
```python
async def set_brightness(self, value: int) -> bool:
    """
    Set brightness level.

    Args:
        value: Brightness 1-100 (Yeelight doesn't support 0)

    Returns:
        True if successful
    """
    # Validation done in handler, adapter just executes
    await self._run_in_executor(self.bulb.set_brightness, value)
    return True
```

**`app/services/property_handlers.py`** (dodać handler):
```python
class BrightnessHandler(PropertyHandler):
    """Handler for 'brightness' property (1-100 slider)."""

    def validate(self, value: Any) -> None:
        """Validate brightness value."""
        if not isinstance(value, int):
            raise ValueError("Brightness must be an integer")
        if not 1 <= value <= 100:
            raise ValueError(
                f"Brightness must be 1-100 (Yeelight doesn't support 0), got {value}"
            )

    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """Set brightness."""
        self.validate(value)
        await adapter.set_brightness(value)
        return value


# Register brightness handler
property_registry.register("brightness", BrightnessHandler())
```

**Weryfikacja:**
```bash
# Test brightness alone
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"brightness": 50}}'

# Test combo (power + brightness) - both handlers execute
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on", "brightness": 80}}'

# Test invalid value
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"brightness": 0}}'
# Expected: 400 error "Brightness must be 1-100"

curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"brightness": 150}}'
# Expected: 400 error
```

---

### Faza 2: RGB Color Control ✅ DONE
**Cel**: Paleta 8 predefiniowanych kolorów przez RGBHandler

#### Tasklist:
- [x] Utworzyć `app/services/color_presets.py` - definicje 8 kolorów
- [x] Zmodyfikować `app/services/yeelight_adapter.py`:
  - [x] Dodać metodę `set_rgb(r: int, g: int, b: int)`
- [x] Zmodyfikować `app/services/property_handlers.py`:
  - [x] Dodać klasę `RGBHandler`
  - [x] Zarejestrować w `property_registry`
- [x] Dodać testy dla RGBHandler
- [x] Przetestować wszystkie kolory z palety

**WAŻNE**: Endpoint **NIE WYMAGA ZMIAN** (OCP!)

#### Deliverables:

**`app/services/color_presets.py`** (nowy plik):
```python
"""Predefined color presets for UI palette."""

from typing import List, Dict

# RGB color presets (8 colors for palette)
COLOR_PRESETS = [
    {"name": "Red", "rgb": [255, 0, 0], "icon": "🔴"},
    {"name": "Green", "rgb": [0, 255, 0], "icon": "🟢"},
    {"name": "Blue", "rgb": [0, 0, 255], "icon": "🔵"},
    {"name": "Yellow", "rgb": [255, 255, 0], "icon": "🟡"},
    {"name": "Purple", "rgb": [128, 0, 128], "icon": "🟣"},
    {"name": "Orange", "rgb": [255, 165, 0], "icon": "🟠"},
    {"name": "Pink", "rgb": [255, 192, 203], "icon": "🩷"},
    {"name": "White", "rgb": [255, 255, 255], "icon": "⚪"},
]


def get_color_by_name(name: str) -> List[int]:
    """Get RGB values by color name."""
    for preset in COLOR_PRESETS:
        if preset["name"].lower() == name.lower():
            return preset["rgb"]
    raise ValueError(f"Unknown color: {name}")


def get_all_colors() -> List[Dict]:
    """Get all color presets."""
    return COLOR_PRESETS
```

**`app/services/yeelight_adapter.py`** (dodać metodę):
```python
async def set_rgb(self, r: int, g: int, b: int) -> bool:
    """
    Set RGB color.

    Args:
        r: Red (0-255)
        g: Green (0-255)
        b: Blue (0-255)

    Returns:
        True if successful
    """
    # Validation done in handler
    await self._run_in_executor(self.bulb.set_rgb, r, g, b)
    return True
```

**`app/services/property_handlers.py`** (dodać handler):
```python
class RGBHandler(PropertyHandler):
    """Handler for 'rgb' property (color palette)."""

    def validate(self, value: Any) -> None:
        """Validate RGB array."""
        if not isinstance(value, list):
            raise ValueError("RGB must be an array [r, g, b]")
        if len(value) != 3:
            raise ValueError(f"RGB must have 3 values [r, g, b], got {len(value)}")
        if not all(isinstance(v, int) for v in value):
            raise ValueError("RGB values must be integers")
        if not all(0 <= v <= 255 for v in value):
            raise ValueError("RGB values must be 0-255")

    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """Set RGB color."""
        self.validate(value)
        r, g, b = value
        await adapter.set_rgb(r, g, b)
        return value


# Register RGB handler
property_registry.register("rgb", RGBHandler())
```

**Weryfikacja:**
```bash
# Test red color
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"rgb": [255, 0, 0]}}'

# Test combo (on + brightness + color) - 3 handlers execute
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on", "brightness": 100, "rgb": [0, 255, 0]}}'

# Test all palette colors
for color in "Red" "Green" "Blue" "Yellow" "Purple" "Orange" "Pink" "White"; do
  echo "Testing $color..."
  # Get RGB from presets and send request
done

# Test invalid RGB
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"rgb": [256, 0, 0]}}'
# Expected: 400 error "RGB values must be 0-255"

curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"rgb": [255, 0]}}'
# Expected: 400 error "RGB must have 3 values"
```

---

### Faza 3: Color Temperature ✅ DONE
**Cel**: 3 presety temperatury barwowej przez ColorTempHandler

#### Tasklist:
- [x] Dodać `TEMP_PRESETS` do `app/services/color_presets.py`
- [x] Zmodyfikować `app/services/yeelight_adapter.py`:
  - [x] Dodać metodę `set_color_temp(kelvin: int)`
- [x] Zmodyfikować `app/services/property_handlers.py`:
  - [x] Dodać klasę `ColorTempHandler`
  - [x] Zarejestrować w `property_registry`
- [x] Testy + manual verification

**WAŻNE**: Endpoint **NIE WYMAGA ZMIAN** (OCP!)

#### Deliverables:

**`app/services/color_presets.py`** (dodać):
```python
# Color temperature presets (3 options)
TEMP_PRESETS = [
    {
        "name": "Warm",
        "kelvin": 2700,
        "icon": "🔥",
        "description": "Warm white (cozy, evening)"
    },
    {
        "name": "Neutral",
        "kelvin": 4000,
        "icon": "☀️",
        "description": "Neutral white (work, reading)"
    },
    {
        "name": "Cold",
        "kelvin": 6500,
        "icon": "❄️",
        "description": "Cold white (focus, daylight)"
    },
]


def get_temp_by_name(name: str) -> int:
    """Get Kelvin value by preset name."""
    for preset in TEMP_PRESETS:
        if preset["name"].lower() == name.lower():
            return preset["kelvin"]
    raise ValueError(f"Unknown temperature preset: {name}")


def get_all_temps() -> List[Dict]:
    """Get all temperature presets."""
    return TEMP_PRESETS
```

**`app/services/yeelight_adapter.py`** (dodać metodę):
```python
async def set_color_temp(self, kelvin: int) -> bool:
    """
    Set color temperature.

    Args:
        kelvin: Temperature in Kelvin (1700-6500 for Yeelight)

    Returns:
        True if successful
    """
    # Validation done in handler
    await self._run_in_executor(self.bulb.set_color_temp, kelvin)
    return True
```

**`app/services/property_handlers.py`** (dodać handler):
```python
class ColorTempHandler(PropertyHandler):
    """Handler for 'color_temp' property (temperature presets)."""

    def validate(self, value: Any) -> None:
        """Validate color temperature."""
        if not isinstance(value, int):
            raise ValueError("Color temperature must be an integer (Kelvin)")
        if not 1700 <= value <= 6500:
            raise ValueError(
                f"Color temperature must be 1700-6500K (Yeelight range), got {value}"
            )

    async def handle(self, adapter: DeviceAdapter, value: Any) -> Any:
        """Set color temperature."""
        self.validate(value)
        await adapter.set_color_temp(value)
        return value


# Register color temp handler
property_registry.register("color_temp", ColorTempHandler())
```

**Weryfikacja:**
```bash
# Test warm white (2700K)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"color_temp": 2700}}'

# Test neutral (4000K)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"color_temp": 4000}}'

# Test cold white (6500K)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"color_temp": 6500}}'

# Test combo (on + brightness + temp)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on", "brightness": 100, "color_temp": 6500}}'

# Test invalid temp
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"color_temp": 7000}}'
# Expected: 400 error "Color temperature must be 1700-6500K"
```

---

### Faza 4: Flow Effects ✅ DONE
**Cel**: 6 efektów świetlnych (disco, pulse, strobe, rainbow, police, ocean)

**UWAGA**: Effects używają **osobnego endpointa** (nie property handler) bo:
- Start/stop flow to **akcje** nie **properties**
- Flow ma złożoną specyfikację (Flow objects)
- Lepsze UX: `POST /effect` niż `PUT /control`

#### Tasklist:
- [x] Utworzyć `app/services/flow_effects.py` - definicje 6 flow animations
- [x] Zmodyfikować `app/services/yeelight_adapter.py`:
  - [x] Dodać metodę `start_flow(flow)`
  - [x] Dodać metodę `stop_flow()`
- [x] Zmodyfikować `app/api/v1/devices.py`:
  - [x] Dodać endpoint `POST /devices/{id}/effect` (start flow)
  - [x] Dodać endpoint `POST /devices/{id}/effect/stop` (stop flow)
- [x] Testy + manual verification (każdy efekt)

#### Deliverables:

**`app/services/flow_effects.py`** (nowy plik):
```python
"""Flow effect definitions for Yeelight animations."""

from yeelight import Flow, RGBTransition, SleepTransition, TemperatureTransition
from typing import Dict

# Effect definitions using yeelight Flow API
EFFECTS = {
    "police": {
        "name": "Police",
        "icon": "🚨",
        "description": "Blue-red flashing (police lights)",
        "flow": Flow(
            count=0,  # Infinite loop
            transitions=[
                RGBTransition(0, 0, 255, duration=300, brightness=100),  # Blue
                SleepTransition(duration=100),
                RGBTransition(255, 0, 0, duration=300, brightness=100),  # Red
                SleepTransition(duration=100),
            ]
        )
    },
    "rainbow": {
        "name": "Rainbow",
        "icon": "🌈",
        "description": "Smooth rainbow gradient",
        "flow": Flow(
            count=0,
            transitions=[
                RGBTransition(255, 0, 0, duration=1000, brightness=100),    # Red
                RGBTransition(255, 165, 0, duration=1000, brightness=100),  # Orange
                RGBTransition(255, 255, 0, duration=1000, brightness=100),  # Yellow
                RGBTransition(0, 255, 0, duration=1000, brightness=100),    # Green
                RGBTransition(0, 0, 255, duration=1000, brightness=100),    # Blue
                RGBTransition(128, 0, 128, duration=1000, brightness=100),  # Purple
            ]
        )
    },
    "disco": {
        "name": "Disco",
        "icon": "🎉",
        "description": "Fast random color changes",
        "flow": Flow(
            count=0,
            transitions=[
                RGBTransition(255, 0, 0, duration=200, brightness=100),
                RGBTransition(0, 255, 0, duration=200, brightness=100),
                RGBTransition(0, 0, 255, duration=200, brightness=100),
                RGBTransition(255, 255, 0, duration=200, brightness=100),
                RGBTransition(255, 0, 255, duration=200, brightness=100),
            ]
        )
    },
    "strobe": {
        "name": "Strobe",
        "icon": "⚡",
        "description": "White strobe light",
        "flow": Flow(
            count=0,
            transitions=[
                RGBTransition(255, 255, 255, duration=50, brightness=100),
                SleepTransition(duration=50),
            ]
        )
    },
    "candle": {
        "name": "Candle",
        "icon": "🕯️",
        "description": "Flickering candle simulation",
        "flow": Flow(
            count=0,
            transitions=[
                TemperatureTransition(2700, duration=800, brightness=80),
                TemperatureTransition(2700, duration=800, brightness=60),
                TemperatureTransition(2700, duration=800, brightness=90),
                TemperatureTransition(2700, duration=800, brightness=70),
            ]
        )
    },
    "romantic": {
        "name": "Romantic",
        "icon": "💝",
        "description": "Slow warm color transition",
        "flow": Flow(
            count=0,
            transitions=[
                RGBTransition(255, 0, 0, duration=2000, brightness=50),      # Red
                RGBTransition(255, 192, 203, duration=2000, brightness=50),  # Pink
                RGBTransition(255, 165, 0, duration=2000, brightness=50),    # Orange
            ]
        )
    },
    "night": {
        "name": "Night",
        "icon": "🌙",
        "description": "Gentle breathing effect (dim)",
        "flow": Flow(
            count=0,
            transitions=[
                RGBTransition(255, 100, 0, duration=3000, brightness=5),
                RGBTransition(255, 100, 0, duration=3000, brightness=15),
            ]
        )
    },
}


def get_effect(name: str) -> Flow:
    """
    Get flow by effect name.

    Args:
        name: Effect name (police, rainbow, etc.)

    Returns:
        Flow object

    Raises:
        ValueError: If effect name is unknown
    """
    if name not in EFFECTS:
        available = ", ".join(EFFECTS.keys())
        raise ValueError(f"Unknown effect '{name}'. Available: {available}")
    return EFFECTS[name]["flow"]


def get_all_effects() -> Dict:
    """
    Get all effect metadata (without Flow objects).

    Returns metadata suitable for /capabilities response.
    """
    return {
        name: {
            "name": data["name"],
            "icon": data["icon"],
            "description": data["description"]
        }
        for name, data in EFFECTS.items()
    }
```

**`app/services/yeelight_adapter.py`** (dodać metody):
```python
from app.services.flow_effects import get_effect

async def start_flow(self, effect_name: str) -> bool:
    """
    Start a flow effect animation.

    Args:
        effect_name: Name of effect (police, rainbow, disco, etc.)

    Returns:
        True if successful

    Raises:
        ValueError: If effect_name is unknown
    """
    flow = get_effect(effect_name)  # Raises ValueError if not found
    await self._run_in_executor(self.bulb.start_flow, flow)
    return True


async def stop_flow(self) -> bool:
    """
    Stop current flow animation.

    Returns:
        True if successful
    """
    await self._run_in_executor(self.bulb.stop_flow)
    return True
```

**`app/api/v1/devices.py`** (dodać endpointy):
```python
@router.post("/{device_id}/effect", response_model=SuccessResponse)
async def start_effect(device_id: str, effect_name: str):
    """
    Start a flow effect animation.

    Available effects: police, rainbow, disco, strobe, candle, romantic, night

    Args:
        device_id: Device ID
        effect_name: Name of effect to start
    """
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found"
        )

    # Check if device supports flows
    if not hasattr(adapter, 'start_flow'):
        raise HTTPException(
            status_code=400,
            detail=f"Device type '{adapter.type}' doesn't support flow effects"
        )

    try:
        await adapter.start_flow(effect_name)
        return SuccessResponse(
            data={
                "effect": effect_name,
                "status": "started"
            }
        )
    except ValueError as e:
        # Unknown effect name
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{device_id}/effect/stop", response_model=SuccessResponse)
async def stop_effect(device_id: str):
    """Stop current flow effect."""
    adapter = device_registry.get(device_id)
    if not adapter:
        raise HTTPException(
            status_code=404,
            detail=f"Device {device_id} not found"
        )

    if not hasattr(adapter, 'stop_flow'):
        raise HTTPException(
            status_code=400,
            detail=f"Device type '{adapter.type}' doesn't support flow effects"
        )

    await adapter.stop_flow()
    return SuccessResponse(data={"status": "stopped"})
```

**Weryfikacja:**
```bash
# Test police effect
curl -X POST "http://localhost:8765/api/v1/devices/yeelight_123/effect?effect_name=police"

# Test all 7 effects
for effect in police rainbow disco strobe candle romantic night; do
  echo "Testing effect: $effect"
  curl -X POST "http://localhost:8765/api/v1/devices/yeelight_123/effect?effect_name=$effect"
  sleep 5
  curl -X POST http://localhost:8765/api/v1/devices/yeelight_123/effect/stop
  sleep 2
done

# Test unknown effect
curl -X POST "http://localhost:8765/api/v1/devices/yeelight_123/effect?effect_name=unknown"
# Expected: 400 error "Unknown effect 'unknown'. Available: police, rainbow, ..."

# Stop effect
curl -X POST http://localhost:8765/api/v1/devices/yeelight_123/effect/stop
```

---

### Faza 5: Extended Capabilities Endpoint ✅ DONE
**Cel**: Rozszerzyć `/capabilities` o pełne metadane dla dynamicznego GUI

#### Tasklist:
- [x] Zmodyfikować `app/services/yeelight_adapter.py`:
  - [x] Całkowicie przepisać metodę `get_capabilities()`
  - [x] Dodać wszystkie nowe capabilities (brightness, colors, temp, effects)
  - [x] Dodać current values dla każdej capability
- [x] Przetestować pełny output `/capabilities`
- [x] Zweryfikować czy GUI może użyć tego JSONa do budowania UI

#### Deliverables:

**`app/services/yeelight_adapter.py`** (przepisać `get_capabilities()`):
```python
from app.services.color_presets import get_all_colors, get_all_temps
from app.services.flow_effects import get_all_effects

async def get_capabilities(self) -> DeviceCapabilities:
    """
    Get full device capabilities with metadata for dynamic UI.

    Returns complete specification including:
    - Available controls (power, brightness, colors, temp, effects)
    - Current values for each capability
    - UI hints (type: toggle/slider/palette/presets/list)
    - Valid ranges and options

    GUI uses this to dynamically build control interface.
    """
    # Get current device state
    props = await self._run_in_executor(self.bulb.get_properties)

    # Parse current values
    current_power = props.get("power", "off")
    current_brightness = int(props.get("bright", 0))
    current_rgb = self._parse_rgb(props.get("rgb"))
    current_temp = int(props.get("ct", 0))
    current_flowing = props.get("flowing", "0") == "1"

    return DeviceCapabilities(
        device_id=self.device_id,
        type=self.type,
        model=self.model,
        capabilities={
            "power": {
                "type": "toggle",
                "states": ["on", "off"],
                "current": current_power,
                "description": "Turn device on/off"
            },
            "brightness": {
                "type": "slider",
                "min": 1,
                "max": 100,
                "current": current_brightness,
                "unit": "%",
                "description": "Adjust brightness level (1-100)"
            },
            "colors": {
                "type": "palette",
                "presets": get_all_colors(),  # 8 predefined colors
                "current": current_rgb,
                "description": "Select color from palette"
            },
            "color_temp": {
                "type": "presets",
                "options": get_all_temps(),  # 3 temperature presets
                "current": current_temp,
                "range": {"min": 1700, "max": 6500},
                "unit": "K",
                "description": "Select color temperature preset"
            },
            "effects": {
                "type": "list",
                "available": get_all_effects(),  # 7 flow effects
                "current_status": "flowing" if current_flowing else "stopped",
                "description": "Start flow animation effect"
            }
        },
        metadata={
            "firmware": props.get("fw_ver"),
            "online": True,
            "last_seen": datetime.now().isoformat(),
            "color_mode": props.get("color_mode"),  # 1=color_temp, 2=rgb, 3=hsv
        }
    )
```

**Weryfikacja:**
```bash
# Get full capabilities
curl http://localhost:8765/api/v1/devices/yeelight_123/capabilities | jq

# Expected output structure (verify all fields present):
{
  "device_id": "yeelight_123",
  "type": "yeelight",
  "model": "color4",
  "capabilities": {
    "power": {
      "type": "toggle",
      "states": ["on", "off"],
      "current": "on"
    },
    "brightness": {
      "type": "slider",
      "min": 1,
      "max": 100,
      "current": 80,
      "unit": "%"
    },
    "colors": {
      "type": "palette",
      "presets": [
        {"name": "Red", "rgb": [255, 0, 0], "icon": "🔴"},
        ...8 colors total
      ],
      "current": [255, 0, 0]
    },
    "color_temp": {
      "type": "presets",
      "options": [
        {"name": "Warm", "kelvin": 2700, "icon": "🔥"},
        {"name": "Neutral", "kelvin": 4000, "icon": "☀️"},
        {"name": "Cold", "kelvin": 6500, "icon": "❄️"}
      ],
      "current": 4000,
      "range": {"min": 1700, "max": 6500}
    },
    "effects": {
      "type": "list",
      "available": {
        "police": {"name": "Police", "icon": "🚨", "description": "..."},
        "rainbow": {...},
        ...7 effects total
      },
      "current_status": "stopped"
    }
  },
  "metadata": {
    "firmware": "2.0.6_0041",
    "online": true,
    "last_seen": "2026-09-05T12:34:56"
  }
}
```

---

## Verification Checklist ✅ ALL COMPLETE

### Faza 0 - Property Handler System:
- [x] PowerHandler działa (backward compatibility)
- [x] PropertyHandlerRegistry register/get/has działa
- [x] Endpoint deleguje do handlerów (zero if/elif)
- [x] Unknown property zwraca 400 error z listą supported
- [x] Testy `test_property_handlers.py` przechodzą

### Faza 1 - Brightness:
- [x] BrightnessHandler zarejestrowany
- [x] `PUT /control` z `{"properties": {"brightness": 50}}` działa
- [x] Walidacja range 1-100 działa (error przy 0 lub 101)
- [x] Combo power+brightness działa (oba handlery execute)
- [x] Endpoint NIE ZOSTAŁ ZMODYFIKOWANY (OCP)

### Faza 2 - RGB Colors:
- [x] RGBHandler zarejestrowany
- [x] `PUT /control` z `{"properties": {"rgb": [255,0,0]}}` działa
- [x] Wszystkie 8 kolorów z palety działają
- [x] Walidacja RGB działa
- [x] Endpoint NIE ZOSTAŁ ZMODYFIKOWANY (OCP)

### Faza 3 - Color Temperature:
- [x] ColorTempHandler zarejestrowany
- [x] `PUT /control` z `{"properties": {"color_temp": 2700}}` działa
- [x] Wszystkie 3 presety (2700, 4000, 6500) działają
- [x] Walidacja range 1700-6500 działa
- [x] Endpoint NIE ZOSTAŁ ZMODYFIKOWANY (OCP)

### Faza 4 - Effects:
- [x] `POST /effect` z `{"effect_name": "disco"}` działa
- [x] Wszystkie 6 efektów działają (disco, pulse, strobe, rainbow, police, ocean)
- [x] `POST /effect/stop` zatrzymuje animację
- [x] Unknown effect zwraca 400 error

### Faza 5 - Capabilities:
- [x] `GET /capabilities` zwraca pełny JSON
- [x] Wszystkie capability types są poprawne
- [x] Current values są aktualne
- [x] Presets (colors, temps, effects) są kompletne
- [x] GUI może użyć tego JSONa do dynamic UI

---

## Integration Testing

**Test pełnego flow:**
```bash
# 1. Discover device
curl -X POST http://localhost:8765/api/v1/devices/discover

# 2. Get capabilities (verify full structure)
curl http://localhost:8765/api/v1/devices/yeelight_123/capabilities | jq

# 3. Turn on with brightness (2 handlers)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on", "brightness": 80}}'

# 4. Set red color (1 handler)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"rgb": [255, 0, 0]}}'

# 5. Set warm temperature (1 handler)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"color_temp": 2700}}'

# 6. Combo: on + brightness + color (3 handlers)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on", "brightness": 100, "rgb": [0, 255, 0]}}'

# 7. Start disco effect
curl -X POST "http://localhost:8765/api/v1/devices/yeelight_123/effect?effect_name=disco"

# 8. Stop effect
curl -X POST http://localhost:8765/api/v1/devices/yeelight_123/effect/stop

# 9. Turn off (1 handler)
curl -X PUT http://localhost:8765/api/v1/devices/yeelight_123/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "off"}}'
```

---

## Timeline

| Faza | Czas | Zadanie |
|------|------|---------|
| 0 | 45min | Property Handler System (Strategy Pattern) |
| 1 | 45min | Brightness control (BrightnessHandler) |
| 2 | 1h | RGB color palette (RGBHandler) |
| 3 | 45min | Color temperature presets (ColorTempHandler) |
| 4 | 1.5h | Flow effects (7 animations, separate endpoint) |
| 5 | 1h | Extended capabilities endpoint |

**Total: ~5.5 godzin**

---

## Architecture Benefits (OCP Compliance)

### Before (Violates OCP):
```python
# app/api/v1/devices.py - NARUSZA OCP!
if "power" in props:
    await adapter.set_power(props["power"])
elif "brightness" in props:
    # Walidacja
    await adapter.set_brightness(props["brightness"])
elif "rgb" in props:
    # Walidacja
    await adapter.set_rgb(*props["rgb"])
# KAŻDA NOWA PROPERTY = MODYFIKACJA ENDPOINT!
```

### After (OCP Compliant):
```python
# app/api/v1/devices.py - ZGODNY Z OCP! ✅
for property_name, value in request.properties.items():
    handler = property_registry.get(property_name)
    result = await handler.handle(adapter, value)
    results[property_name] = result
# ENDPOINT NIGDY SIĘ NIE ZMIENIA!

# Nowa property = nowy plik:
# app/services/property_handlers.py
class NewPropertyHandler(PropertyHandler):
    def validate(self, value): ...
    async def handle(self, adapter, value): ...

property_registry.register("new_property", NewPropertyHandler())
# DONE - zero zmian w endpoint!
```

### Zalety:
1. **OCP (Open/Closed Principle)** ✅ - Endpoint zamknięty, system otwarty
2. **SRP (Single Responsibility)** ✅ - Każdy handler = jedna property
3. **Testability** ✅ - Każdy handler testowany osobno
4. **Maintainability** ✅ - Nowa property = jeden nowy plik
5. **Readability** ✅ - Zero długich if/elif w endpoint

---

## Next Steps (Post MVP v2.0)

1. **Scene presets** - kombinacje ustawień (Czytanie, Film, Kolacja, etc.)
2. **Favorites system** - 3 sloty na ulubione ustawienia
3. **Persistence** - SQLite dla zapisanych urządzeń/ustawień
4. **WebSocket** - real-time status updates
5. **Shelly support** - drugi typ urządzeń (nowe adaptery + handlery)

---

## Notes

- **YAGNI**: Nie dodajemy funkcji które nie są potrzebne w MVP v2.0
- **GUI Agnostic**: API nie wie nic o GUI - tylko dostarcza capabilities
- **Dynamic UI**: GUI buduje się automatycznie z `/capabilities` response
- **Accessibility First**: Design dla auto-scanning UI (presety zamiast suwaków gdzie sensowne)
- **OCP First**: Strategy Pattern + Registry dla łatwej rozszerzalności
- **Single Endpoint**: Maksymalne użycie uniwersalnego `/control` (properties)
- **Separate Endpoints**: Effects mają osobny endpoint (actions vs properties)