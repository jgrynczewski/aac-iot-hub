"""Tests for property handlers (Strategy Pattern)."""
import pytest
from unittest.mock import AsyncMock, Mock

from app.services.property_handlers import (
    PropertyHandler,
    PropertyHandlerRegistry,
    PowerHandler,
    BrightnessHandler,
    RGBHandler,
    ColorTempHandler,
    property_registry,
)


class TestPowerHandler:
    """Test PowerHandler validation and execution."""

    def test_validate_valid_states(self):
        """Test PowerHandler validates valid power states."""
        handler = PowerHandler()

        # Should not raise
        handler.validate("on")
        handler.validate("off")
        handler.validate("toggle")

    def test_validate_invalid_state(self):
        """Test PowerHandler rejects invalid power states."""
        handler = PowerHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate("invalid")

        assert "Power must be" in str(exc_info.value)
        assert "invalid" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_power_on(self):
        """Test PowerHandler executes power on command."""
        handler = PowerHandler()
        mock_adapter = Mock()
        mock_adapter.set_power = AsyncMock()

        result = await handler.handle(mock_adapter, "on")

        assert result == "on"
        mock_adapter.set_power.assert_called_once_with("on")

    @pytest.mark.asyncio
    async def test_handle_power_off(self):
        """Test PowerHandler executes power off command."""
        handler = PowerHandler()
        mock_adapter = Mock()
        mock_adapter.set_power = AsyncMock()

        result = await handler.handle(mock_adapter, "off")

        assert result == "off"
        mock_adapter.set_power.assert_called_once_with("off")

    @pytest.mark.asyncio
    async def test_handle_power_toggle(self):
        """Test PowerHandler executes toggle command."""
        handler = PowerHandler()
        mock_adapter = Mock()
        mock_adapter.set_power = AsyncMock()

        result = await handler.handle(mock_adapter, "toggle")

        assert result == "toggle"
        mock_adapter.set_power.assert_called_once_with("toggle")

    @pytest.mark.asyncio
    async def test_handle_validates_before_execution(self):
        """Test PowerHandler validates value before calling adapter."""
        handler = PowerHandler()
        mock_adapter = Mock()
        mock_adapter.set_power = AsyncMock()

        with pytest.raises(ValueError, match="Power must be"):
            await handler.handle(mock_adapter, "invalid")

        # Adapter method should NOT be called when validation fails
        mock_adapter.set_power.assert_not_called()


class TestBrightnessHandler:
    """Test BrightnessHandler validation and execution."""

    def test_validate_valid_brightness(self):
        """Test BrightnessHandler validates valid brightness values."""
        handler = BrightnessHandler()

        # Should not raise
        handler.validate(1)   # Min value
        handler.validate(50)  # Mid value
        handler.validate(100) # Max value

    def test_validate_brightness_zero(self):
        """Test BrightnessHandler rejects brightness=0 (Yeelight limitation)."""
        handler = BrightnessHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate(0)

        assert "must be 1-100" in str(exc_info.value)
        assert "doesn't support 0" in str(exc_info.value)
        assert "0" in str(exc_info.value)

    def test_validate_brightness_too_high(self):
        """Test BrightnessHandler rejects brightness > 100."""
        handler = BrightnessHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate(101)

        assert "must be 1-100" in str(exc_info.value)
        assert "101" in str(exc_info.value)

    def test_validate_brightness_negative(self):
        """Test BrightnessHandler rejects negative brightness."""
        handler = BrightnessHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate(-10)

        assert "must be 1-100" in str(exc_info.value)

    def test_validate_brightness_wrong_type_string(self):
        """Test BrightnessHandler rejects string type."""
        handler = BrightnessHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate("50")

        assert "must be an integer" in str(exc_info.value)
        assert "str" in str(exc_info.value)

    def test_validate_brightness_wrong_type_float(self):
        """Test BrightnessHandler rejects float type."""
        handler = BrightnessHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate(50.5)

        assert "must be an integer" in str(exc_info.value)
        assert "float" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_brightness_50(self):
        """Test BrightnessHandler executes brightness=50 command."""
        handler = BrightnessHandler()
        mock_adapter = Mock()
        mock_adapter.set_brightness = AsyncMock()

        result = await handler.handle(mock_adapter, 50)

        assert result == 50
        mock_adapter.set_brightness.assert_called_once_with(50)

    @pytest.mark.asyncio
    async def test_handle_brightness_1(self):
        """Test BrightnessHandler executes brightness=1 (min)."""
        handler = BrightnessHandler()
        mock_adapter = Mock()
        mock_adapter.set_brightness = AsyncMock()

        result = await handler.handle(mock_adapter, 1)

        assert result == 1
        mock_adapter.set_brightness.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_handle_brightness_100(self):
        """Test BrightnessHandler executes brightness=100 (max)."""
        handler = BrightnessHandler()
        mock_adapter = Mock()
        mock_adapter.set_brightness = AsyncMock()

        result = await handler.handle(mock_adapter, 100)

        assert result == 100
        mock_adapter.set_brightness.assert_called_once_with(100)

    @pytest.mark.asyncio
    async def test_handle_validates_before_execution(self):
        """Test BrightnessHandler validates value before calling adapter."""
        handler = BrightnessHandler()
        mock_adapter = Mock()
        mock_adapter.set_brightness = AsyncMock()

        with pytest.raises(ValueError, match="must be 1-100"):
            await handler.handle(mock_adapter, 0)

        # Adapter method should NOT be called when validation fails
        mock_adapter.set_brightness.assert_not_called()


