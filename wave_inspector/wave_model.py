"""Pure NumPy functions for generating and combining one-dimensional waves."""

from dataclasses import dataclass
import math

import numpy as np
from numpy.typing import NDArray

from wave_inspector.formulas import FormulaPreset


@dataclass(frozen=True, slots=True)
class WaveFrame:
    """Vector data for each component and the resulting composite wave."""

    base: NDArray[np.float32]
    relief: NDArray[np.float32]
    crust: NDArray[np.float32]
    composite: NDArray[np.float32]


def compute_phase(start_height: float) -> float:
    """Returns the sine phase that starts at the requested normalized height."""
    clamped_height = max(0.0, min(1.0, start_height))
    normalized_value = (clamped_height * 2.0) - 1.0
    return math.asin(normalized_value)


def _build_sine_wave(
    x_coordinates: NDArray[np.float32],
    cycles: float,
    start_height: float,
) -> NDArray[np.float32]:
    """Builds one normalized sine wave over the supplied x coordinates."""
    phase = compute_phase(start_height)
    angles = (2.0 * math.pi * cycles * x_coordinates) + phase
    wave = 0.5 + (0.5 * np.sin(angles))
    return wave.astype(np.float32)


def build_wave_frame(
    x_coordinates: NDArray[np.float32],
    formula: FormulaPreset,
    base_cycles: float,
    relief_cycles: float,
    crust_cycles: float,
) -> WaveFrame:
    """Builds the three component waves and clipped formula result."""
    from config import BASE_START, CRUST_START, RELIEF_START

    base = _build_sine_wave(
        x_coordinates,
        base_cycles,
        BASE_START,
    )
    relief = _build_sine_wave(
        x_coordinates,
        relief_cycles,
        RELIEF_START,
    )
    crust = _build_sine_wave(
        x_coordinates,
        crust_cycles,
        CRUST_START,
    )

    raw_composite = formula.func(base, relief, crust)
    composite = np.clip(raw_composite, 0.0, 1.0).astype(np.float32)

    return WaveFrame(
        base=base,
        relief=relief,
        crust=crust,
        composite=composite,
    )
