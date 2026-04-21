#!/usr/bin/env python3
"""
POC sterowania żarówką Yeelight.

Automatycznie znajduje żarówki w sieci lokalnej i przełącza stan pierwszej znalezionej.
Wymaga włączonego "LAN Control" w aplikacji Yeelight Classic.
"""

from yeelight import Bulb, discover_bulbs


print("Szukam żarówek w sieci...")
bulbs = discover_bulbs()

if bulbs:
    first_bulb = bulbs[0]
    bulb_ip = first_bulb.get("ip")
    print(f"Znaleziono żarówkę: {bulb_ip}")

    bulb = Bulb(bulb_ip)
    bulb.toggle()
    print("Przełączono stan żarówki!")
else:
    print("W sieci nie ma żarówek lub nie mają włączonego LAN Control")
    exit(1)
