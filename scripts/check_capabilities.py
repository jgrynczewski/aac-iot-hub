#!/usr/bin/env python3
"""Check Yeelight bulb capabilities."""

from yeelight import Bulb, discover_bulbs

print("🔍 Searching for bulbs on the network...")
bulbs = discover_bulbs()

if not bulbs:
    print("❌ No bulbs found. Make sure LAN Control is enabled!")
    exit(1)

first_bulb = bulbs[0]
bulb_ip = first_bulb.get("ip")
print(f"✅ Found bulb: {bulb_ip}")

bulb = Bulb(bulb_ip)

print("\n📋 Getting bulb properties...")
props = bulb.get_properties()

print("\n✨ Bulb Capabilities:")
print(f"  Model: {props.get('model', 'Unknown')}")
print(f"  Firmware: {props.get('fw_ver', 'Unknown')}")
print(f"  Support: {props.get('support', 'Unknown')}")
print(f"  Power: {props.get('power', 'Unknown')}")
print(f"  Bright: {props.get('bright', 'Unknown')}")
print(f"  Color Mode: {props.get('color_mode', 'Unknown')}")
print(f"  RGB: {props.get('rgb', 'Unknown')}")
print(f"  CT: {props.get('ct', 'Unknown')}")

print("\n🔍 Full properties:")
for key, value in sorted(props.items()):
    print(f"  {key}: {value}")

# Check if 'support' contains flow-related capabilities
support = props.get('support', '')
if 'start_cf' in support:
    print("\n✅ This bulb SUPPORTS flow effects (start_cf found in support)")
else:
    print("\n❌ This bulb MAY NOT support flow effects (start_cf not in support)")
    print(f"   Supported features: {support}")