"""Tests for color and temperature presets."""
import pytest

from app.services.color_presets import (
    COLOR_PALETTE,
    TEMPERATURE_PRESETS,
    get_color_names,
    get_rgb,
    get_temperature_names,
    get_temperature,
)


class TestColorPresets:
    """Test color palette functionality."""

    def test_color_palette_has_8_colors(self):
        """Test color palette has exactly 8 colors."""
        assert len(COLOR_PALETTE) == 8

    def test_color_palette_has_required_colors(self):
        """Test color palette includes all required AAC colors."""
        required_colors = {"red", "green", "blue", "yellow", "purple", "orange", "pink", "white"}
        assert set(COLOR_PALETTE.keys()) == required_colors

    def test_color_values_are_rgb_tuples(self):
        """Test all color values are (R, G, B) tuples with valid ranges."""
        for color_name, rgb in COLOR_PALETTE.items():
            assert isinstance(rgb, tuple), f"{color_name} should be tuple"
            assert len(rgb) == 3, f"{color_name} should have 3 values"
            r, g, b = rgb
            assert 0 <= r <= 255, f"{color_name} red out of range"
            assert 0 <= g <= 255, f"{color_name} green out of range"
            assert 0 <= b <= 255, f"{color_name} blue out of range"

    def test_get_color_names_returns_sorted_list(self):
        """Test get_color_names returns alphabetically sorted list."""
        names = get_color_names()

        assert isinstance(names, list)
        assert len(names) == 8
        assert names == sorted(names)  # Check alphabetical order
        assert "blue" in names
        assert "red" in names

    def test_get_rgb_red(self):
        """Test get_rgb returns correct RGB for red."""
        rgb = get_rgb("red")
        assert rgb == (255, 0, 0)

    def test_get_rgb_green(self):
        """Test get_rgb returns correct RGB for green."""
        rgb = get_rgb("green")
        assert rgb == (0, 255, 0)

    def test_get_rgb_blue(self):
        """Test get_rgb returns correct RGB for blue."""
        rgb = get_rgb("blue")
        assert rgb == (0, 0, 255)

    def test_get_rgb_case_insensitive(self):
        """Test get_rgb works with different case variations."""
        assert get_rgb("RED") == (255, 0, 0)
        assert get_rgb("Red") == (255, 0, 0)
        assert get_rgb("rED") == (255, 0, 0)
        assert get_rgb("red") == (255, 0, 0)

    def test_get_rgb_unknown_color_raises_value_error(self):
        """Test get_rgb raises ValueError for unknown color."""
        with pytest.raises(ValueError) as exc_info:
            get_rgb("unknown_color")

        error_msg = str(exc_info.value)
        assert "Unknown color 'unknown_color'" in error_msg
        assert "Available colors:" in error_msg
        # Should list all 8 colors
        assert "red" in error_msg
        assert "blue" in error_msg

    def test_get_rgb_empty_string_raises_value_error(self):
        """Test get_rgb raises ValueError for empty string."""
        with pytest.raises(ValueError) as exc_info:
            get_rgb("")

        assert "Unknown color ''" in str(exc_info.value)


class TestTemperaturePresets:
    """Test color temperature presets functionality."""

    def test_temperature_presets_has_3_options(self):
        """Test temperature presets has exactly 3 options."""
        assert len(TEMPERATURE_PRESETS) == 3

    def test_temperature_presets_has_required_options(self):
        """Test temperature presets includes warm/neutral/cold."""
        required = {"warm", "neutral", "cold"}
        assert set(TEMPERATURE_PRESETS.keys()) == required

    def test_temperature_values_in_yeelight_range(self):
        """Test all temperature values are in Yeelight range (1700K-6500K)."""
        for name, kelvin in TEMPERATURE_PRESETS.items():
            assert 1700 <= kelvin <= 6500, f"{name} ({kelvin}K) out of Yeelight range"

    def test_get_temperature_names_returns_sorted_list(self):
        """Test get_temperature_names returns alphabetically sorted list."""
        names = get_temperature_names()

        assert isinstance(names, list)
        assert len(names) == 3
        assert names == sorted(names)  # Check alphabetical order
        assert "warm" in names
        assert "cold" in names

    def test_get_temperature_warm(self):
        """Test get_temperature returns correct Kelvin for warm."""
        temp = get_temperature("warm")
        assert temp == 2700

    def test_get_temperature_neutral(self):
        """Test get_temperature returns correct Kelvin for neutral."""
        temp = get_temperature("neutral")
        assert temp == 4000

    def test_get_temperature_cold(self):
        """Test get_temperature returns correct Kelvin for cold."""
        temp = get_temperature("cold")
        assert temp == 6500

    def test_get_temperature_case_insensitive(self):
        """Test get_temperature works with different case variations."""
        assert get_temperature("WARM") == 2700
        assert get_temperature("Warm") == 2700
        assert get_temperature("wArM") == 2700

    def test_get_temperature_unknown_preset_raises_value_error(self):
        """Test get_temperature raises ValueError for unknown preset."""
        with pytest.raises(ValueError) as exc_info:
            get_temperature("unknown_preset")

        error_msg = str(exc_info.value)
        assert "Unknown temperature preset 'unknown_preset'" in error_msg
        assert "Available presets:" in error_msg
        # Should list all 3 presets
        assert "warm" in error_msg
        assert "cold" in error_msg

    def test_get_temperature_empty_string_raises_value_error(self):
        """Test get_temperature raises ValueError for empty string."""
        with pytest.raises(ValueError) as exc_info:
            get_temperature("")

        assert "Unknown temperature preset ''" in str(exc_info.value)