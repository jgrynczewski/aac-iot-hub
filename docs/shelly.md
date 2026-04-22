# Shelly DUO RGBW Control

## Step 1: Install dependencies

```bash
pip install zeroconf requests
```

## Step 2: Bulb setup

### Initial WiFi Configuration

On first power-on, the bulb creates its own WiFi network (AP mode) with SSID like `shellycolorbulb-XXXXXX`.

You need to configure WiFi credentials to connect the bulb to your network:

**Method 1: Using Shelly Smart Control app (recommended)**
1. Download [**Shelly Smart Control**](https://www.shelly.com/shelly-smart-control-app) app (Android/iOS)
2. In the app, choose "Add Device"
3. The app will connect to the bulb's WiFi network automatically
4. Enter your WiFi network name (SSID) and password
5. The bulb will connect to your WiFi network

**Method 2: Using web browser**
1. Connect to the bulb's WiFi network (`shellycolorbulb-XXXXXX`)
2. Open browser and go to `http://192.168.33.1`
3. Configure your WiFi credentials in the web interface
4. The bulb will connect to your WiFi network

**Unlike Yeelight, Shelly devices have HTTP API enabled by default** - after WiFi configuration, no additional app settings are required for local control!

⚠️ **Connection issues?**

If the bulb was previously used or you're having connection problems, **perform a factory reset**:

1. Turn the bulb on and off **5 times** (each power-on for ~1-2 seconds)
2. After the 5th power-on, the bulb should blink - this indicates pairing mode
3. Reconnect the bulb to WiFi (via Shelly app or other method)

Detailed reset instructions: [How to factory reset Shelly Duo](https://shelly-forum.com/thread/22793-how-to-factory-reset-shelly-duo/)

## Step 3: Run the script

```bash
python shelly_toggle.py
```

The script will automatically discover Shelly devices on the local network (via mDNS) and toggle the first one found.

⚠️ **Discovery can be unstable** - sometimes requires multiple attempts (works ~1 in 3-5 runs). This is a known issue with mDNS discovery for Gen1 devices.

## Shelly Generation Differences

### Gen1 (e.g. Shelly Bulb Duo RGBW)
- Chip: ESP8266
- mDNS: announces as `_http._tcp.local.`
- API: REST HTTP (e.g. `/color/0?turn=toggle`)
- Discovery: less stable (broadcasts don't always arrive)

### Gen2+ (Plus/Pro)
- Chip: ESP32
- mDNS: announces as `_shelly._tcp.local.`
- API: RPC-style (e.g. `/rpc/Light.Toggle`)
- Discovery: more stable

The script supports both generations.

## Troubleshooting

- **Script doesn't find the bulb** - This is normal for Gen1, try running 2-3 times
  - Alternative: increase timeout in code (default 5s)
  - Ensure computer and bulb are on the same WiFi network

- **Discovery always returns []** - Check:
  - Bulb works in Shelly app (if installed)
  - Firewall isn't blocking mDNS (UDP port 5353)
  - Try factory reset of the bulb

- **Error during toggle** - Device was discovered but doesn't respond to HTTP API
  - Verify IP is correct
  - Try manually: `curl http://BULB_IP/shelly`

## Python Libraries Overview for Shelly

### 1. **pyShelly**
- **PyPI:** [pyShelly](https://pypi.org/project/pyShelly/)
- **GitHub:** [StyraHem/pyShelly](https://github.com/StyraHem/pyShelly)
- **Type:** Event-driven (callback-based)
- **Protocol:** CoAP for auto-discovery + MQTT
- **Pros:** Auto-discovery via CoAP, support for 40+ models
- **Cons:** Callback-based pattern (more complex), requires asyncio/event loop
- **Use case:** Home Assistant integrations, Telldus

### 2. **aioshelly**
- **PyPI:** [aioshelly](https://pypi.org/project/aioshelly/)
- **GitHub:** [home-assistant-libs/aioshelly](https://github.com/home-assistant-libs/aioshelly)
- **Type:** Async (asyncio)
- **Protocol:** HTTP API + WebSocket (for Gen2+)
- **Pros:** Official Home Assistant library, full Gen1 and Gen2+ support, actively maintained
- **Cons:** Requires async/await (asyncio)
- **Use case:** Best choice for modern APIs (FastAPI, aiohttp)

### 3. **ShellyPy**
- **PyPI:** [ShellyPy](https://pypi.org/project/ShellyPy/)
- **GitHub:** [Jan200101/ShellyPy](https://github.com/Jan200101/ShellyPy)
- **Type:** Synchronous
- **Protocol:** HTTP API wrapper
- **Pros:** Simple HTTP API wrapper, synchronous
- **Cons:** **No auto-discovery** (must know IP), basic functionality
- **Use case:** Simple scripts when you know device IP

### 4. **Custom implementation (as in this project)**
- **Type:** Synchronous
- **Protocol:** mDNS (zeroconf) + raw HTTP API (requests)
- **Pros:** Full control, minimal dependencies, easy debugging
- **Cons:** Need to handle edge cases yourself, fewer features
- **Use case:** POC, learning, simple projects

## Recommendations

- **For POC/simple scripts:** Custom implementation or ShellyPy
- **For production API:** aioshelly (with FastAPI)
- **For Home Assistant:** aioshelly (official integration)

## Shelly API Documentation

- [Shelly API Documentation](https://shelly-api-docs.shelly.cloud/) - official HTTP API documentation
- [Gen1 API Reference](https://shelly-api-docs.shelly.cloud/gen1/) - Gen1 devices documentation
- [Gen2 API Reference](https://shelly-api-docs.shelly.cloud/gen2/) - Gen2+ devices documentation
- [mDNS Discovery](https://shelly-api-docs.shelly.cloud/gen2/General/mDNS/) - how mDNS discovery works