class TestRGBHandler:
    """Test RGBHandler validation and execution."""

    def test_validate_valid_color_names(self):
        """Test RGBHandler validates valid color names from palette."""
        handler = RGBHandler()

        # Should not raise for all 8 palette colors
        handler.validate("red")
        handler.validate("green")
        handler.validate("blue")
        handler.validate("yellow")
        handler.validate("purple")
        handler.validate("orange")
        handler.validate("pink")
        handler.validate("white")

    def test_validate_color_case_insensitive(self):
        """Test RGBHandler validates colors case-insensitively."""
        handler = RGBHandler()

        # Should not raise
        handler.validate("RED")
        handler.validate("Red")
        handler.validate("rED")

    def test_validate_invalid_color_raises_value_error(self):
        """Test RGBHandler rejects invalid color names."""
        handler = RGBHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate("invalid_color")

        error_msg = str(exc_info.value)
        assert "Unknown color 'invalid_color'" in error_msg
        assert "Available colors:" in error_msg

    def test_validate_wrong_type_integer(self):
        """Test RGBHandler rejects integer type."""
        handler = RGBHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate(123)

        assert "must be a string" in str(exc_info.value)
        assert "int" in str(exc_info.value)

    def test_validate_wrong_type_list(self):
        """Test RGBHandler rejects list type."""
        handler = RGBHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate([255, 0, 0])

        assert "must be a string" in str(exc_info.value)
        assert "list" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_red_color(self):
        """Test RGBHandler executes red color command."""
        handler = RGBHandler()
        mock_adapter = Mock()
        mock_adapter.set_rgb = AsyncMock()

        result = await handler.handle(mock_adapter, "red")

        assert result == "red"
        mock_adapter.set_rgb.assert_called_once_with(255, 0, 0)

    @pytest.mark.asyncio
    async def test_handle_green_color(self):
        """Test RGBHandler executes green color command."""
        handler = RGBHandler()
        mock_adapter = Mock()
        mock_adapter.set_rgb = AsyncMock()

        result = await handler.handle(mock_adapter, "green")

        assert result == "green"
        mock_adapter.set_rgb.assert_called_once_with(0, 255, 0)

    @pytest.mark.asyncio
    async def test_handle_blue_color(self):
        """Test RGBHandler executes blue color command."""
        handler = RGBHandler()
        mock_adapter = Mock()
        mock_adapter.set_rgb = AsyncMock()

        result = await handler.handle(mock_adapter, "blue")

        assert result == "blue"
        mock_adapter.set_rgb.assert_called_once_with(0, 0, 255)

    @pytest.mark.asyncio
    async def test_handle_purple_color(self):
        """Test RGBHandler executes purple color command."""
        handler = RGBHandler()
        mock_adapter = Mock()
        mock_adapter.set_rgb = AsyncMock()

        result = await handler.handle(mock_adapter, "purple")

        assert result == "purple"
        mock_adapter.set_rgb.assert_called_once_with(128, 0, 128)

    @pytest.mark.asyncio
    async def test_handle_validates_before_execution(self):
        """Test RGBHandler validates color before calling adapter."""
        handler = RGBHandler()
        mock_adapter = Mock()
        mock_adapter.set_rgb = AsyncMock()

        with pytest.raises(ValueError, match="Unknown color"):
            await handler.handle(mock_adapter, "invalid_color")

        # Adapter method should NOT be called when validation fails
        mock_adapter.set_rgb.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_case_insensitive(self):
        """Test RGBHandler handles colors case-insensitively."""
        handler = RGBHandler()
        mock_adapter = Mock()
        mock_adapter.set_rgb = AsyncMock()

        result = await handler.handle(mock_adapter, "RED")

        assert result == "RED"
        mock_adapter.set_rgb.assert_called_once_with(255, 0, 0)


