# Future Device Support - Research

This document analyzes potential IoT devices that could be integrated into AAC IoT Hub beyond smart bulbs.

**Use Case:** Remote-controlled robot with camera for home monitoring and mobility assistance (e.g., for wheelchair users who want to navigate and observe their home remotely).

## 1. ESP32-CAM + Robot Chassis (Best DIY Option)

**Hardware:**
- ESP32-CAM board (~$3-5) - microcontroller with camera and WiFi
- 2WD/4WD robot chassis (~$10-20)
- Motor driver (L298N ~$2-3)
- Batteries and wiring (~$10)

**Total Cost:** ~$25-40 USD (~150-250 PLN)

**Programming:**
- Python/MicroPython or Arduino C++
- Full control over functionality
- Abundant tutorials and community support

**API Example:**
```python
POST /api/v1/devices/{robot_id}/move
{
  "direction": "forward",  # forward, backward, left, right, stop
  "speed": 50              # 0-100
}

GET /api/v1/devices/{robot_id}/camera/stream
# Returns MJPEG or WebRTC video stream

POST /api/v1/devices/{robot_id}/camera/pan
{
  "angle": 45  # Pan camera servo
}
```

**Integration with AAC IoT Hub:**
```python
# app/services/adapters/esp32_robot_adapter.py
class ESP32RobotAdapter(DeviceAdapter):
    device_type = "robot"

    async def get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            operations=["move", "camera_stream", "camera_pan"],
            supports_power=True,
            supports_movement=True,
            supports_camera=True
        )

    async def move(self, direction: str, speed: int):
        await self._http_client.post(
            f"http://{self.ip}/move",
            json={"direction": direction, "speed": speed}
        )

    async def get_camera_stream_url(self) -> str:
        return f"http://{self.ip}:81/stream"
```

**Pros:**
- Cheapest option
- Full customization
- Local control (no cloud)
- Can add sensors (ultrasonic, PIR, etc.)

**Cons:**
- Requires hardware assembly
- Need to write ESP32 firmware
- Medium difficulty

**Difficulty:** Medium

---

## 2. DJI Tello EDU Drone (Ready-to-Use with SDK)

**Hardware:**
- DJI Tello EDU drone (~$100-120 USD / 500-700 PLN)

**Programming:**
- Official Python SDK (`djitellopy` library)
- Stable flight controller
- 720p video streaming
- 13-minute flight time

**Code Example:**
```python
from djitellopy import Tello

tello = Tello()
tello.connect()
tello.takeoff()
tello.move_forward(100)  # cm
tello.rotate_clockwise(90)
frame_reader = tello.get_frame_read()
frame = frame_reader.frame  # OpenCV image
tello.land()
```

**API Integration:**
```python
# app/services/adapters/tello_adapter.py
class TelloAdapter(DeviceAdapter):
    device_type = "drone"

    async def get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            operations=["takeoff", "land", "move", "rotate", "flip", "camera_stream"],
            supports_power=True,
            supports_movement=True,
            supports_camera=True
        )
```

**Pros:**
- Works out of the box
- Excellent Python SDK
- Stable flight
- Better range than ground robots
- Can access hard-to-reach places

**Cons:**
- More expensive
- Noisy
- Limited battery life (13 min)
- Requires open space

**Difficulty:** Easy

---

## 3. Raspberry Pi + Robot Chassis + Pi Camera

**Hardware:**
- Raspberry Pi Zero 2W (~$20 / 150 PLN) or Pi 4
- Pi Camera Module (~$15 / 100 PLN)
- Robot chassis (~$15 / 100 PLN)
- Motor driver, batteries, components (~$15 / 100 PLN)

**Total Cost:** ~$65 USD (~400-600 PLN)

**Programming:**
- Full Linux environment
- Python with all libraries (OpenCV, TensorFlow, etc.)
- GPIO for motor control
- PiCamera for video streaming

**Example:**
```python
import picamera
import RPi.GPIO as GPIO
from flask import Flask, Response

app = Flask(__name__)

# Motor control via GPIO
def move_forward():
    GPIO.output(MOTOR_LEFT_FWD, GPIO.HIGH)
    GPIO.output(MOTOR_RIGHT_FWD, GPIO.HIGH)

# Camera streaming
@app.route('/camera/stream')
def stream():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )
```

**Pros:**
- Most flexible platform
- Full Linux, all tools available
- Can add: microphone, speaker, sensors, AI/ML
- Easy to extend functionality
- Well documented

