# AAC IoT Hub - Next Steps & Development Context

**Document Purpose:** Kompletny kontekst dla wznowienia rozwoju projektu po przerwie.

**Last Updated:** 2026-05-09

**Current Status:** ✅ **MVP Complete (100%)** - Gotowy do rozszerzania

---

## 🎯 Current State Summary

### **What is DONE (MVP v1.0):**

✅ **Core Infrastructure (100%)**
- FastAPI REST API server
- Docker containerization (host network mode for SSDP)
- Pydantic schemas for validation
- Device abstraction layer (adapter pattern)
- SSDP discovery service for Yeelight
- Global device registry (in-memory)

✅ **API Endpoints (Basic Control)**
- `GET /api/health` - Health check
- `GET /api/v1/status` - Detailed status
- `GET /api/v1/devices` - List all devices
- `POST /api/v1/devices/discover` - Trigger SSDP discovery
- `GET /api/v1/devices/{id}` - Get device details
- `GET /api/v1/devices/{id}/capabilities` - Get capabilities
- `PUT /api/v1/devices/{id}/control` - **Universal control endpoint**

✅ **Current Capabilities (Power Only)**
```json
{
  "properties": {
    "power": "on|off|toggle"
  }
}
```

✅ **Testing (39 tests passing)**
- tests/test_health.py (4 tests)
- tests/test_devices.py (15 tests)
- tests/test_device_adapter.py (12 tests)
- tests/test_discovery.py (8 tests)

✅ **Documentation**
- README.md - Quick start, usage
- docs/STATUS.md - Implementation status (100% complete)
- docs/API_EXAMPLES.md - curl examples
- docs/GUI_REQUIREMENTS.md - **NEW:** Specyfikacja dla GUI projektu
- docs/IMPLEMENTATION_PLAN.md - Original plan (all phases complete)
- 4x ADR documents (architecture decisions)

✅ **Manual Testing**
- Tested with real Yeelight devices
- All endpoints verified
- SSDP discovery works
- Power control (on/off/toggle) works

---

## 🚀 What is NEXT (MVP v2.0)

### **Priority 1: Extended Control Capabilities**

**Goal:** Rozszerzyć API o pełną kontrolę żarówki zgodnie z GUI requirements.

#### **1.1 Brightness Control**
**File to modify:** `app/services/yeelight_adapter.py`

**Add method:**
```python
async def set_brightness(self, value: int, effect: str = "smooth", duration: int = 500) -> bool:
    """
    Set bulb brightness.

    Args:
        value: 1-100
        effect: "smooth" or "sudden"
        duration: transition time in ms

    Raises:
        ValueError: if value out of range
    """
    if not 1 <= value <= 100:
        raise ValueError(f"Brightness must be 1-100, got {value}")

    await self._run_in_executor(
        self.bulb.set_brightness,
        value,
        effect=effect,
        duration=duration
    )
    return True
```

**Update control endpoint:** `app/api/v1/devices.py`
```python
# In control_device() function, add:
elif capability == "brightness":
    value = request.properties.get("brightness")
    await adapter.set_brightness(value)
    applied_changes[capability] = value
```

**Update tests:** `tests/test_device_adapter.py`
- Add `test_yeelight_adapter_set_brightness()`
- Add `test_yeelight_adapter_set_brightness_invalid_range()`

---

#### **1.2 RGB Color Control**
**File to modify:** `app/services/yeelight_adapter.py`

**Add method:**
```python
async def set_rgb(self, red: int, green: int, blue: int,
                  effect: str = "smooth", duration: int = 500) -> bool:
    """
    Set RGB color.

    Args:
        red: 0-255
        green: 0-255
        blue: 0-255
        effect: "smooth" or "sudden"
        duration: transition time in ms

    Raises:
        ValueError: if any value out of range
    """
    if not all(0 <= c <= 255 for c in [red, green, blue]):
        raise ValueError(f"RGB values must be 0-255")

    await self._run_in_executor(
        self.bulb.set_rgb,
        red, green, blue,
        effect=effect,
        duration=duration
    )
    return True
```

**Update control endpoint:**
```python
elif capability == "rgb":
    rgb = request.properties.get("rgb")  # [r, g, b]
    await adapter.set_rgb(*rgb)
    applied_changes[capability] = rgb
```

---

