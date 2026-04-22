# Yeelight Bulb Control

## Step 1: Install library

```bash
pip install yeelight
```

## Step 2: Enable LAN Control mode on the bulb

⚠️ **IMPORTANT: You must use the Yeelight Classic app!**

The **LAN Control** option is **ONLY** available in the **[Yeelight Classic](https://home.yeelight.de/en/support/lan-control/)** app.

**The Xiaomi Home app DOES NOT have this option!** If you have the bulb added in Xiaomi Home, you must install the Yeelight Classic app separately.

**Steps:**
1. Download and install the **Yeelight Classic** app on your phone (Android/iOS)
2. Add your bulb to the Yeelight Classic app
3. Click on your bulb
4. Enter bulb settings (icon in the bottom right corner)
5. Find the **"LAN Control"** option
6. **ENABLE** this option! Without it, the script won't work.

## Step 3: Run the script

```bash
python yeelight_toggle.py
```

The script will automatically find bulbs on the network and toggle the first one found.

The bulb should toggle (on → off or off → on).

## Troubleshooting

- **"No bulbs on the network"** - Make sure that:
  - The bulb is powered on (connected to power)
  - **LAN Control** option is enabled in the Yeelight Classic app
  - Computer and bulb are on the same WiFi network

- **"BulbException: Can't connect"** - LAN Control mode is not enabled or the bulb is not responding

- **Script finds nothing despite LAN Control being enabled** - Check the computer's firewall (it may be blocking UDP broadcasts)

## yeelight library

The project uses the [python-yeelight](https://gitlab.com/stavros/python-yeelight) library for bulb communication.

**Characteristics:**
- Simple, synchronous library
- Discovery via SSDP (UDP multicast)
- Reliable communication
- Rich API (colors, effects, flows, music mode)

**Documentation:**
- [python-yeelight documentation](https://yeelight.readthedocs.io/en/latest/) - full documentation with all available methods and functions
- [Official Yeelight API specification](https://www.yeelight.com/download/Yeelight_Inter-Operation_Spec.pdf)