# AAC IoT Hub

**Local smart home device control hub**

## About

AAC IoT Hub is a project for local IoT device control without cloud dependency. Currently supports:

- 🔆 **Yeelight** - WiFi bulbs (Yeelight Color Bulb, Yeelight Duo, etc.)
- 🔆 **Shelly** - Shelly bulbs and devices (Shelly Bulb Duo RGBW, Gen1 and Gen2+)

## Project Status

🚧 **Early POC (Proof of Concept)** - simple scripts for testing device communication are currently available.

## Quick Start

### Install dependencies

```bash
# For Yeelight
pip install yeelight

# For Shelly
pip install zeroconf requests
```

### Run

```bash
# Yeelight control
python yeelight_toggle.py

# Shelly control
python shelly_toggle.py
```

## Device Documentation

- **[Yeelight](docs/yeelight.md)** - configuration, issues, libraries
- **[Shelly](docs/shelly.md)** - configuration, Gen1/Gen2 differences, libraries, troubleshooting

## Roadmap

Planned features:

- [ ] REST API for device control
- [ ] Containerization (Docker)
- [ ] Support for more features (colors, brightness, effects)
- [ ] Support for additional IoT device types

## Technologies

- **Python 3.12**
- **yeelight** - Yeelight bulb communication
- **zeroconf** - mDNS discovery for Shelly
- **requests** - HTTP API for Shelly

## License

MIT