#### **1.3 Color Temperature Control**
**File to modify:** `app/services/yeelight_adapter.py`

**Add method:**
```python
async def set_color_temp(self, degrees: int,
                        effect: str = "smooth", duration: int = 500) -> bool:
    """
    Set color temperature.

    Args:
        degrees: 1700-6500 Kelvin
        effect: "smooth" or "sudden"
        duration: transition time in ms

    Raises:
        ValueError: if degrees out of range
    """
    if not 1700 <= degrees <= 6500:
        raise ValueError(f"Color temp must be 1700-6500K, got {degrees}")

    await self._run_in_executor(
        self.bulb.set_color_temp,
        degrees,
        effect=effect,
        duration=duration
    )
    return True
```

**Update control endpoint:**
```python
elif capability == "color_temp":
    temp = request.properties.get("color_temp")
    await adapter.set_color_temp(temp)
    applied_changes[capability] = temp
```

---

#### **1.4 Update Schemas**
**File to modify:** `app/schemas/device.py`

**Update DeviceCapabilities:**
```python
# Add to capabilities list
capabilities: List[str] = ["power"]  # Change to:
capabilities: List[str] = ["power", "brightness", "rgb", "color_temp"]
```

**Update get_capabilities() in YeelightAdapter:**
```python
capabilities={
    "power": {
        "widget": "toggle",
        "label": "Power",
        "states": ["on", "off", "toggle"],
        "current": status.status.power
    },
    "brightness": {
        "widget": "slider",
        "label": "Brightness",
        "min": 1,
        "max": 100,
        "current": current_brightness  # get from status
    },
    "rgb": {
        "widget": "color_picker",
        "label": "RGB Color",
        "current": [r, g, b]  # get from status
    },
    "color_temp": {
        "widget": "slider",
        "label": "Color Temperature",
        "min": 1700,
        "max": 6500,
        "unit": "K",
        "current": current_temp  # get from status
    }
}
```

---

### **Priority 2: Flow Animations**

#### **2.1 Create Flow Definitions**
**New file:** `app/services/flows.py`

```python
"""Predefined flow animations for Yeelight bulbs."""

from yeelight import Flow, RGBTransition, HSVTransition, SleepTransition, TemperatureTransition
import random


def create_police_flow() -> Flow:
    """Police siren effect (blue-red flashing)."""
    return Flow(
        count=0,  # infinite
        transitions=[
            RGBTransition(0, 0, 255, duration=300, brightness=100),
            SleepTransition(200),
            RGBTransition(255, 0, 0, duration=300, brightness=100),
            SleepTransition(200),
        ]
    )


def create_rainbow_flow() -> Flow:
    """Rainbow color cycle."""
    return Flow(
        count=0,
        transitions=[
            HSVTransition(0, 100, duration=1000),    # Red
            HSVTransition(60, 100, duration=1000),   # Yellow
            HSVTransition(120, 100, duration=1000),  # Green
            HSVTransition(180, 100, duration=1000),  # Cyan
            HSVTransition(240, 100, duration=1000),  # Blue
            HSVTransition(300, 100, duration=1000),  # Magenta
        ]
    )


def create_disco_flow() -> Flow:
    """Random color party mode."""
    transitions = []
    for _ in range(10):
        transitions.extend([
            RGBTransition(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
                duration=200,
                brightness=100
            ),
            SleepTransition(100),
        ])
    return Flow(count=0, transitions=transitions)


def create_strobe_flow() -> Flow:
    """White strobe light."""
    return Flow(
        count=0,
        transitions=[
            RGBTransition(255, 255, 255, duration=50, brightness=100),
            SleepTransition(50),
            RGBTransition(0, 0, 0, duration=50, brightness=1),
            SleepTransition(50),
        ]
    )


def create_candle_flow() -> Flow:
    """Candle flicker simulation."""
    transitions = []
    for _ in range(10):
        transitions.append(
            TemperatureTransition(
                2700,
                duration=random.randint(800, 1200),
                brightness=random.randint(60, 90)
            )
        )
    return Flow(count=0, transitions=transitions)


def create_romantic_flow() -> Flow:
    """Smooth warm color transitions."""
    return Flow(
        count=0,
        transitions=[
            TemperatureTransition(2700, duration=2000, brightness=60),
            TemperatureTransition(2000, duration=2000, brightness=40),
            TemperatureTransition(2500, duration=2000, brightness=50),
        ]
    )


def create_magic_flow() -> Flow:
    """Slow random color mix."""
    transitions = []
    for _ in range(5):
        transitions.append(
            HSVTransition(
                random.randint(0, 359),
                random.randint(70, 100),
                duration=3000
            )
        )
    return Flow(count=0, transitions=transitions)


# Registry of all flows
PREDEFINED_FLOWS = {
    "police": create_police_flow,
    "rainbow": create_rainbow_flow,
    "disco": create_disco_flow,
    "strobe": create_strobe_flow,
    "candle": create_candle_flow,
    "romantic": create_romantic_flow,
    "magic": create_magic_flow,
}


def get_flow(name: str) -> Flow:
    """
    Get flow by name.

    Args:
        name: Flow name (police, rainbow, etc.)

    Returns:
        Flow object

    Raises:
        ValueError: if flow name not found
    """
    if name not in PREDEFINED_FLOWS:
        raise ValueError(f"Unknown flow: {name}. Available: {list(PREDEFINED_FLOWS.keys())}")

    return PREDEFINED_FLOWS[name]()
```

