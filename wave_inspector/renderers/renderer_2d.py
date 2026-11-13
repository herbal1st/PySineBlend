"""2D spatial synthesizer renderer generating surfaces and relief nets."""

from typing import Dict, List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray
import pygame
import config
from wave_inspector.contour_net import (
    ContourScratch,
    bake_tile_contour_edges,
    create_contour_scratch,
    draw_contour_net_to_surface,
    draw_culled_contour_net_to_surface,
)
from wave_inspector.formulas import PRESETS_2D
from wave_inspector.renderers.base_renderer import BaseRenderer
from wave_inspector.state import InspectorState


class Renderer2D(BaseRenderer):
    """Bakes 2D float32 heightfield into surface or topographical net."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Initializes base renderer, target surface, and scratch cache."""
        super().__init__(screen)
        self.rendered_surface: pygame.Surface = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self._scratch_surfaces: Dict[Tuple[int, int], pygame.Surface] = {}
        self._contour_scratch: Optional[ContourScratch] = None
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

        if state.net_enabled:
            if state.tile_stepping_enabled:
                self._draw_tile_contour_edges(heightfield, color_source, state)
            else:
                self._render_net_surface(heightfield, color_source, state)
            return

        h_dim, w_dim = heightfield.shape
        indices = np.clip(heightfield * 1023.0, 0, 1023).astype(np.int32)
        rgb_buffer = color_source[indices]
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

    def _get_contour_scratch(self) -> ContourScratch:
        """Lazily allocates reusable (W, H) buffers for contour rendering."""
        if self._contour_scratch is None:
            self._contour_scratch = create_contour_scratch(
                self.width, self.height
            )
        return self._contour_scratch

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

    def _render_net_surface(
        self,
        heightfield: NDArray[np.float32],
        lut: NDArray[np.uint8],
        state: InspectorState,
    ) -> None:
        """Draws crisp isolines directly using culled or native paths."""
        h_dim, w_dim = heightfield.shape
        if w_dim != self.width or h_dim != self.height:
            draw_culled_contour_net_to_surface(
                surface=self.rendered_surface,
                coarse_wh=np.ascontiguousarray(heightfield.T),
                lut=lut,
                intervals=state.net_intervals,
                bandwidth=state.net_bandwidth,
                bg_color=config.COLOR_NET_BACKGROUND,
            )
            return

        scratch = self._get_contour_scratch()
        np.copyto(scratch.field_buf, heightfield.T)
        draw_contour_net_to_surface(
            surface=self.rendered_surface,
            heightfield_wh=scratch.field_buf,
            lut=lut,
            intervals=state.net_intervals,
            bandwidth=state.net_bandwidth,
            bg_color=config.COLOR_NET_BACKGROUND,
            scratch=scratch,
        )

    def _draw_tile_contour_edges(
        self,
        heightfield: NDArray[np.float32],
        lut: NDArray[np.uint8],
        state: InspectorState,
    ) -> None:
        """Stamps 1px tile-boundary isoline outlines onto target surface."""
        self.rendered_surface.fill(config.COLOR_NET_BACKGROUND)
        edges = bake_tile_contour_edges(
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
        """Draws channel strip and records clickable layer hitboxes."""
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
            c_id: Optional[int] = 2
        else:
            c_col = col_silenced
            c_text = "C: Silenced"
            c_id = None

        segments: List[Tuple[str, Tuple[int, int, int], Optional[int]]] = [
            ("CHANNEL FOCUS: [ ", col_label, None),
            (f"B: {state.base_cycles:.2f}", b_col, 0),
            (" | ", col_divider, None),
            (f"R: {state.relief_cycles:.2f}", r_col, 1),
            (" | ", col_divider, None),
            (c_text, c_col, c_id),
            (" ] cycles", col_label, None),
        ]

        rendered = [
            (self.font.render(text, True, color), ch_id)
            for text, color, ch_id in segments
        ]
        box_w = sum(surf.get_width() for surf, _ in rendered) + (pad * 2)
        box_h = max(surf.get_height() for surf, _ in rendered) + (pad * 2)

        bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg_surf.fill(config.COLOR_HUD_CARD_2D)
        self.screen.blit(bg_surf, (x, y))

        pygame.draw.rect(
            self.screen,
            config.COLOR_SELECTION,
            (x, y, box_w, box_h),
            config.PANEL_SELECTION_WIDTH,
        )

        state.channel_hitboxes.clear()
        curr_x = x + pad
        for surf, ch_id in rendered:
            self.screen.blit(surf, (curr_x, y + pad))
            if ch_id is not None:
                state.channel_hitboxes[ch_id] = pygame.Rect(
                    curr_x - 4, y, surf.get_width() + 8, box_h
                )
            curr_x += surf.get_width()
