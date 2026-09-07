# Helper Scripts

Utility scripts for manual testing and device exploration.

## Scripts

### `check_capabilities.py`
Check Yeelight bulb capabilities and supported features.

```bash
python scripts/check_capabilities.py
```

### `test_flow.py`
Interactive flow effects tester - test all 6 flow effects on real hardware.

```bash
python scripts/test_flow.py
```

### `yeelight_toggle.py`
MVP v1.0 POC - Simple bulb discovery and toggle.

```bash
python scripts/yeelight_toggle.py
```

### `shelly_toggle.py`
Shelly device POC (experimental - discovery issues present).

```bash
python scripts/shelly_toggle.py
```

## Requirements

These scripts use the same dependencies as the main project:

```bash
source .venv/bin/activate
python scripts/<script_name>.py
```