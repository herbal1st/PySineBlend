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
    uses_crust: bool
    func: WaveFunction


@dataclass(frozen=True, slots=True)
class Preset2D:
    """2D spatial preset specification binding projection geometry."""

    name: str
    shorthand: str
    uses_crust: bool
    projection: str
    func: WaveFunction
    composite_index: int


# ------ Core Mathematical Functions ------

def _solo_base(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return b


def _solo_relief(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return r


def _solo_crust(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return c


def _master_3_layer(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    rf = config.MIN_RELIEF_FACTOR + ((1.0 - config.MIN_RELIEF_FACTOR) * r)
    return (config.CRUST_BUDGET * c) + (config.RELIEF_BUDGET * b * rf)


def _global_envelope(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return r * ((config.CRUST_BUDGET * c) + (config.RELIEF_BUDGET * b))


def _volcanic_island(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return (0.50 * c) + (0.40 * b * r) + (0.10 * b)


def _inverse_crust_bypass(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    rmix = (c * r) + (1.0 - c)
    return (config.CRUST_BUDGET * c) + (config.RELIEF_BUDGET * b * rmix)


def _dynamic_lerp(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return ((1.0 - r) * c) + (r * b)


def _tectonic_subduction(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return (0.40 * (c * c)) + (0.60 * b * (r * c))


def _stepped_mesa(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    terraces = np.floor(r * 4.0) / 4.0
    return (0.35 * c) + (0.65 * b * terraces)


def _factored_virtual_crust(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return r * (config.CRUST_BUDGET + (config.RELIEF_BUDGET * b))


def _tibetan_high_plateau(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return (np.power(r, 1.5) * 0.40) + (b * (0.60 * np.sin(r * np.pi)))


def _razor_ridge(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return (r * 0.40) + (0.60 * r * (b * b))


def _inverted_canyonlands(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return (r * 0.50) + (0.50 * (1.0 - (r * (1.0 - b))))


def _soft_natural_saturation(b: NDArray, r: NDArray, c: NDArray) -> NDArray:
    return np.tanh(2.5 * r * b) * 0.95


# ------ 1D Composite Catalog (12 Formulas) ------

COMPOSITE_CATALOG: List[FormulaPreset] = [
    # 3-Layer Series (Indices 0 to 4)
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
    # 2-Layer Series (Indices 5 to 9)
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
    # 3-Layer Hybrids (Indices 10 and 11)
    FormulaPreset(
        name="Tectonic Subduction Belt",
        shorthand="(0.40 * (C**2)) + (0.60 * B * (R * C))",
        uses_crust=True,
        func=_tectonic_subduction,
    ),
    FormulaPreset(
        name="Stepped Mesa Terraces",
        shorthand="(0.35 * C) + (0.65 * B * (floor(R * 4.0) / 4.0))",
        uses_crust=True,
        func=_stepped_mesa,
    ),
]


# ------ 2D Unified Preset Catalog (20 Presets) ------

PRESETS_2D: List[Preset2D] = [
    # 1. Solo Components (Presets 1 to 3)
    Preset2D(
        name="Solo Vertical Base D(x)",
        shorthand="D(x)",
        uses_crust=False,
        projection="STANDARD",
        func=_solo_base,
        composite_index=-1,
    ),
    Preset2D(
        name="Solo Horizontal Relief M(y)",
        shorthand="M(y)",
        uses_crust=False,
        projection="STANDARD",
        func=_solo_relief,
        composite_index=-1,
    ),
    Preset2D(
        name="Solo Radial Crust C(r)",
        shorthand="C(r)",
        uses_crust=True,
        projection="STANDARD",
        func=_solo_crust,
        composite_index=-1,
    ),
    # 2. 3-Layer Series (Presets 4 to 8)
    Preset2D(
        name="Master 3-Layer Budgeting",
        shorthand="(0.35 * C) + (0.65 * B * (0.05 + 0.95 * R))",
        uses_crust=True,
        projection="STANDARD",
        func=_master_3_layer,
        composite_index=0,
    ),
    Preset2D(
        name="Global Envelope Factor",
        shorthand="R * ((0.35 * C) + (0.65 * B))",
        uses_crust=True,
        projection="STANDARD",
        func=_global_envelope,
        composite_index=1,
    ),
    Preset2D(
        name="Volcanic Island Override",
        shorthand="(0.50 * C) + (0.40 * B * R) + (0.10 * B)",
        uses_crust=True,
        projection="STANDARD",
        func=_volcanic_island,
        composite_index=2,
    ),
    Preset2D(
        name="Inverse Crust Bypass",
        shorthand="(0.35 * C) + (0.65 * B * (C * R + (1.0 - C)))",
        uses_crust=True,
        projection="STANDARD",
        func=_inverse_crust_bypass,
        composite_index=3,
    ),
    Preset2D(
        name="Dynamic Lerp / Morph",
        shorthand="((1.0 - R) * C) + (R * B)",
        uses_crust=True,
        projection="STANDARD",
        func=_dynamic_lerp,
        composite_index=4,
    ),
    # 3. 2-Layer Series Dual Projections (Presets 9 to 18)
    Preset2D(
        name="Factored Virtual Crust [Radial]",
        shorthand="R(r) * (0.35 + 0.65 * B(x))",
        uses_crust=False,
        projection="RADIAL",
        func=_factored_virtual_crust,
        composite_index=5,
    ),
    Preset2D(
        name="Factored Virtual Crust [Warped]",
        shorthand="R(y) * (0.35 + 0.65 * B(x_warp))",
        uses_crust=False,
        projection="WARPED",
        func=_factored_virtual_crust,
        composite_index=5,
    ),
    Preset2D(
        name="Tibetan High Plateau [Radial]",
        shorthand="(R(r)**1.5 * 0.40) + (B * (0.60 * sin(R(r) * pi)))",
        uses_crust=False,
        projection="RADIAL",
        func=_tibetan_high_plateau,
        composite_index=6,
    ),
    Preset2D(
        name="Tibetan High Plateau [Warped]",
        shorthand="(R(y)**1.5 * 0.40) + (B * (0.60 * sin(R(y) * pi)))",
        uses_crust=False,
        projection="WARPED",
        func=_tibetan_high_plateau,
        composite_index=6,
    ),
    Preset2D(
        name="Razor Ridge / Granite Peaks [Radial]",
        shorthand="(R(r) * 0.40) + (0.60 * R(r) * (B**2))",
        uses_crust=False,
        projection="RADIAL",
        func=_razor_ridge,
        composite_index=7,
    ),
    Preset2D(
        name="Razor Ridge / Granite Peaks [Warped]",
        shorthand="(R(y) * 0.40) + (0.60 * R(y) * (B_warp**2))",
        uses_crust=False,
        projection="WARPED",
        func=_razor_ridge,
        composite_index=7,
    ),
    Preset2D(
        name="Inverted Canyonlands [Radial]",
        shorthand="(R(r) * 0.50) + (0.50 * (1.0 - R(r) * (1.0 - B)))",
        uses_crust=False,
        projection="RADIAL",
        func=_inverted_canyonlands,
        composite_index=8,
    ),
    Preset2D(
        name="Inverted Canyonlands [Warped]",
        shorthand="(R(y) * 0.50) + (0.50 * (1.0 - R(y) * (1.0 - B_warp)))",
        uses_crust=False,
        projection="WARPED",
        func=_inverted_canyonlands,
        composite_index=8,
    ),
    Preset2D(
        name="Soft Natural Saturation [Radial]",
        shorthand="tanh(2.5 * R(r) * B(x)) * 0.95",
        uses_crust=False,
        projection="RADIAL",
        func=_soft_natural_saturation,
        composite_index=9,
    ),
    Preset2D(
        name="Soft Natural Saturation [Warped]",
        shorthand="tanh(2.5 * R(y) * B(x_warp)) * 0.95",
        uses_crust=False,
        projection="WARPED",
        func=_soft_natural_saturation,
        composite_index=9,
    ),
    # 4. 3-Layer Hybrids (Presets 19 and 20)
    Preset2D(
        name="Tectonic Subduction Belt",
        shorthand="(0.40 * (C**2)) + (0.60 * B * (R * C))",
        uses_crust=True,
        projection="STANDARD",
        func=_tectonic_subduction,
        composite_index=10,
    ),
    Preset2D(
        name="Stepped Mesa Terraces",
        shorthand="(0.35 * C) + (0.65 * B * (floor(R * 4.0) / 4.0))",
        uses_crust=True,
        projection="STANDARD",
        func=_stepped_mesa,
        composite_index=11,
    ),
]