#### **2.2 Add Flow Methods to Adapter**
**File to modify:** `app/services/yeelight_adapter.py`

```python
from app.services.flows import get_flow

# Add methods:
async def start_flow(self, flow_name: str) -> bool:
    """
    Start predefined flow animation.

    Args:
        flow_name: Name of flow (police, rainbow, disco, etc.)

    Raises:
        ValueError: if flow name unknown
    """
    flow = get_flow(flow_name)
    await self._run_in_executor(self.bulb.start_flow, flow)
    return True


async def stop_flow(self) -> bool:
    """Stop current flow animation."""
    await self._run_in_executor(self.bulb.stop_flow)
    return True
```

#### **2.3 Update Control Endpoint**
**File:** `app/api/v1/devices.py`

```python
elif capability == "flow":
    flow_name = request.properties.get("flow")
    await adapter.start_flow(flow_name)
    applied_changes[capability] = flow_name

elif capability == "flow_action":
    action = request.properties.get("flow_action")
    if action == "stop":
        await adapter.stop_flow()
        applied_changes[capability] = "stopped"
```

---

### **Priority 3: GUI Preset Colors**

#### **3.1 Create Color Presets File**
**New file:** `app/services/presets.py`

```python
"""Color and scene presets for GUI."""

# RGB Color Presets
PRESET_COLORS = {
    "white":   (255, 255, 255),
    "yellow":  (255, 255, 0),
    "red":     (255, 0, 0),
    "green":   (0, 255, 0),
    "blue":    (0, 0, 255),
    "purple":  (128, 0, 128),
    "orange":  (255, 165, 0),
    "pink":    (255, 192, 203),
}

# Color Temperature Presets
COLOR_TEMPS = {
    "warm":    2700,  # Ciepłe
    "neutral": 4000,  # Neutralne
    "cool":    6500,  # Zimne
}

# Scene Presets (brightness + color_temp/rgb)
SCENES = {
    "reading": {
        "color_temp": 5000,
        "brightness": 100,
    },
    "movie": {
        "color_temp": 2700,
        "brightness": 20,
    },
    "night": {
        "rgb": [255, 0, 0],
        "brightness": 5,
    },
    "work": {
        "color_temp": 6500,
        "brightness": 100,
    },
    "dinner": {
        "color_temp": 3000,
        "brightness": 60,
    },
}
```

#### **3.2 Add Convenience Methods**
**File:** `app/services/yeelight_adapter.py`

```python
from app.services.presets import PRESET_COLORS, COLOR_TEMPS, SCENES

async def set_preset_color(self, color_name: str) -> bool:
    """Set color from preset name."""
    if color_name not in PRESET_COLORS:
        raise ValueError(f"Unknown color: {color_name}")

    rgb = PRESET_COLORS[color_name]
    await self.set_rgb(*rgb)
    return True


async def set_preset_temp(self, temp_name: str) -> bool:
    """Set color temp from preset name."""
    if temp_name not in COLOR_TEMPS:
        raise ValueError(f"Unknown temp: {temp_name}")

    temp = COLOR_TEMPS[temp_name]
    await self.set_color_temp(temp)
    return True


async def set_scene(self, scene_name: str) -> bool:
    """Apply predefined scene."""
    if scene_name not in SCENES:
        raise ValueError(f"Unknown scene: {scene_name}")

    scene = SCENES[scene_name]

    # Apply brightness
    if "brightness" in scene:
        await self.set_brightness(scene["brightness"])

    # Apply color temp or RGB
    if "color_temp" in scene:
        await self.set_color_temp(scene["color_temp"])
    elif "rgb" in scene:
        await self.set_rgb(*scene["rgb"])

    return True
```