class TestColorTempHandler:
    """Test ColorTempHandler validation and execution."""

    def test_validate_valid_temperature_names(self):
        """Test ColorTempHandler validates valid temperature presets."""
        handler = ColorTempHandler()

        # Should not raise for all 3 temperature presets
        handler.validate("warm")
        handler.validate("neutral")
        handler.validate("cold")

    def test_validate_temperature_case_insensitive(self):
        """Test ColorTempHandler validates temperatures case-insensitively."""
        handler = ColorTempHandler()

        # Should not raise
        handler.validate("WARM")
        handler.validate("Warm")
        handler.validate("wArM")

    def test_validate_invalid_temperature_raises_value_error(self):
        """Test ColorTempHandler rejects invalid temperature names."""
        handler = ColorTempHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate("invalid_temp")

        error_msg = str(exc_info.value)
        assert "Unknown temperature preset 'invalid_temp'" in error_msg
        assert "Available presets:" in error_msg

    def test_validate_wrong_type_integer(self):
        """Test ColorTempHandler rejects integer type."""
        handler = ColorTempHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate(2700)

        assert "must be a string" in str(exc_info.value)
        assert "int" in str(exc_info.value)

    def test_validate_wrong_type_list(self):
        """Test ColorTempHandler rejects list type."""
        handler = ColorTempHandler()

        with pytest.raises(ValueError) as exc_info:
            handler.validate(["warm"])

        assert "must be a string" in str(exc_info.value)
        assert "list" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handle_warm_temperature(self):
        """Test ColorTempHandler executes warm temperature command."""
        handler = ColorTempHandler()
        mock_adapter = Mock()
        mock_adapter.set_color_temp = AsyncMock()

        result = await handler.handle(mock_adapter, "warm")

        assert result == "warm"
        mock_adapter.set_color_temp.assert_called_once_with(2700)

    @pytest.mark.asyncio
    async def test_handle_neutral_temperature(self):
        """Test ColorTempHandler executes neutral temperature command."""
        handler = ColorTempHandler()
        mock_adapter = Mock()
        mock_adapter.set_color_temp = AsyncMock()

        result = await handler.handle(mock_adapter, "neutral")

        assert result == "neutral"
        mock_adapter.set_color_temp.assert_called_once_with(4000)

    @pytest.mark.asyncio
    async def test_handle_cold_temperature(self):
        """Test ColorTempHandler executes cold temperature command."""
        handler = ColorTempHandler()
        mock_adapter = Mock()
        mock_adapter.set_color_temp = AsyncMock()

        result = await handler.handle(mock_adapter, "cold")

        assert result == "cold"
        mock_adapter.set_color_temp.assert_called_once_with(6500)

    @pytest.mark.asyncio
    async def test_handle_validates_before_execution(self):
        """Test ColorTempHandler validates temperature before calling adapter."""
        handler = ColorTempHandler()
        mock_adapter = Mock()
        mock_adapter.set_color_temp = AsyncMock()

        with pytest.raises(ValueError, match="Unknown temperature preset"):
            await handler.handle(mock_adapter, "invalid_temp")

        # Adapter method should NOT be called when validation fails
        mock_adapter.set_color_temp.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_case_insensitive(self):
        """Test ColorTempHandler handles temperatures case-insensitively."""
        handler = ColorTempHandler()
        mock_adapter = Mock()
        mock_adapter.set_color_temp = AsyncMock()

        result = await handler.handle(mock_adapter, "WARM")

        assert result == "WARM"
        mock_adapter.set_color_temp.assert_called_once_with(2700)


