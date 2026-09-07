"""
Color and temperature presets for accessible control.

YAGNI: Start with 8 core colors for AAC interface.
Colors are designed for:
- Easy visual distinction
- Accessibility (high contrast, color-blind friendly)
- Simple button-based selection
"""

# RGB Color Palette (8 colors)
# Format: name -> (R, G, B) where each value is 0-255
COLOR_PALETTE = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
    "pink": (255, 192, 203),
    "white": (255, 255, 255),
}

# Color Temperature Presets (Kelvin)
# Yeelight supports 1700K - 6500K
# We provide 3 simple presets for AAC interface
TEMPERATURE_PRESETS = {
    "warm": 2700,      # Warm white (candle-like, relaxing)
    "neutral": 4000,   # Neutral white (natural daylight)
    "cold": 6500,      # Cool white (energizing, focused)
}


def get_color_names() -> list[str]:
    """
    Get list of available color names.

    Returns:
        Sorted list of color names
    """
    return sorted(COLOR_PALETTE.keys())


def get_rgb(color_name: str) -> tuple[int, int, int]:
    """
    Get RGB values for a color name.

    Args:
        color_name: Name of color (e.g., "red", "blue")

    Returns:
        Tuple of (R, G, B) values

    Raises:
        ValueError: If color_name is not in palette
    """
    color_name_lower = color_name.lower()
    if color_name_lower not in COLOR_PALETTE:
        available = ", ".join(sorted(COLOR_PALETTE.keys()))
        raise ValueError(
            f"Unknown color '{color_name}'. Available colors: {available}"
        )
    return COLOR_PALETTE[color_name_lower]


def get_temperature_names() -> list[str]:
    """
    Get list of available temperature preset names.

    Returns:
        Sorted list of temperature names
    """
    return sorted(TEMPERATURE_PRESETS.keys())


def get_temperature(preset_name: str) -> int:
    """
    Get temperature value for a preset name.

    Args:
        preset_name: Name of temperature preset (e.g., "warm", "cold")

    Returns:
        Temperature in Kelvin

    Raises:
        ValueError: If preset_name is not valid
    """
    preset_name_lower = preset_name.lower()
    if preset_name_lower not in TEMPERATURE_PRESETS:
        available = ", ".join(sorted(TEMPERATURE_PRESETS.keys()))
        raise ValueError(
            f"Unknown temperature preset '{preset_name}'. "
            f"Available presets: {available}"
        )
    return TEMPERATURE_PRESETS[preset_name_lower]