"""Pure NumPy vectorized topographical contour net (isoline) generator."""

from dataclasses import dataclass
from functools import lru_cache
from typing import Tuple
import numpy as np
from numpy.typing import NDArray
import pygame


@dataclass(frozen=True, slots=True)
class TileContourEdges:
    """Directional contour colors and active masks for coarse tile seams."""

    v_colors: NDArray[np.uint8]
    v_active: NDArray[np.bool_]
    h_colors: NDArray[np.uint8]
    h_active: NDArray[np.bool_]


@dataclass(slots=True)
class ContourScratch:
    """Reusable (W, H) buffers eliminating per-frame contour allocations."""

    field_buf: NDArray[np.float32]
    work_a: NDArray[np.float32]
    work_b: NDArray[np.float32]
    mask: NDArray[np.bool_]


@dataclass(frozen=True, slots=True)
class CellResamplePlan:
    """Cached coarse-cell-to-screen mapping and sub-pixel weights."""

    cell_sx: NDArray[np.int32]
    cell_wx: NDArray[np.float32]
    cell_sy: NDArray[np.int32]
    cell_wy: NDArray[np.float32]


def create_contour_scratch(width: int, height: int) -> ContourScratch:
    """Allocates reusable (W, H) scratch buffers matching SDL layout."""
    shape = (width, height)
    return ContourScratch(
        field_buf=np.empty(shape, dtype=np.float32),
        work_a=np.empty(shape, dtype=np.float32),
        work_b=np.empty(shape, dtype=np.float32),
        mask=np.empty(shape, dtype=bool),
    )


def bake_tile_contour_edges(
    heightfield: NDArray[np.float32],
    lut: NDArray[np.uint8],
    intervals: float,
) -> TileContourEdges:
    """Computes seam-crossing colors and masks on a coarse tile grid."""
    h_dim, w_dim = heightfield.shape
    v_cols = max(0, w_dim - 1)
    h_rows = max(0, h_dim - 1)

    v_colors = np.zeros((h_dim, v_cols, 3), dtype=np.uint8)
    v_active = np.zeros((h_dim, v_cols), dtype=bool)
    h_colors = np.zeros((h_rows, w_dim, 3), dtype=np.uint8)
    h_active = np.zeros((h_rows, w_dim), dtype=bool)

    if h_dim < 2 and w_dim < 2:
        return TileContourEdges(
            v_colors=v_colors,
            v_active=v_active,
            h_colors=h_colors,
            h_active=h_active,
        )

    count = max(1, int(round(intervals))) + 1
    levels = np.linspace(0.0, 1.0, count, dtype=np.float32)

    has_v = w_dim > 1
    has_h = h_dim > 1
    if has_v:
        v_min = np.minimum(heightfield[:, :-1], heightfield[:, 1:])
        v_max = np.maximum(heightfield[:, :-1], heightfield[:, 1:])
    if has_h:
        h_min = np.minimum(heightfield[:-1, :], heightfield[1:, :])
        h_max = np.maximum(heightfield[:-1, :], heightfield[1:, :])

    for lvl in levels:
        lvl_idx = int(np.clip(lvl * 1023.0, 0, 1023))
        lvl_color = lut[lvl_idx]

        if has_v:
            v_cross = (v_min <= lvl) & (lvl <= v_max)
            v_active |= v_cross
            v_colors[v_cross] = lvl_color

        if has_h:
            h_cross = (h_min <= lvl) & (lvl <= h_max)
            h_active |= h_cross
            h_colors[h_cross] = lvl_color

    return TileContourEdges(
        v_colors=v_colors,
        v_active=v_active,
        h_colors=h_colors,
        h_active=h_active,
    )


def draw_contour_net_to_surface(
    surface: pygame.Surface,
    heightfield_wh: NDArray[np.float32],
    lut: NDArray[np.uint8],
    intervals: float,
    bandwidth: float,
    bg_color: Tuple[int, int, int],
    scratch: ContourScratch,
) -> None:
    """Draws crisp isolines directly onto a (W, H) surface in-place."""
    surface.fill(bg_color)

    step_count = max(1, int(round(intervals)))
    step_f = float(step_count)
    limit = bandwidth * step_f

    np.multiply(heightfield_wh, step_f, out=scratch.work_a)
    np.rint(scratch.work_a, out=scratch.work_b)
    np.subtract(scratch.work_a, scratch.work_b, out=scratch.work_a)
    np.abs(scratch.work_a, out=scratch.work_a)
    np.less_equal(scratch.work_a, limit, out=scratch.mask)

    if not np.any(scratch.mask):
        return

    indices = np.clip(
        heightfield_wh[scratch.mask] * 1023.0, 0.0, 1023.0
    ).astype(np.int32)
    colors = lut[indices]

    surf_view = pygame.surfarray.pixels3d(surface)
    try:
        surf_view[scratch.mask] = colors
    finally:
        del surf_view