**Cons:**
- Requires assembly
- More expensive than ESP32
- Higher power consumption

**Difficulty:** Medium

---

## 4. Ready-Made Educational Platforms

### Anki Vector / Cozmo
- Ready robot with camera
- Python SDK available
- **Issue:** Anki bankrupted, but SDK still works
- If found used: ~$100-200

### LEGO Mindstorms / SPIKE
- Python API
- Easy building and programming
- Expensive (~$300-400 / 1500-2000 PLN)
- Educational focus

---

## 5. Other Easily Programmable IoT Devices

### Shelly (Already in Project)
**Devices:**
- Relays, switches, dimmers, sensors
- HTTP REST API
- ~$10-30 per device (50-150 PLN)

**Use cases:**
- Door locks
- Garage doors
- Lights (non-Yeelight)
- Power monitoring

### Tasmota/ESPHome Devices
**What:** WiFi devices flashed with open-source firmware
- REST API / MQTT support
- Very cheap (~$5-20 / 20-100 PLN)
- Plugs, switches, sensors

**Example devices:**
- Sonoff switches
- Generic ESP8266/ESP32 devices

### Xiaomi/Aqara (Zigbee)
**Devices:**
- Motion sensors
- Door/window sensors
- Temperature/humidity sensors
- ~$6-15 per sensor (30-80 PLN)

**Requirements:**
- Zigbee gateway needed
- REST API via gateway

### IP Cameras (Wyze, TP-Link Tapo, etc.)
**Devices:**
- Wyze Cam (~$20-30 / 100-200 PLN)
- TP-Link Tapo C200 (~$30 / 150 PLN)

**Programming:**
- Unofficial Python SDKs available
- RTSP/ONVIF protocols
- Local network streaming

---

## Recommended Solution for Wheelchair Mobility Use Case

### Option 1: Budget (~$150-250 PLN)
**ESP32-CAM + Robot Chassis**

**Best for:** Tight budget, DIY enthusiast, learning experience

**Requirements:**
- Basic soldering skills
- Arduino/MicroPython programming
- 2-3 days assembly/setup

### Option 2: Ready-to-Use (~$500-800 PLN)
**DJI Tello EDU**

**Best for:** Quick deployment, no assembly, aerial perspective

**Pros:**
- Python SDK works immediately
- Better range than ground robot
- Can fly over obstacles

**Cons:**
- Noise
- 13-minute battery life
- Requires open space

### Option 3: Most Flexible (~$400-600 PLN)
**Raspberry Pi Zero 2W + Robot Chassis + Pi Camera**

**Best for:** Maximum flexibility, extensibility, professional result

**Can add later:**
- Voice control (microphone)
- Speaker for two-way communication
- AI object detection (TensorFlow Lite)
- Ultrasonic sensors for collision avoidance
- IMU for stability

---

## Integration Architecture with AAC IoT Hub

All these devices would integrate naturally into the existing unified API:

```python
# Unified device control
POST /api/v1/devices/{device_id}/power
POST /api/v1/devices/{device_id}/move      # New operation for robots
GET  /api/v1/devices/{device_id}/camera    # New operation for cameras
GET  /api/v1/devices/{device_id}/capabilities

# Device adapter pattern
class DeviceAdapter(ABC):
    @abstractmethod
    async def get_capabilities(self) -> DeviceCapabilities:
        pass

    # Optional operations based on capabilities
    async def move(self, direction: str, speed: int):
        raise NotImplementedError(f"{self.type} doesn't support movement")

    async def get_camera_stream(self):
        raise NotImplementedError(f"{self.type} doesn't support camera")
```

**Benefits:**
- Single API for bulbs, robots, cameras, sensors
- Clients query capabilities to build dynamic UI
- Easy to add new device types
- Local control, no cloud dependency

---

## Next Steps

1. **Prototype Phase:** Start with ESP32-CAM POC
   - Similar to existing `yeelight_toggle.py` and `shelly_toggle.py`
   - Create `esp32_robot_toggle.py`
   - Document in `docs/esp32-robot.md`

2. **ADR:** If chosen, create ADR-004 for robot device selection

3. **Implementation:** Add to roadmap after current Yeelight MVP complete

4. **Web UI:** Could show:
   - Device grid (bulbs, robots, sensors)
   - Live camera streams
   - Movement controls (virtual joystick)
   - Device capabilities automatically rendered