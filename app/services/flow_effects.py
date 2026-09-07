"""
Flow effects for Yeelight devices.

Predefined light animations for AAC interface.
Each effect runs in a loop until stopped.
"""

from yeelight import Flow, RGBTransition
from typing import List, Tuple


def _create_transitions(transitions_spec: List[Tuple]) -> List[RGBTransition]:
    """
    Create RGBTransition list from specification.

    Args:
        transitions_spec: List of (r, g, b, duration, brightness) tuples
                         brightness is optional

    Returns:
        List of RGBTransition objects
    """
    transitions = []
    for spec in transitions_spec:
        if len(spec) == 4:
            r, g, b, duration = spec
            transitions.append(RGBTransition(r, g, b, duration=duration))
        elif len(spec) == 5:
            r, g, b, duration, brightness = spec
            transitions.append(RGBTransition(r, g, b, duration=duration, brightness=brightness))
    return transitions


# Effect definitions
# Each effect is a list of (R, G, B, duration_ms, [brightness]) tuples

DISCO_TRANSITIONS = [
    (255, 0, 0, 500),       # Red
    (0, 255, 0, 500),       # Green
    (0, 0, 255, 500),       # Blue
    (255, 255, 0, 500),     # Yellow
    (255, 0, 255, 500),     # Magenta
    (0, 255, 255, 500),     # Cyan
]

PULSE_TRANSITIONS = [
    (255, 0, 0, 1000, 100),  # Bright red
    (255, 0, 0, 1000, 10),   # Dim red
]

STROBE_TRANSITIONS = [
    (255, 255, 255, 100, 100),  # White bright
    (255, 255, 255, 100, 1),    # White dim
]

RAINBOW_TRANSITIONS = [
    (255, 0, 0, 1000),       # Red
    (255, 127, 0, 1000),     # Orange
    (255, 255, 0, 1000),     # Yellow
    (0, 255, 0, 1000),       # Green
    (0, 0, 255, 1000),       # Blue
    (75, 0, 130, 1000),      # Indigo
    (148, 0, 211, 1000),     # Violet
]

POLICE_TRANSITIONS = [
    (255, 0, 0, 300, 100),   # Red
    (0, 0, 255, 300, 100),   # Blue
]

OCEAN_TRANSITIONS = [
    (0, 105, 148, 2000, 70),    # Deep blue
    (0, 191, 255, 2000, 90),    # Light blue
    (64, 224, 208, 2000, 100),  # Turquoise
    (0, 150, 200, 2000, 80),    # Medium blue
]

# Registry of all available effects
FLOW_EFFECTS = {
    "disco": DISCO_TRANSITIONS,
    "pulse": PULSE_TRANSITIONS,
    "strobe": STROBE_TRANSITIONS,
    "rainbow": RAINBOW_TRANSITIONS,
    "police": POLICE_TRANSITIONS,
    "ocean": OCEAN_TRANSITIONS,
}


def get_effect_names() -> List[str]:
    """
    Get list of available effect names.

    Returns:
        Sorted list of effect names
    """
    return sorted(FLOW_EFFECTS.keys())


def create_flow(effect_name: str) -> Flow:
    """
    Create a Flow object for the given effect.

    Args:
        effect_name: Name of the effect (e.g., "disco", "rainbow")

    Returns:
        Flow object configured for infinite loop

    Raises:
        ValueError: If effect_name is not valid
    """
    effect_name_lower = effect_name.lower()
    if effect_name_lower not in FLOW_EFFECTS:
        available = ", ".join(sorted(FLOW_EFFECTS.keys()))
        raise ValueError(
            f"Unknown effect '{effect_name}'. "
            f"Available effects: {available}"
        )

    transitions_spec = FLOW_EFFECTS[effect_name_lower]
    transitions = _create_transitions(transitions_spec)

    return Flow(
        count=0,  # Loop forever
        action=Flow.actions.recover,  # Return to previous state when stopped
        transitions=transitions
    )