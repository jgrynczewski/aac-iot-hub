#!/usr/bin/env python3
"""
Yeelight bulb control POC.

Automatically discovers bulbs on the local network and toggles the first one found.
Requires "LAN Control" enabled in the Yeelight Classic app.
"""

from yeelight import Bulb, discover_bulbs


print("Searching for bulbs on the network...")
bulbs = discover_bulbs()

if bulbs:
    first_bulb = bulbs[0]
    bulb_ip = first_bulb.get("ip")
    print(f"Found bulb: {bulb_ip}")

    bulb = Bulb(bulb_ip)
    bulb.toggle()
    print("Bulb toggled!")
else:
    print("No bulbs on the network or LAN Control is not enabled")
    exit(1)