---

## 📁 File Structure Reference

```
aac-iot-hub/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Settings
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── devices.py         # 🔄 TO MODIFY: Add new capabilities
│   │       └── health.py
│   │
│   ├── schemas/
│   │   ├── device.py              # 🔄 TO MODIFY: Update capabilities
│   │   ├── requests.py
│   │   └── responses.py
│   │
│   └── services/
│       ├── device_adapter.py      # Abstract base
│       ├── yeelight_adapter.py    # 🔄 TO MODIFY: Add new methods
│       ├── device_registry.py
│       ├── discovery.py
│       ├── flows.py               # ➕ TO CREATE: Flow definitions
│       └── presets.py             # ➕ TO CREATE: Color/scene presets
│
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_devices.py            # 🔄 TO MODIFY: Add tests for new features
│   ├── test_device_adapter.py     # 🔄 TO MODIFY: Add tests for new methods
│   └── test_discovery.py
│
├── docs/
│   ├── STATUS.md                  # ✅ Current: 100% complete
│   ├── API_EXAMPLES.md            # 🔄 TO UPDATE: Add new endpoint examples
│   ├── GUI_REQUIREMENTS.md        # ✅ New: GUI spec
│   ├── IMPLEMENTATION_PLAN.md
│   ├── MANUAL_TESTING.md
│   └── adr/                       # Architecture decisions
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt               # 🔄 TO UPDATE: Add yeelight flows deps
├── pytest.ini
└── README.md                      # 🔄 TO UPDATE: Add new features
```

---

## 🔧 Technical Context

### **Yeelight Library Methods Available**

Already used:
- ✅ `bulb.turn_on()`
- ✅ `bulb.turn_off()`
- ✅ `bulb.toggle()`
- ✅ `bulb.get_properties()`

Ready to use:
- ⏳ `bulb.set_brightness(brightness, effect="smooth", duration=500)`
- ⏳ `bulb.set_rgb(red, green, blue, effect="smooth", duration=500)`
- ⏳ `bulb.set_color_temp(degrees, effect="smooth", duration=500)`
- ⏳ `bulb.set_hsv(hue, saturation, value, effect="smooth", duration=500)`
- ⏳ `bulb.start_flow(flow_object)`
- ⏳ `bulb.stop_flow()`
- ⏳ `bulb.set_scene(scene_class, *args)`
- ⏳ `bulb.set_adjust(action, prop)` - increase/decrease/circle
- ⏳ `bulb.start_music(port)` - remove rate limit
- ⏳ `bulb.stop_music()`

### **Current API Capabilities**

**Implemented:**
```python
{
  "power": "on|off|toggle"
}
```

**To Implement:**
```python
{
  "power": "on|off|toggle",
  "brightness": 1-100,
  "rgb": [r, g, b],           # 0-255 each
  "color_temp": 1700-6500,    # Kelvin
  "flow": "police|rainbow|disco|strobe|candle|romantic|magic",
  "flow_action": "start|stop",
  "preset_color": "white|yellow|red|green|blue|purple|orange|pink",
  "preset_temp": "warm|neutral|cool",
  "scene": "reading|movie|night|work|dinner"
}
```

### **Rate Limiting**

- **Normal mode:** 60 commands/minute
- **Music mode:** Unlimited (use for flows)
- **Recommendation:** Auto-enable music mode when starting flows

---

## 📝 Development Workflow

### **When You Resume:**

1. **Quick Status Check:**
   ```bash
   cd /path/to/aac-iot-hub
   docker compose ps
   pytest tests/ -v
   ```

2. **Start with Priority 1.1 (Brightness):**
   - Modify `app/services/yeelight_adapter.py`
   - Update `app/api/v1/devices.py`
   - Add tests to `tests/test_device_adapter.py`
   - Test manually with real bulb
   - Update `docs/API_EXAMPLES.md`

