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
    aspect_ratio: float
    inv_max_r: float


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
    return _build_mesh_from_axes(x_lin, y_lin, width, height)


def build_coarse_mesh_2d(
    width: int,
    height: int,
    tile_size: int,
) -> CoordinateMesh2D:
    """Precomputes coarse tile-centroid coordinate and radial distance grids."""
    coarse_w = max(1, math.ceil(float(width) / float(tile_size)))
    coarse_h = max(1, math.ceil(float(height) / float(tile_size)))

    stride_x = float(tile_size) / float(width)
    stride_y = float(tile_size) / float(height)

    x_lin = (np.arange(coarse_w, dtype=np.float32) + 0.5) * stride_x
    y_lin = (np.arange(coarse_h, dtype=np.float32) + 0.5) * stride_y
    return _build_mesh_from_axes(x_lin, y_lin, width, height)


def build_scrub_mesh_2d(
    width: int,
    height: int,
    factor: int,
) -> CoordinateMesh2D:
    """Precomputes endpoint-aligned (N+1) sub-sampled mesh for scrubbing."""
    safe_factor = max(1, factor)
    scrub_w = max(2, (width // safe_factor) + 1)
    scrub_h = max(2, (height // safe_factor) + 1)

    x_lin = np.linspace(0.0, 1.0, scrub_w, dtype=np.float32)
    y_lin = np.linspace(0.0, 1.0, scrub_h, dtype=np.float32)
    return _build_mesh_from_axes(x_lin, y_lin, width, height)


def build_wave_frame_1d(
    x_coordinates: NDArray[np.float32],
    formula: FormulaPreset,
    base_cycles: float,
    relief_cycles: float,
    crust_cycles: float,
    tile_stepping: bool = False,
    tile_size: int = config.DEFAULT_TILE_SIZE,
    base_offset_x: float = 0.0,
    relief_offset_x: float = 0.0,
    crust_offset_x: float = 0.0,
) -> WaveFrame1D:
    """Builds 1D component waveforms and the clipped composite result."""
    coords = x_coordinates
    if tile_stepping:
        coords = quantize_coordinates(
            coords=x_coordinates,
            dimension_size=config.SCREEN_WIDTH,
            tile_size=tile_size,
        )

    base = _evaluate_sine_grid(
        coords - base_offset_x, base_cycles, config.BASE_START
    )
    relief = _evaluate_sine_grid(
        coords - relief_offset_x, relief_cycles, config.RELIEF_START
    )
    crust = _evaluate_sine_grid(
        coords - crust_offset_x, crust_cycles, config.CRUST_START
    )

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
    base_offset_x: float = 0.0,
    base_offset_y: float = 0.0,
    relief_offset_x: float = 0.0,
    relief_offset_y: float = 0.0,
    crust_offset_x: float = 0.0,
    crust_offset_y: float = 0.0,
) -> NDArray[np.float32]:
    """Evaluates compact 2D wave field for the supplied coordinate mesh."""
    x_grid = mesh.x_norm - base_offset_x
    y_grid = mesh.y_norm - relief_offset_y
    zeros = np.zeros_like(mesh.x_norm)

    if preset.composite_index < 0:
        base_2d = _evaluate_sine_grid(
            x_grid, base_cycles, config.BASE_START
        )
        relief_2d = _evaluate_sine_grid(
            y_grid, relief_cycles, config.RELIEF_START
        )
        c_rad = _compute_radial_grid(mesh, crust_offset_x, crust_offset_y)
        crust_2d = _evaluate_sine_grid(
            c_rad, crust_cycles, config.CRUST_START
        )
    elif not preset.uses_crust:
        crust_2d = zeros
        if is_warped:
            relief_2d = _evaluate_sine_grid(
                y_grid, relief_cycles, config.RELIEF_START
            )
            warp = config.WARP_FACTOR * (relief_2d - 0.5)
            base_2d = _evaluate_sine_grid(
                x_grid + warp, base_cycles, config.BASE_START
            )
        else:
            base_2d = _evaluate_sine_grid(
                x_grid, base_cycles, config.BASE_START
            )
            r_rad = _compute_radial_grid(
                mesh, relief_offset_x, relief_offset_y
            )
            relief_2d = _evaluate_sine_grid(
                r_rad, relief_cycles, config.RELIEF_START
            )
    else:
        c_rad = _compute_radial_grid(mesh, crust_offset_x, crust_offset_y)
        crust_2d = _evaluate_sine_grid(
            c_rad, crust_cycles, config.CRUST_START
        )
        relief_2d = _evaluate_sine_grid(
            y_grid, relief_cycles, config.RELIEF_START
        )
        if is_warped:
            warp = config.WARP_FACTOR * (relief_2d - 0.5)
            base_2d = _evaluate_sine_grid(
                x_grid + warp, base_cycles, config.BASE_START
            )
        else:
            base_2d = _evaluate_sine_grid(
                x_grid, base_cycles, config.BASE_START
            )

    raw_composite = preset.func(base_2d, relief_2d, crust_2d)
    clipped = np.clip(raw_composite, 0.0, 1.0).astype(np.float32)
    return np.ascontiguousarray(clipped)


def _build_mesh_from_axes(
    x_lin: NDArray[np.float32],
    y_lin: NDArray[np.float32],
    width: int,
    height: int,
) -> CoordinateMesh2D:
    """Constructs normalized X, Y, and aspect-corrected radial grids."""
    x_norm, y_norm = np.meshgrid(x_lin, y_lin)

    aspect_ratio = float(width) / float(height)
    x_centered = (x_norm - 0.5) * aspect_ratio
    y_centered = y_norm - 0.5

    raw_r = np.sqrt((x_centered * x_centered) + (y_centered * y_centered))
    max_corner_r = math.sqrt((0.5 * aspect_ratio) ** 2 + 0.5**2)
    inv_max_r = 1.0 / float(max_corner_r)
    r_norm = (raw_r * inv_max_r).astype(np.float32)

    return CoordinateMesh2D(
        x_norm=x_norm,
        y_norm=y_norm,
        r_norm=r_norm,
        aspect_ratio=aspect_ratio,
        inv_max_r=inv_max_r,
    )


def _compute_radial_grid(
    mesh: CoordinateMesh2D,
    offset_x: float,
    offset_y: float,
) -> NDArray[np.float32]:
    """Computes normalized radial distance from a shifted center point."""
    if offset_x == 0.0 and offset_y == 0.0:
        return mesh.r_norm

    dx = (mesh.x_norm - (0.5 + offset_x)) * mesh.aspect_ratio
    dy = mesh.y_norm - (0.5 + offset_y)
    raw_r = np.sqrt((dx * dx) + (dy * dy))
    return (raw_r * mesh.inv_max_r).astype(np.float32)


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
