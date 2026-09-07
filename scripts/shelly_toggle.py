#!/usr/bin/env python3
"""
Shelly DUO RGBW bulb control POC.

Automatically discovers Shelly bulbs on the local network (via mDNS) and toggles the first one found.
"""

import requests
from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
import time


class ShellyListener(ServiceListener):
    """Listener for detecting Shelly devices via mDNS."""

    def __init__(self):
        self.devices = []

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        """Callback invoked when a new device is found."""
        # Gen1 Shelly announces as _http._tcp.local., so filter by name
        if '_http._tcp' in type_ and 'shelly' not in name.lower():
            return

        info = zc.get_service_info(type_, name)
        if info:
            # Extract IP address from info
            addresses = [addr for addr in info.parsed_addresses()]
            if addresses:
                device_info = {
                    'name': name,
                    'ip': addresses[0],
                    'port': info.port,
                    'type': type_
                }
                self.devices.append(device_info)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        pass


def discover_shelly_devices(timeout=5):
    """
    Discovers Shelly devices on the local network via mDNS.

    Supports both generations:
    - Gen1 (e.g. Shelly Bulb Duo, esp8266): announces as _http._tcp.local.
    - Gen2+ (Plus/Pro, esp32): announces as _shelly._tcp.local.
    """
    zeroconf = Zeroconf()
    listener = ShellyListener()

    # Scan both service types as different generations use different protocols
    browser_gen2 = ServiceBrowser(zeroconf, "_shelly._tcp.local.", listener)  # Gen2+
    browser_gen1 = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)    # Gen1

    print(f"Searching for Shelly devices on the network (for {timeout}s)...")
    time.sleep(timeout)

    zeroconf.close()
    return listener.devices


def toggle_shelly_bulb(ip):
    """
    Toggles Shelly bulb state via HTTP API.

    HTTP API for Shelly:
    - Gen1: http://IP/color/0?turn=toggle (/color endpoint for RGBW)
    - Gen2+: http://IP/rpc/Light.Toggle (RPC-style API)

    This function uses Gen1 API (for Shelly Bulb Duo RGBW).
    """
    url = f"http://{ip}/color/0?turn=toggle"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Communication error with bulb: {e}")
        return False


if __name__ == "__main__":
    devices = discover_shelly_devices(timeout=20)
    print(devices)

    if devices:
        first_device = devices[0]
        device_ip = first_device['ip']
        device_name = first_device['name']
        print(f"Found device: {device_name} ({device_ip})")

        if toggle_shelly_bulb(device_ip):
            print("Bulb toggled!")
        else:
            print("Failed to toggle bulb")
            exit(1)
    else:
        print("No Shelly devices found on the network")
        exit(1)