3. **Test Each Feature:**
   ```bash
   # Unit tests
   pytest tests/test_device_adapter.py::test_set_brightness -v

   # Manual test
   curl -X PUT http://localhost:8765/api/v1/devices/{id}/control \
     -H "Content-Type: application/json" \
     -d '{"properties": {"brightness": 50}}'
   ```

4. **Update Documentation:**
   - `docs/API_EXAMPLES.md` - Add curl examples
   - `docs/STATUS.md` - Update progress
   - `README.md` - Add to feature list

---

## 🎯 Success Criteria for MVP v2.0

### **Phase 1 Complete When:**
- ✅ Brightness control works (1-100)
- ✅ RGB color control works (8 preset colors)
- ✅ Color temperature works (3 presets)
- ✅ All tests pass
- ✅ API_EXAMPLES.md updated
- ✅ GUI can use basic color control

### **Phase 2 Complete When:**
- ✅ 3-5 flow animations work
- ✅ Start/stop flow works
- ✅ All tests pass
- ✅ GUI has "WOW" effects

### **Phase 3 Complete When:**
- ✅ Scenes work (reading, movie, night, work, dinner)
- ✅ Favorites system implemented (optional)
- ✅ All tests pass
- ✅ Full GUI functionality enabled

---

## 💡 Quick Reference

### **Test the Current System:**
```bash
# Start container
docker compose up -d

# Test health
curl http://localhost:8765/api/health

# Discover devices
curl -X POST http://localhost:8765/api/v1/devices/discover

# Control device (power only for now)
DEVICE_ID="yeelight_..."
curl -X PUT http://localhost:8765/api/v1/devices/${DEVICE_ID}/control \
  -H "Content-Type: application/json" \
  -d '{"properties": {"power": "on"}}'
```

### **Run Tests:**
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_device_adapter.py -v

# With coverage
pytest --cov=app tests/
```

### **Check Logs:**
```bash
docker compose logs -f aac-iot-hub
```

---

## 🔗 Related Documentation

**In this repo:**
- `README.md` - Main documentation
- `docs/STATUS.md` - Implementation status (100% MVP v1.0)
- `docs/API_EXAMPLES.md` - Current API usage examples
- `docs/GUI_REQUIREMENTS.md` - **NEW:** Complete GUI specification
- `docs/IMPLEMENTATION_PLAN.md` - Original implementation plan
- `docs/adr/` - Architecture Decision Records

**External:**
- [Yeelight Python Library](https://yeelight.readthedocs.io/)
- [Yeelight API Docs](https://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf)

---

## ⚠️ Important Notes

### **Before You Code:**
1. **Read `docs/GUI_REQUIREMENTS.md`** - Contains full spec from our discussion
2. **Check current tests pass:** `pytest tests/ -v`
3. **Review ADR documents** - Understand architecture decisions

### **GUI Project Integration:**
- GUI project will consume this API
- ON/OFF already works - GUI can start with that
- When GUI needs more features, come back here and implement Priority 1-3
- Keep API endpoints backward compatible

### **Database/Persistence:**
- Currently: In-memory only
- Favorites feature will need persistence (SQLite recommended)
- Can defer to Phase 3

### **Testing Strategy:**
- Write tests FIRST for new features
- Use mocks for unit tests (no real bulb needed)
- Manual test with real bulb after implementation
- Update integration tests

---

## 🎬 Next Session Starter Prompt

**When you return to this project, use this prompt:**

```
I'm resuming development of AAC IoT Hub project.
Read NEXT_STEPS.md for full context.

Current status: MVP v1.0 complete (power control only)
Next task: Implement Priority 1.1 (Brightness Control)

Files to modify:
- app/services/yeelight_adapter.py (add set_brightness method)
- app/api/v1/devices.py (handle brightness property)
- tests/test_device_adapter.py (add brightness tests)

Let's start with the YeelightAdapter implementation.
```

---

**Good luck with the GUI project! 🎨💡**

**When you're ready to expand the API, everything you need is in this document.**

---

**Document Version:** 1.0
**Created:** 2026-05-09
**Status:** Ready for MVP v2.0 development
**Estimated Time for Phase 1:** 2-3 hours
**Estimated Time for Phase 2:** 1-2 hours
**Estimated Time for Phase 3:** 3-4 hours
**Total MVP v2.0:** ~6-9 hours of development
