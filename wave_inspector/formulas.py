"""Formula presets for combining one-dimensional terrain waves."""

from dataclasses import dataclass
from typing import Callable, List

import numpy as np
from numpy.typing import NDArray

import config

WaveFunction = Callable[
    [
        NDArray[np.float32],
        NDArray[np.float32],
        NDArray[np.float32],
    ],
    NDArray[np.float32],
]


@dataclass(frozen=True, slots=True)
class FormulaPreset:
    """One named formula and its layer requirements."""

    name: str
    shorthand: str
    uses_crust: bool
    func: WaveFunction


def _master_3_layer(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Combines crust budget with detail scaled by the relief envelope."""
    relief_factor = config.MIN_RELIEF_FACTOR + (
        (1.0 - config.MIN_RELIEF_FACTOR) * relief
    )
    return (
        (config.CRUST_BUDGET * crust)
        + (config.RELIEF_BUDGET * base * relief_factor)
    )


def _global_envelope(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Scales the weighted base and crust layers by the relief envelope."""
    combined = (config.CRUST_BUDGET * crust) + (
        config.RELIEF_BUDGET * base
    )
    return relief * combined


def _volcanic_island(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Combines a dominant crust layer with two base contributions."""
    return (0.50 * crust) + (0.40 * base * relief) + (0.10 * base)


def _inverse_crust_bypass(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Lets crust values bypass or apply the relief envelope."""
    relief_mix = (crust * relief) + (1.0 - crust)
    return (
        (config.CRUST_BUDGET * crust)
        + (config.RELIEF_BUDGET * base * relief_mix)
    )


def _dynamic_lerp(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Morphs between crust and base according to the relief layer."""
    return ((1.0 - relief) * crust) + (relief * base)


def _factored_virtual_crust(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Uses relief to scale base detail with a virtual crust budget."""
    virtual_base = config.CRUST_BUDGET + (
        config.RELIEF_BUDGET * base
    )
    return relief * virtual_base


def _tibetan_high_plateau(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Creates high plateaus from a power curve and sinusoidal relief."""
    plateau = np.power(relief, 1.5) * 0.40
    relief_wave = base * (0.60 * np.sin(relief * np.pi))
    return plateau + relief_wave


def _razor_ridge(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Sharpens base detail by squaring it under the relief envelope."""
    return (relief * 0.40) + (0.60 * relief * np.square(base))


def _inverted_canyonlands(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Inverts the relief-weighted valley contribution."""
    valleys = relief * (1.0 - base)
    return (relief * 0.50) + (0.50 * (1.0 - valleys))


def _soft_natural_saturation(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Compresses base and relief detail with a smooth tanh curve."""
    return np.tanh(2.5 * relief * base) * 0.95


def _tectonic_subduction_belt(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Combines squared crust with relief-modulated base detail."""
    return (0.40 * np.square(crust)) + (
        0.60 * base * (relief * crust)
    )


def _stepped_mesa_terraces(
    base: NDArray[np.float32],
    relief: NDArray[np.float32],
    crust: NDArray[np.float32],
) -> NDArray[np.float32]:
    """Quantizes relief into terraces and adds the crust contribution."""
    terraces = np.floor(relief * 4.0) / 4.0
    return (0.35 * crust) + (0.65 * base * terraces)


FORMULA_CATALOG: List[FormulaPreset] = [
    FormulaPreset(
        name="Master 3-Layer Budgeting",
        shorthand="(0.35 * C) + (0.65 * B * (0.05 + 0.95 * R))",
        uses_crust=True,
        func=_master_3_layer,
    ),
    FormulaPreset(
        name="Global Envelope Factor",
        shorthand="R * ((0.35 * C) + (0.65 * B))",
        uses_crust=True,
        func=_global_envelope,
    ),
    FormulaPreset(
        name="Volcanic Island Override",
        shorthand="(0.50 * C) + (0.40 * B * R) + (0.10 * B)",
        uses_crust=True,
        func=_volcanic_island,
    ),
    FormulaPreset(
        name="Inverse Crust Bypass",
        shorthand="(0.35 * C) + (0.65 * B * (C * R + (1.0 - C)))",
        uses_crust=True,
        func=_inverse_crust_bypass,
    ),
    FormulaPreset(
        name="Dynamic Lerp / Morph",
        shorthand="((1.0 - R) * C) + (R * B)",
        uses_crust=True,
        func=_dynamic_lerp,
    ),
    FormulaPreset(
        name="Factored Virtual Crust",
        shorthand="R * (0.35 + 0.65 * B)",
        uses_crust=False,
        func=_factored_virtual_crust,
    ),
    FormulaPreset(
        name="Tibetan High Plateau",
        shorthand="(R**1.5 * 0.40) + (B * (0.60 * sin(R * pi)))",
        uses_crust=False,
        func=_tibetan_high_plateau,
    ),
    FormulaPreset(
        name="Razor Ridge / Granite Peaks",
        shorthand="(R * 0.40) + (0.60 * R * (B**2))",
        uses_crust=False,
        func=_razor_ridge,
    ),
    FormulaPreset(
        name="Inverted Canyonlands",
        shorthand="(R * 0.50) + (0.50 * (1.0 - R * (1.0 - B)))",
        uses_crust=False,
        func=_inverted_canyonlands,
    ),
    FormulaPreset(
        name="Soft Natural Saturation",
        shorthand="tanh(2.5 * R * B) * 0.95",
        uses_crust=False,
        func=_soft_natural_saturation,
    ),
    FormulaPreset(
        name="Tectonic Subduction Belt",
        shorthand="(0.40 * (C**2)) + (0.60 * B * (R * C))",
        uses_crust=True,
        func=_tectonic_subduction_belt,
    ),
    FormulaPreset(
        name="Stepped Mesa Terraces",
        shorthand="(0.35 * C) + (0.65 * B * (floor(R * 4.0) / 4.0))",
        uses_crust=True,
        func=_stepped_mesa_terraces,
    ),
]
