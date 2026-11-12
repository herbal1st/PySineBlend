"""2D spatial synthesizer renderer generating surfaces and relief nets."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray
import pygame
import config
from wave_inspector.formulas import PRESETS_2D
from wave_inspector.renderers.base_renderer import BaseRenderer
from wave_inspector.state import InspectorState


@dataclass(frozen=True, slots=True)
class _TileContourEdges:
    """Directional contour colors and active masks for coarse tile seams."""

    v_colors: NDArray[np.uint8]
    v_active: NDArray[np.bool_]
    h_colors: NDArray[np.uint8]
    h_active: NDArray[np.bool_]


class Renderer2D(BaseRenderer):
    """Bakes 2D float32 heightfield into surface or topographical net."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Initializes base renderer, target surface, and scratch cache."""
        super().__init__(screen)
        self.rendered_surface: pygame.Surface = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self._scratch_surfaces: Dict[Tuple[int, int], pygame.Surface] = {}
        grey = np.linspace(
            0.0, 255.0, 1024, dtype=np.float32
        ).astype(np.uint8)
        self._fallback_lut: NDArray[np.uint8] = np.ascontiguousarray(
            np.repeat(grey[:, np.newaxis], 3, axis=1)
        )

    def update_surface(
        self,
        heightfield: NDArray[np.float32],
        lut: Optional[NDArray[np.uint8]],
        state: InspectorState,
    ) -> None:
        """Colors compact or native heightfields and scales onto target."""
        color_source = lut if lut is not None else self._fallback_lut

        if state.net_enabled and state.tile_stepping_enabled:
            self._draw_tile_contour_edges(heightfield, color_source, state)
            return

        h_dim, w_dim = heightfield.shape
        rgb_buffer = self._bake_rgb_buffer(heightfield, color_source, state)
        transposed = np.transpose(rgb_buffer, (1, 0, 2))

        if w_dim == self.width and h_dim == self.height:
            pygame.surfarray.blit_array(self.rendered_surface, transposed)
            return

        scratch = self._get_scratch_surface(w_dim, h_dim)
        pygame.surfarray.blit_array(scratch, transposed)

        if state.tile_stepping_enabled:
            target_w = w_dim * state.tile_size
            target_h = h_dim * state.tile_size
            scaled = pygame.transform.scale(scratch, (target_w, target_h))
            self.rendered_surface.blit(scaled, (0, 0))
            return

        pygame.transform.smoothscale(
            scratch,
            (self.width, self.height),
            self.rendered_surface,
        )

    def render(self, state: InspectorState, fps: float) -> None:
        """Blits baked 2D surface, metadata, and controls."""
        self.screen.blit(self.rendered_surface, (0, 0))
        self._draw_hud(state, fps)
        self.draw_controls_card(is_dark_theme=True)

    def _get_scratch_surface(
        self,
        width: int,
        height: int,
    ) -> pygame.Surface:
        """Returns cached offscreen surface matching compact grid size."""
        key = (width, height)
        surface = self._scratch_surfaces.get(key)
        if surface is None:
            surface = pygame.Surface(key)
            self._scratch_surfaces[key] = surface
        return surface

    def _bake_rgb_buffer(
        self,
        heightfield: NDArray[np.float32],
        lut: NDArray[np.uint8],
        state: InspectorState,
    ) -> NDArray[np.uint8]:
        """Maps float32 heights to uint8 RGB via LUT or contour net."""
        if state.net_enabled:
            return self._bake_contour_net(
                heightfield=heightfield,
                lut=lut,
                intervals=state.net_intervals,
                bandwidth=state.net_bandwidth,
                tile_stepping=state.is_scrubbing,
            )

        indices = np.clip(heightfield * 1023.0, 0, 1023).astype(np.int32)
        return np.ascontiguousarray(lut[indices])

    def _bake_contour_net(
        self,
        heightfield: NDArray[np.float32],
        lut: NDArray[np.uint8],
        intervals: float,
        bandwidth: float,
        tile_stepping: bool,
    ) -> NDArray[np.uint8]:
        """Synthesizes contour lines via one-sided crossings or bands."""
        h_dim, w_dim = heightfield.shape
        bg_rgb = np.array(config.COLOR_NET_BACKGROUND, dtype=np.uint8)
        buffer = np.full((h_dim, w_dim, 3), bg_rgb, dtype=np.uint8)

        count = max(1, int(round(intervals))) + 1
        levels = np.linspace(0.0, 1.0, count, dtype=np.float32)

        if tile_stepping:
            h_curr_x = heightfield[:, :-1]
            h_next_x = heightfield[:, 1:]
            h_curr_y = heightfield[:-1, :]
            h_next_y = heightfield[1:, :]

            for lvl in levels:
                lvl_idx = int(np.clip(lvl * 1023.0, 0, 1023))
                lvl_color = lut[lvl_idx]
                cross_mask = np.zeros((h_dim, w_dim), dtype=bool)

                if lvl >= 0.999:
                    cross_x = (h_curr_x < lvl) != (h_next_x < lvl)
                    cross_y = (h_curr_y < lvl) != (h_next_y < lvl)
                else:
                    cross_x = (h_curr_x <= lvl) != (h_next_x <= lvl)
                    cross_y = (h_curr_y <= lvl) != (h_next_y <= lvl)

                cross_mask[:, :-1] |= cross_x
                cross_mask[:-1, :] |= cross_y
                buffer[cross_mask] = lvl_color
        else:
            contour_mask = np.zeros((h_dim, w_dim), dtype=bool)
            for lvl in levels:
                diff = np.abs(heightfield - lvl)
                contour_mask |= diff <= bandwidth

            indices = np.clip(heightfield * 1023.0, 0, 1023).astype(np.int32)
            colored_pixels = lut[indices]
            buffer[contour_mask] = colored_pixels[contour_mask]

        return np.ascontiguousarray(buffer)

    def _draw_tile_contour_edges(
        self,
        heightfield: NDArray[np.float32],
        lut: NDArray[np.uint8],
        state: InspectorState,
    ) -> None:
        """Stamps 1px tile-boundary isoline outlines onto target surface."""
        self.rendered_surface.fill(config.COLOR_NET_BACKGROUND)
        edges = self._bake_tile_contour_edges(
            heightfield=heightfield,
            lut=lut,
            intervals=state.net_intervals,
        )
        tile_sz = state.tile_size

        v_cols_y = np.repeat(edges.v_colors, tile_sz, axis=0)[:self.height]
        v_mask_y = np.repeat(edges.v_active, tile_sz, axis=0)[:self.height]
        v_cols_xy = np.transpose(v_cols_y, (1, 0, 2))
        v_mask_xy = np.transpose(v_mask_y, (1, 0))

        h_cols_x = np.repeat(edges.h_colors, tile_sz, axis=1)[:, :self.width]
        h_mask_x = np.repeat(edges.h_active, tile_sz, axis=1)[:, :self.width]
        h_cols_xy = np.transpose(h_cols_x, (1, 0, 2))
        h_mask_xy = np.transpose(h_mask_x, (1, 0))

        surf_view = pygame.surfarray.pixels3d(self.rendered_surface)
        try:
            v_slots = surf_view[tile_sz::tile_sz].shape[0]
            v_count = min(v_cols_xy.shape[0], v_slots)
            if v_count > 0:
                v_stop = tile_sz * (v_count + 1)
                v_target = surf_view[tile_sz:v_stop:tile_sz]
                v_src = v_cols_xy[:v_count]
                v_where = v_mask_xy[:v_count, :, None]
                np.copyto(v_target, v_src, where=v_where)

            h_slots = surf_view[:, tile_sz::tile_sz].shape[1]
            h_count = min(h_cols_xy.shape[1], h_slots)
            if h_count > 0:
                h_stop = tile_sz * (h_count + 1)
                h_target = surf_view[:, tile_sz:h_stop:tile_sz]
                h_src = h_cols_xy[:, :h_count]
                h_where = h_mask_xy[:, :h_count, None]
                np.copyto(h_target, h_src, where=h_where)
        finally:
            del surf_view

    @staticmethod
    def _bake_tile_contour_edges(
        heightfield: NDArray[np.float32],
        lut: NDArray[np.uint8],
        intervals: float,
    ) -> _TileContourEdges:
        """Computes seam-crossing colors and masks on a coarse tile grid."""
        h_dim, w_dim = heightfield.shape
        v_cols = max(0, w_dim - 1)
        h_rows = max(0, h_dim - 1)

        v_colors = np.zeros((h_dim, v_cols, 3), dtype=np.uint8)
        v_active = np.zeros((h_dim, v_cols), dtype=bool)
        h_colors = np.zeros((h_rows, w_dim, 3), dtype=np.uint8)
        h_active = np.zeros((h_rows, w_dim), dtype=bool)

        if h_dim < 2 and w_dim < 2:
            return _TileContourEdges(
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

        return _TileContourEdges(
            v_colors=v_colors,
            v_active=v_active,
            h_colors=h_colors,
            h_active=h_active,
        )

    def _draw_hud(self, state: InspectorState, fps: float) -> None:
        """Renders stacked blueprint metadata and active channel cards."""
        preset = state.preset_2d
        pal_name, _, pal_desc = state.active_palette
        p_idx = state.preset_index_2d + 1
        total_p = len(PRESETS_2D)

        if preset.composite_index < 0:
            type_tag = "SOLO"
            persp_tag = "N/A (SOLO)"
        elif preset.uses_crust:
            type_tag = "3-LAYER"
            persp_tag = "WARPED" if state.is_warped else "RADIAL"
        else:
            type_tag = "2-LAYER"
            persp_tag = "WARPED" if state.is_warped else "RADIAL"

        step_tag = (
            f"ACTIVE ({state.tile_size}px)"
            if state.tile_stepping_enabled
            else "OFF (Smooth)"
        )
        net_tag = "ACTIVE" if state.net_enabled else "OFF"

        hud_lines: List[Tuple[str, Tuple[int, int, int]]] = [
            (
                f"MODE 2: 2D SPATIAL SYNTHESIZER | TILE: {step_tag} | "
                f"NET: {net_tag}",
                config.COLOR_HUD_TEXT_ACTIVE,
            ),
            (
                f"PALETTE: {pal_name} ({pal_desc}) | PERSP: {persp_tag}",
                config.COLOR_HUD_TEXT_NORMAL,
            ),
            (
                f"PRESET [{p_idx}/{total_p}] [{type_tag}] {preset.name}",
                config.COLOR_HUD_TEXT_NORMAL,
            ),
            (
                f"MATH  : {preset.shorthand}",
                config.COLOR_HUD_TEXT_NORMAL,
            ),
            (
                f"STATS : FPS: {fps:.1f} | VIEW: {self.width}x{self.height}",
                config.COLOR_HUD_TEXT_NORMAL,
            ),
        ]

        card1_h = self.draw_card(
            x=10,
            y=10,
            lines=hud_lines,
            bg_rgba=config.COLOR_HUD_CARD_2D,
            pad=8,
        )

        self._draw_channel_strip(
            x=10,
            y=10 + card1_h + 6,
            state=state,
            uses_crust=preset.uses_crust,
        )

    def _draw_channel_strip(
        self,
        x: int,
        y: int,
        state: InspectorState,
        uses_crust: bool,
    ) -> None:
        """Draws highlighted channel card framed in active blue border."""
        col_active = (85, 155, 255)
        col_muted = (140, 145, 155)
        col_divider = (80, 85, 95)
        col_label = (220, 220, 220)
        col_silenced = (90, 95, 105)

        pad = 8
        b_col = col_active if state.selected_panel_index == 0 else col_muted
        r_col = col_active if state.selected_panel_index == 1 else col_muted

        if uses_crust:
            c_col = (
                col_active if state.selected_panel_index == 2 else col_muted
            )
            c_text = f"C: {state.crust_cycles:.2f}"
        else:
            c_col = col_silenced
            c_text = "C: Silenced"

        segments: List[Tuple[str, Tuple[int, int, int]]] = [
            ("CHANNEL FOCUS: [ ", col_label),
            (f"B: {state.base_cycles:.2f}", b_col),
            (" | ", col_divider),
            (f"R: {state.relief_cycles:.2f}", r_col),
            (" | ", col_divider),
            (c_text, c_col),
            (" ] cycles", col_label),
        ]

        rendered = [
            self.font.render(text, True, color) for text, color in segments
        ]
        box_w = sum(surf.get_width() for surf in rendered) + (pad * 2)
        box_h = max(surf.get_height() for surf in rendered) + (pad * 2)

        bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg_surf.fill(config.COLOR_HUD_CARD_2D)
        self.screen.blit(bg_surf, (x, y))

        pygame.draw.rect(
            self.screen,
            config.COLOR_SELECTION,
            (x, y, box_w, box_h),
            config.PANEL_SELECTION_WIDTH,
        )

        curr_x = x + pad
        for surf in rendered:
            self.screen.blit(surf, (curr_x, y + pad))
            curr_x += surf.get_width()