class TestPropertyHandlerRegistry:
    """Test PropertyHandlerRegistry register/get/has functionality."""

    def test_register_and_get(self):
        """Test registering and retrieving a handler."""
        registry = PropertyHandlerRegistry()
        handler = PowerHandler()

        registry.register("test_prop", handler)

        retrieved = registry.get("test_prop")
        assert retrieved == handler

    def test_get_unknown_property(self):
        """Test getting unknown property raises ValueError with supported list."""
        registry = PropertyHandlerRegistry()
        registry.register("power", PowerHandler())

        with pytest.raises(ValueError) as exc_info:
            registry.get("nonexistent")

        error_msg = str(exc_info.value)
        assert "Unknown property 'nonexistent'" in error_msg
        assert "Supported properties: power" in error_msg

    def test_get_unknown_property_shows_all_supported(self):
        """Test error message shows all supported properties."""
        registry = PropertyHandlerRegistry()
        registry.register("power", PowerHandler())
        registry.register("brightness", BrightnessHandler())

        with pytest.raises(ValueError) as exc_info:
            registry.get("unknown")

        error_msg = str(exc_info.value)
        assert "brightness" in error_msg
        assert "power" in error_msg

    def test_has_property_registered(self):
        """Test has() returns True for registered property."""
        registry = PropertyHandlerRegistry()
        handler = PowerHandler()

        registry.register("test", handler)

        assert registry.has("test") is True

    def test_has_property_not_registered(self):
        """Test has() returns False for unregistered property."""
        registry = PropertyHandlerRegistry()

        assert registry.has("nonexistent") is False

    def test_get_all_handlers(self):
        """Test get_all() returns all registered handlers."""
        registry = PropertyHandlerRegistry()
        power_handler = PowerHandler()
        brightness_handler = BrightnessHandler()

        registry.register("power", power_handler)
        registry.register("brightness", brightness_handler)

        all_handlers = registry.get_all()

        assert len(all_handlers) == 2
        assert all_handlers["power"] == power_handler
        assert all_handlers["brightness"] == brightness_handler

    def test_get_all_returns_copy(self):
        """Test get_all() returns a copy (not direct reference)."""
        registry = PropertyHandlerRegistry()
        registry.register("power", PowerHandler())

        all_handlers = registry.get_all()
        all_handlers["fake"] = Mock()  # Modify copy

        # Original registry should be unchanged
        assert not registry.has("fake")

    def test_get_supported_properties(self):
        """Test get_supported_properties() returns sorted list."""
        registry = PropertyHandlerRegistry()
        registry.register("power", PowerHandler())
        registry.register("brightness", BrightnessHandler())

        supported = registry.get_supported_properties()

        assert supported == ["brightness", "power"]  # Sorted alphabetically


class TestGlobalPropertyRegistry:
    """Test global property_registry instance."""

    def test_global_registry_has_power(self):
        """Test global registry has PowerHandler registered."""
        assert property_registry.has("power")
        handler = property_registry.get("power")
        assert isinstance(handler, PowerHandler)

    def test_global_registry_has_brightness(self):
        """Test global registry has BrightnessHandler registered."""
        assert property_registry.has("brightness")
        handler = property_registry.get("brightness")
        assert isinstance(handler, BrightnessHandler)

    def test_global_registry_has_color(self):
        """Test global registry has RGBHandler registered."""
        assert property_registry.has("color")
        handler = property_registry.get("color")
        assert isinstance(handler, RGBHandler)

    def test_global_registry_has_temperature(self):
        """Test global registry has ColorTempHandler registered."""
        assert property_registry.has("temperature")
        handler = property_registry.get("temperature")
        assert isinstance(handler, ColorTempHandler)

    def test_global_registry_supported_properties(self):
        """Test global registry reports correct supported properties."""
        supported = property_registry.get_supported_properties()

        assert "power" in supported
        assert "brightness" in supported
        assert "color" in supported
        assert "temperature" in supported
        assert len(supported) >= 4  # At least power + brightness + color + temperature