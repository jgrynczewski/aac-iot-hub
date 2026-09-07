#!/usr/bin/env python3
"""
Test Yeelight Flow Effects.

Automatically discovers bulbs and lets you test flow effects.
"""

import time
from yeelight import Bulb, Flow, RGBTransition, discover_bulbs


def test_disco(bulb):
    """1. Disco - fast color changes (party mode)."""
    print("🎵 Starting DISCO effect...")
    transitions = [
        RGBTransition(255, 0, 0, duration=500),     # Red
        RGBTransition(0, 255, 0, duration=500),     # Green
        RGBTransition(0, 0, 255, duration=500),     # Blue
        RGBTransition(255, 255, 0, duration=500),   # Yellow
        RGBTransition(255, 0, 255, duration=500),   # Magenta
        RGBTransition(0, 255, 255, duration=500),   # Cyan
    ]
    bulb.start_flow(Flow(count=0, action=Flow.actions.recover, transitions=transitions))
    print("✅ Disco started (press Ctrl+C to stop)")


def test_pulse(bulb):
    """2. Pulse - breathing effect (red)."""
    print("💓 Starting PULSE effect...")
    transitions = [
        RGBTransition(255, 0, 0, duration=1000, brightness=100),   # Bright red
        RGBTransition(255, 0, 0, duration=1000, brightness=10),    # Dim red
    ]
    bulb.start_flow(Flow(count=0, action=Flow.actions.recover, transitions=transitions))
    print("✅ Pulse started (press Ctrl+C to stop)")


def test_strobe(bulb):
    """3. Strobe - fast flashing (white)."""
    print("⚡ Starting STROBE effect...")
    transitions = [
        RGBTransition(255, 255, 255, duration=100, brightness=100),   # White bright
        RGBTransition(255, 255, 255, duration=100, brightness=1),     # White dim
    ]
    bulb.start_flow(Flow(count=0, action=Flow.actions.recover, transitions=transitions))
    print("✅ Strobe started (press Ctrl+C to stop)")


def test_rainbow(bulb):
    """4. Rainbow - smooth rainbow cycle."""
    print("🌈 Starting RAINBOW effect...")
    transitions = [
        RGBTransition(255, 0, 0, duration=1000),     # Red
        RGBTransition(255, 127, 0, duration=1000),   # Orange
        RGBTransition(255, 255, 0, duration=1000),   # Yellow
        RGBTransition(0, 255, 0, duration=1000),     # Green
        RGBTransition(0, 0, 255, duration=1000),     # Blue
        RGBTransition(75, 0, 130, duration=1000),    # Indigo
        RGBTransition(148, 0, 211, duration=1000),   # Violet
    ]
    bulb.start_flow(Flow(count=0, action=Flow.actions.recover, transitions=transitions))
    print("✅ Rainbow started (press Ctrl+C to stop)")


def test_police(bulb):
    """8. Police - red/blue alternating (alert)."""
    print("🚨 Starting POLICE effect...")
    transitions = [
        RGBTransition(255, 0, 0, duration=300, brightness=100),   # Red
        RGBTransition(0, 0, 255, duration=300, brightness=100),   # Blue
    ]
    bulb.start_flow(Flow(count=0, action=Flow.actions.recover, transitions=transitions))
    print("✅ Police started (press Ctrl+C to stop)")


def test_ocean(bulb):
    """10. Ocean - calm ocean waves."""
    print("🌊 Starting OCEAN effect...")
    transitions = [
        RGBTransition(0, 105, 148, duration=2000, brightness=70),   # Deep blue
        RGBTransition(0, 191, 255, duration=2000, brightness=90),   # Light blue
        RGBTransition(64, 224, 208, duration=2000, brightness=100), # Turquoise
        RGBTransition(0, 150, 200, duration=2000, brightness=80),   # Medium blue
    ]
    bulb.start_flow(Flow(count=0, action=Flow.actions.recover, transitions=transitions))
    print("✅ Ocean started (press Ctrl+C to stop)")


def stop_flow(bulb):
    """Stop any running flow."""
    print("🛑 Stopping flow...")
    bulb.stop_flow()
    print("✅ Flow stopped")


def main():
    print("🔍 Searching for bulbs on the network...")
    bulbs = discover_bulbs()

    if not bulbs:
        print("❌ No bulbs found. Make sure LAN Control is enabled!")
        return

    first_bulb = bulbs[0]
    bulb_ip = first_bulb.get("ip")
    print(f"✅ Found bulb: {bulb_ip}")

    bulb = Bulb(bulb_ip)

    print("\n📋 Available effects:")
    print("  1. Disco     - Fast color changes (party)")
    print("  2. Pulse     - Breathing effect (red)")
    print("  3. Strobe    - Fast flashing (white)")
    print("  4. Rainbow   - Smooth rainbow cycle")
    print("  5. Police    - Red/blue alert")
    print("  6. Ocean     - Calm ocean waves")

    choice = input("\nSelect effect (1-6): ").strip()

    effects = {
        "1": test_disco,
        "2": test_pulse,
        "3": test_strobe,
        "4": test_rainbow,
        "5": test_police,
        "6": test_ocean,
    }

    try:
        if choice in effects:
            effects[choice](bulb)
        else:
            print("❌ Invalid choice")
            return

        # Let it run
        print("\n⏳ Effect is running... Press Ctrl+C to stop\n")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n")
        stop_flow(bulb)
        print("👋 Done!")


if __name__ == "__main__":
    main()