def draw_culled_contour_net_to_surface(
    surface: pygame.Surface,
    coarse_wh: NDArray[np.float32],
    lut: NDArray[np.uint8],
    intervals: float,
    bandwidth: float,
    bg_color: Tuple[int, int, int],
) -> None:
    """Draws 1px isolines from a coarse (W, H) grid via cell culling."""
    surface.fill(bg_color)
    src_w, src_h = coarse_wh.shape
    if src_w < 2 or src_h < 2:
        return

    step_f = float(max(1, int(round(intervals))))
    limit = bandwidth * step_f
    cx_idx, cy_idx = _find_active_cells(coarse_wh, step_f, limit)
    if cx_idx.size == 0:
        return

    tgt_w, tgt_h = surface.get_size()
    plan = _get_cell_plan(src_w, src_h, tgt_w, tgt_h)

    f00 = coarse_wh[cx_idx, cy_idx][:, None, None]
    f10 = coarse_wh[cx_idx + 1, cy_idx][:, None, None]
    f01 = coarse_wh[cx_idx, cy_idx + 1][:, None, None]
    f11 = coarse_wh[cx_idx + 1, cy_idx + 1][:, None, None]

    wx = plan.cell_wx[cx_idx][:, :, None]
    wy = plan.cell_wy[cy_idx][:, None, :]

    top = f00 + ((f10 - f00) * wx)
    bot = f01 + ((f11 - f01) * wx)
    vals = top + ((bot - top) * wy)

    scaled = vals * step_f
    mask = np.abs(scaled - np.rint(scaled)) <= limit
    hit_k, hit_bx, hit_by = np.nonzero(mask)
    if hit_k.size == 0:
        return

    screen_x = plan.cell_sx[cx_idx[hit_k], hit_bx]
    screen_y = plan.cell_sy[cy_idx[hit_k], hit_by]
    hit_vals = vals[hit_k, hit_bx, hit_by]

    indices = np.clip(hit_vals * 1023.0, 0.0, 1023.0).astype(np.int32)
    colors = lut[indices]

    surf_view = pygame.surfarray.pixels3d(surface)
    try:
        surf_view[screen_x, screen_y] = colors
    finally:
        del surf_view


def _find_active_cells(
    coarse_wh: NDArray[np.float32],
    step_f: float,
    limit: float,
) -> Tuple[NDArray[np.intp], NDArray[np.intp]]:
    """Identifies coarse cells whose value bounds cross a contour band."""
    f00 = coarse_wh[:-1, :-1]
    f10 = coarse_wh[1:, :-1]
    f01 = coarse_wh[:-1, 1:]
    f11 = coarse_wh[1:, 1:]

    c_min = np.minimum(np.minimum(f00, f10), np.minimum(f01, f11))
    c_max = np.maximum(np.maximum(f00, f10), np.maximum(f01, f11))

    u_min = c_min * step_f
    u_max = c_max * step_f
    active = np.ceil(u_min - limit) <= np.floor(u_max + limit)
    return np.nonzero(active)


@lru_cache(maxsize=8)
def _get_cell_plan(
    src_w: int,
    src_h: int,
    tgt_w: int,
    tgt_h: int,
) -> CellResamplePlan:
    """Precomputes per-cell screen coordinates and sub-pixel weights."""
    cell_sx, cell_wx = _build_axis_cells(src_w, tgt_w)
    cell_sy, cell_wy = _build_axis_cells(src_h, tgt_h)
    return CellResamplePlan(
        cell_sx=cell_sx,
        cell_wx=cell_wx,
        cell_sy=cell_sy,
        cell_wy=cell_wy,
    )


def _build_axis_cells(
    src_len: int,
    tgt_len: int,
) -> Tuple[NDArray[np.int32], NDArray[np.float32]]:
    """Maps each coarse cell interval along one axis to screen slots."""
    num_cells = src_len - 1
    ratio = float(num_cells) / float(tgt_len)
    coords = np.arange(tgt_len, dtype=np.float32) * ratio
    cell_px = np.clip(
        np.floor(coords).astype(np.int32), 0, num_cells - 1
    )
    weight_px = (coords - cell_px).astype(np.float32)

    counts = np.bincount(cell_px, minlength=num_cells)
    max_span = max(1, int(np.max(counts)))

    cell_pos = np.empty((num_cells, max_span), dtype=np.int32)
    cell_w = np.empty((num_cells, max_span), dtype=np.float32)

    cell_ids = np.arange(num_cells)
    starts = np.searchsorted(cell_px, cell_ids, side="left")
    ends = np.searchsorted(cell_px, cell_ids, side="right")

    for idx in range(num_cells):
        s_idx = int(starts[idx])
        e_idx = int(ends[idx])
        span = e_idx - s_idx
        if span <= 0:
            clamped = min(tgt_len - 1, s_idx)
            cell_pos[idx, :] = clamped
            cell_w[idx, :] = weight_px[clamped]
            continue

        cell_pos[idx, :span] = np.arange(s_idx, e_idx, dtype=np.int32)
        cell_w[idx, :span] = weight_px[s_idx:e_idx]
        if span < max_span:
            cell_pos[idx, span:] = e_idx - 1
            cell_w[idx, span:] = weight_px[e_idx - 1]

    return cell_pos, cell_w
