"""Pure NumPy mathematical engine for 1D and 2D wave synthesis."""

from dataclasses import dataclass
import math
import numpy as np
from numpy.typing import NDArray
import config
from wave_inspector.formulas import FormulaPreset, Preset2D


@dataclass(frozen=True, slots=True)
class WaveFrame1D:
    """Holds 1D vector arrays for input components and composite result."""

    base: NDArray[np.float32]
    relief: NDArray[np.float32]
    crust: NDArray[np.float32]
    composite: NDArray[np.float32]


@dataclass(frozen=True, slots=True)
class CoordinateMesh2D:
    """Precomputed normalized 2D coordinate matrices for spatial views."""

    x_norm: NDArray[np.float32]
    y_norm: NDArray[np.float32]
    r_norm: NDArray[np.float32]


def compute_phase(start_height: float) -> float:
    """Calculates ascending sine phase offset for a given start height."""
    clamped = max(0.0, min(1.0, start_height))
    normalized_scalar = (clamped * 2.0) - 1.0
    return math.asin(normalized_scalar)


def quantize_coordinates(
    coords: NDArray[np.float32],
    dimension_size: int,
    tile_size: int,
) -> NDArray[np.float32]:
    """Snaps continuous coordinates to tile centroid points."""
    if tile_size <= 1:
        return coords
    intervals = max(1, dimension_size // tile_size)
    step = 1.0 / float(intervals)
    centered = (np.floor(coords * float(intervals)) + 0.5) * step
    return centered.astype(np.float32)


def build_coordinate_mesh_2d(
    width: int,
    height: int,
) -> CoordinateMesh2D:
    """Generates aspect-ratio-corrected normalized 2D coordinate grids."""
    x_lin = np.linspace(0.0, 1.0, width, dtype=np.float32)
    y_lin = np.linspace(0.0, 1.0, height, dtype=np.float32)
    x_norm, y_norm = np.meshgrid(x_lin, y_lin)

    aspect_ratio: float = float(width) / float(height)
    x_centered = (x_norm - 0.5) * aspect_ratio
    y_centered = y_norm - 0.5

    raw_r = np.sqrt((x_centered * x_centered) + (y_centered * y_centered))
    max_corner_r = math.sqrt((0.5 * aspect_ratio) ** 2 + 0.5**2)
    r_norm = (raw_r / float(max_corner_r)).astype(np.float32)

    return CoordinateMesh2D(
        x_norm=x_norm,
        y_norm=y_norm,
        r_norm=r_norm,
    )


def build_quantized_mesh_2d(
    width: int,
    height: int,
    tile_size: int,
) -> CoordinateMesh2D:
    """Precomputes centroid-quantized coordinate and radial distance grids."""
    base_mesh = build_coordinate_mesh_2d(width, height)
    x_q = quantize_coordinates(base_mesh.x_norm, width, tile_size)
    y_q = quantize_coordinates(base_mesh.y_norm, height, tile_size)

    aspect: float = float(width) / float(height)
    xc = (x_q - 0.5) * aspect
    yc = y_q - 0.5
    raw_r = np.sqrt((xc * xc) + (yc * yc))
    max_r = math.sqrt((0.5 * aspect) ** 2 + 0.5**2)
    r_q = (raw_r / float(max_r)).astype(np.float32)

    return CoordinateMesh2D(
        x_norm=x_q,
        y_norm=y_q,
        r_norm=r_q,
    )


def _evaluate_sine_grid(
    coords: NDArray[np.float32],
    cycles: float,
    start_height: float,
) -> NDArray[np.float32]:
    """Evaluates continuous sine wave across arbitrary coordinate arrays."""
    phase = compute_phase(start_height)
    angles = (2.0 * math.pi * cycles * coords) + phase
    wave = 0.5 + (0.5 * np.sin(angles))
    return wave.astype(np.float32)


def build_wave_frame_1d(
    x_coordinates: NDArray[np.float32],
    formula: FormulaPreset,
    base_cycles: float,
    relief_cycles: float,
    crust_cycles: float,
    tile_stepping: bool = False,
    tile_size: int = config.DEFAULT_TILE_SIZE,
) -> WaveFrame1D:
    """Builds 1D component waveforms and the clipped composite result."""
    coords = x_coordinates
    if tile_stepping:
        coords = quantize_coordinates(
            coords=x_coordinates,
            dimension_size=config.SCREEN_WIDTH,
            tile_size=tile_size,
        )

    base = _evaluate_sine_grid(coords, base_cycles, config.BASE_START)
    relief = _evaluate_sine_grid(coords, relief_cycles, config.RELIEF_START)
    crust = _evaluate_sine_grid(coords, crust_cycles, config.CRUST_START)

    raw_composite = formula.func(base, relief, crust)
    composite = np.clip(raw_composite, 0.0, 1.0).astype(np.float32)

    return WaveFrame1D(
        base=base,
        relief=relief,
        crust=crust,
        composite=composite,
    )


def build_wave_frame_2d(
    mesh: CoordinateMesh2D,
    preset: Preset2D,
    base_cycles: float,
    relief_cycles: float,
    crust_cycles: float,
    is_warped: bool = False,
) -> NDArray[np.float32]:
    """Evaluates 2D wave field with dynamic perspective geometry."""
    x_grid = mesh.x_norm
    y_grid = mesh.y_norm
    r_grid = mesh.r_norm
    zeros = np.zeros_like(x_grid)

    if preset.composite_index < 0:
        base_2d = _evaluate_sine_grid(
            x_grid, base_cycles, config.BASE_START
        )
        relief_2d = _evaluate_sine_grid(
            y_grid, relief_cycles, config.RELIEF_START
        )
        crust_2d = _evaluate_sine_grid(
            r_grid, crust_cycles, config.CRUST_START
        )
    elif not preset.uses_crust:
        crust_2d = zeros
        if is_warped:
            relief_2d = _evaluate_sine_grid(
                y_grid, relief_cycles, config.RELIEF_START
            )
            offset = config.WARP_FACTOR * (relief_2d - 0.5)
            base_2d = _evaluate_sine_grid(
                x_grid + offset, base_cycles, config.BASE_START
            )
        else:
            base_2d = _evaluate_sine_grid(
                x_grid, base_cycles, config.BASE_START
            )
            relief_2d = _evaluate_sine_grid(
                r_grid, relief_cycles, config.RELIEF_START
            )
    else:
        crust_2d = _evaluate_sine_grid(
            r_grid, crust_cycles, config.CRUST_START
        )
        relief_2d = _evaluate_sine_grid(
            y_grid, relief_cycles, config.RELIEF_START
        )
        if is_warped:
            offset = config.WARP_FACTOR * (relief_2d - 0.5)
            base_2d = _evaluate_sine_grid(
                x_grid + offset, base_cycles, config.BASE_START
            )
        else:
            base_2d = _evaluate_sine_grid(
                x_grid, base_cycles, config.BASE_START
            )

    raw_composite = preset.func(base_2d, relief_2d, crust_2d)
    return np.clip(raw_composite, 0.0, 1.0).astype(np.float32)
