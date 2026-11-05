"""Mutable runtime selections and cycle values for the inspector."""

from dataclasses import dataclass

import config


@dataclass(slots=True)
class InspectorState:
    """Tracks the selected formula, focused layer, and current frequencies."""

    active_formula_index: int = 0
    selected_panel_index: int = 0
    base_cycles: float = config.DEFAULT_BASE_CYCLES
    relief_cycles: float = config.DEFAULT_RELIEF_CYCLES
    crust_cycles: float = config.DEFAULT_CRUST_CYCLES
