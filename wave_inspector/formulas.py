"""Formula presets and dual-projection specifications for wave synthesis."""

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
    """Specification model holding formula metadata, layers, and logic."""

    name: str
    shorthand: str
    uses_relief: bool
    uses_crust: bool
    func: WaveFunction


@dataclass(frozen=True, slots=True)
class Preset2D:
    """2D spatial preset specification binding projection geometry."""

    name: str
    shorthand: str
    uses_base: bool
    uses_relief: bool
    uses_crust: bool
    func: WaveFunction
    composite_index: int


def _solo_base(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Returns base wave component."""
    return b


def _solo_relief(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Returns relief multiplier component."""
    return r


def _solo_crust(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Returns continental crust component."""
    return c


def _master_3_layer(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Calculates budgeted 3-layer additive elevation."""
    rf = config.MIN_RELIEF_FACTOR + ((1.0 - config.MIN_RELIEF_FACTOR) * r)
    return (config.CRUST_BUDGET * c) + (config.RELIEF_BUDGET * b * rf)


def _global_envelope(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Scales crust and base elevation inside a global relief envelope."""
    return r * ((config.CRUST_BUDGET * c) + (config.RELIEF_BUDGET * b))


def _volcanic_island(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Calculates tectonic dome with dual-stage detail modulation."""
    return (0.50 * c) + (0.40 * b * r) + (0.10 * b)


def _inverse_crust_bypass(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Blends high relief into shoreline lowlands."""
    rmix = (c * r) + (1.0 - c)
    return (config.CRUST_BUDGET * c) + (config.RELIEF_BUDGET * b * rmix)


def _dynamic_lerp(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Blends linearly between crust and detail via relief factor."""
    return ((1.0 - r) * c) + (r * b)


def _tectonic_subduction(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Generates squared crust basin with modulated subduction belt."""
    return (0.40 * (c * c)) + (0.60 * b * (r * c))


def _stepped_mesa(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Quantizes relief into multi-tiered plateau steps."""
    terraces = np.floor(r * 4.0) / 4.0
    return (0.35 * c) + (0.65 * b * terraces)


def _factored_virtual_crust(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Simulates tectonic floor and peaks using virtual crust scaling."""
    return c * (config.CRUST_BUDGET + (config.RELIEF_BUDGET * b))


def _tibetan_high_plateau(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Models high-altitude plateau with sinusoidal valley carving."""
    return (np.power(c, 1.5) * 0.40) + (b * (0.60 * np.sin(c * np.pi)))


def _razor_ridge(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Sharpens base ridges via quadratic detail squaring."""
    return (c * 0.40) + (0.60 * c * (b * b))


def _inverted_canyonlands(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Carves deep ravines via inverted crust modulation."""
    return (c * 0.50) + (0.50 * (1.0 - (c * (1.0 - b))))


def _soft_natural_saturation(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    """Compresses peaks using hyperbolic tangent saturation."""
    return np.tanh(2.5 * c * b) * 0.95


COMPOSITE_CATALOG: List[FormulaPreset] = [
    FormulaPreset(
        name="Master 3-Layer Budgeting",
        shorthand="(0.35 * C) + (0.65 * B * (0.05 + 0.95 * R))",
        uses_relief=True,
        uses_crust=True,
        func=_master_3_layer,
    ),
    FormulaPreset(
        name="Global Envelope Factor",
        shorthand="R * ((0.35 * C) + (0.65 * B))",
        uses_relief=True,
        uses_crust=True,
        func=_global_envelope,
    ),
    FormulaPreset(
        name="Volcanic Island Override",
        shorthand="(0.50 * C) + (0.40 * B * R) + (0.10 * B)",
        uses_relief=True,
        uses_crust=True,
        func=_volcanic_island,
    ),
    FormulaPreset(
        name="Inverse Crust Bypass",
        shorthand="(0.35 * C) + (0.65 * B * (C * R + (1.0 - C)))",
        uses_relief=True,
        uses_crust=True,
        func=_inverse_crust_bypass,
    ),
    FormulaPreset(
        name="Dynamic Lerp / Morph",
        shorthand="((1.0 - R) * C) + (R * B)",
        uses_relief=True,
        uses_crust=True,
        func=_dynamic_lerp,
    ),
    FormulaPreset(
        name="Factored Virtual Crust",
        shorthand="C * (0.40 + 0.60 * B)",
        uses_relief=False,
        uses_crust=True,
        func=_factored_virtual_crust,
    ),
    FormulaPreset(
        name="Tibetan High Plateau",
        shorthand="(C**1.5 * 0.40) + (B * (0.60 * sin(C * pi)))",
        uses_relief=False,
        uses_crust=True,
        func=_tibetan_high_plateau,
    ),
    FormulaPreset(
        name="Razor Ridge / Granite Peaks",
        shorthand="(C * 0.40) + (0.60 * C * (B**2))",
        uses_relief=False,
        uses_crust=True,
        func=_razor_ridge,
    ),
    FormulaPreset(
        name="Inverted Canyonlands",
        shorthand="(C * 0.50) + (0.50 * (1.0 - C * (1.0 - B)))",
        uses_relief=False,
        uses_crust=True,
        func=_inverted_canyonlands,
    ),
    FormulaPreset(
        name="Soft Natural Saturation",
        shorthand="tanh(2.5 * C * B) * 0.95",
        uses_relief=False,
        uses_crust=True,
        func=_soft_natural_saturation,
    ),
    FormulaPreset(
        name="Tectonic Subduction Belt",
        shorthand="(0.40 * (C**2)) + (0.60 * B * (R * C))",
        uses_relief=True,
        uses_crust=True,
        func=_tectonic_subduction,
    ),
    FormulaPreset(
        name="Stepped Mesa Terraces",
        shorthand="(0.35 * C) + (0.65 * B * (floor(R * 4.0) / 4.0))",
        uses_relief=True,
        uses_crust=True,
        func=_stepped_mesa,
    ),
]


PRESETS_2D: List[Preset2D] = [
    Preset2D(
        name="Solo Vertical Base D(x)",
        shorthand="D(x)",
        uses_base=True,
        uses_relief=False,
        uses_crust=False,
        func=_solo_base,
        composite_index=-1,
    ),
    Preset2D(
        name="Solo Horizontal Relief M(y)",
        shorthand="M(y)",
        uses_base=False,
        uses_relief=True,
        uses_crust=False,
        func=_solo_relief,
        composite_index=-1,
    ),
    Preset2D(
        name="Solo Radial Crust C(r)",
        shorthand="C(r)",
        uses_base=False,
        uses_relief=False,
        uses_crust=True,
        func=_solo_crust,
        composite_index=-1,
    ),
    Preset2D(
        name="Master 3-Layer Budgeting",
        shorthand="(0.35 * C) + (0.65 * B * (0.05 + 0.95 * R))",
        uses_base=True,
        uses_relief=True,
        uses_crust=True,
        func=_master_3_layer,
        composite_index=0,
    ),
    Preset2D(
        name="Global Envelope Factor",
        shorthand="R * ((0.35 * C) + (0.65 * B))",
        uses_base=True,
        uses_relief=True,
        uses_crust=True,
        func=_global_envelope,
        composite_index=1,
    ),
    Preset2D(
        name="Volcanic Island Override",
        shorthand="(0.50 * C) + (0.40 * B * R) + (0.10 * B)",
        uses_base=True,
        uses_relief=True,
        uses_crust=True,
        func=_volcanic_island,
        composite_index=2,
    ),
    Preset2D(
        name="Inverse Crust Bypass",
        shorthand="(0.35 * C) + (0.65 * B * (C * R + (1.0 - C)))",
        uses_base=True,
        uses_relief=True,
        uses_crust=True,
        func=_inverse_crust_bypass,
        composite_index=3,
    ),
    Preset2D(
        name="Dynamic Lerp / Morph",
        shorthand="((1.0 - R) * C) + (R * B)",
        uses_base=True,
        uses_relief=True,
        uses_crust=True,
        func=_dynamic_lerp,
        composite_index=4,
    ),
    Preset2D(
        name="Factored Virtual Crust",
        shorthand="C * (0.40 + 0.60 * B)",
        uses_base=True,
        uses_relief=False,
        uses_crust=True,
        func=_factored_virtual_crust,
        composite_index=5,
    ),
    Preset2D(
        name="Tibetan High Plateau",
        shorthand="(C**1.5 * 0.40) + (B * (0.60 * sin(C * pi)))",
        uses_base=True,
        uses_relief=False,
        uses_crust=True,
        func=_tibetan_high_plateau,
        composite_index=6,
    ),
    Preset2D(
        name="Razor Ridge / Granite Peaks",
        shorthand="(C * 0.40) + (0.60 * C * (B**2))",
        uses_base=True,
        uses_relief=False,
        uses_crust=True,
        func=_razor_ridge,
        composite_index=7,
    ),
    Preset2D(
        name="Inverted Canyonlands",
        shorthand="(C * 0.50) + (0.50 * (1.0 - C * (1.0 - B)))",
        uses_base=True,
        uses_relief=False,
        uses_crust=True,
        func=_inverted_canyonlands,
        composite_index=8,
    ),
    Preset2D(
        name="Soft Natural Saturation",
        shorthand="tanh(2.5 * C * B) * 0.95",
        uses_base=True,
        uses_relief=False,
        uses_crust=True,
        func=_soft_natural_saturation,
        composite_index=9,
    ),
    Preset2D(
        name="Tectonic Subduction Belt",
        shorthand="(0.40 * (C**2)) + (0.60 * B * (R * C))",
        uses_base=True,
        uses_relief=True,
        uses_crust=True,
        func=_tectonic_subduction,
        composite_index=10,
    ),
    Preset2D(
        name="Stepped Mesa Terraces",
        shorthand="(0.35 * C) + (0.65 * B * (floor(R * 4.0) / 4.0))",
        uses_base=True,
        uses_relief=True,
        uses_crust=True,
        func=_stepped_mesa,
        composite_index=11,
    ),
]
