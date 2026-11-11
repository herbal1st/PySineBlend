"""Diagnostic color lookup tables for mathematical wave visualization."""

from typing import List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray

PaletteEntry = Tuple[str, Optional[NDArray[np.uint8]], str]


def _bake_lut(
    control_points: List[Tuple[float, Tuple[int, int, int]]],
) -> NDArray[np.uint8]:
    """Interpolates RGB control stops across 1,024 slots using np.interp."""
    xp = np.array([pt[0] for pt in control_points], dtype=np.float32)
    r_pts = np.array([pt[1][0] for pt in control_points], dtype=np.float32)
    g_pts = np.array([pt[1][1] for pt in control_points], dtype=np.float32)
    b_pts = np.array([pt[1][2] for pt in control_points], dtype=np.float32)

    samples = np.linspace(0.0, 1.0, 1024, dtype=np.float32)

    r_lut = np.clip(np.interp(samples, xp, r_pts), 0, 255).astype(np.uint8)
    g_lut = np.clip(np.interp(samples, xp, g_pts), 0, 255).astype(np.uint8)
    b_lut = np.clip(np.interp(samples, xp, b_pts), 0, 255).astype(np.uint8)

    stacked = np.stack([r_lut, g_lut, b_lut], axis=-1)
    return np.ascontiguousarray(stacked)


def invert_lut(lut: NDArray[np.uint8]) -> NDArray[np.uint8]:
    """Reverses colormap array along elevation axis."""
    return np.ascontiguousarray(lut[::-1])


def get_heatmap_catalog() -> List[PaletteEntry]:
    """Compiles consolidated 4-entry playlist of diagnostic heatmaps."""
    # 1. Greyscale Baseline
    grey_ramp = np.linspace(
        0.0, 255.0, 1024, dtype=np.float32
    ).astype(np.uint8)
    greyscale = np.repeat(grey_ramp[:, np.newaxis], 3, axis=1)

    # 2. Magma (Perceptual High-Contrast Sequential)
    magma_stops: List[Tuple[float, Tuple[int, int, int]]] = [
        (0.00, (0, 0, 4)),
        (0.20, (40, 11, 84)),
        (0.40, (101, 21, 110)),
        (0.60, (182, 54, 121)),
        (0.80, (251, 136, 97)),
        (0.95, (254, 216, 154)),
        (1.00, (252, 253, 191)),
    ]

    # 3. Turbo (Google Spectral Rainbow Curve)
    turbo_stops: List[Tuple[float, Tuple[int, int, int]]] = [
        (0.00, (48, 18, 59)),
        (0.15, (70, 134, 251)),
        (0.35, (27, 229, 181)),
        (0.55, (164, 252, 60)),
        (0.75, (251, 185, 56)),
        (0.90, (227, 73, 24)),
        (1.00, (122, 4, 3)),
    ]

    # 4. Viridis (Perceptual Standard Colormap)
    viridis_stops: List[Tuple[float, Tuple[int, int, int]]] = [
        (0.00, (68, 1, 84)),
        (0.25, (59, 82, 139)),
        (0.50, (33, 145, 140)),
        (0.75, (94, 201, 98)),
        (1.00, (253, 231, 37)),
    ]

    return [
        ("GREYSCALE", np.ascontiguousarray(greyscale), "Linear Monochrome"),
        ("MAGMA", _bake_lut(magma_stops), "Perceptual Sequential"),
        ("TURBO", _bake_lut(turbo_stops), "Spectral Rainbow"),
        ("VIRIDIS", _bake_lut(viridis_stops), "Perceptual Standard"),
    ]
