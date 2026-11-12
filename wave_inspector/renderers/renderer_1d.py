"""1D stacked oscilloscope renderer displaying four signal plots."""

from typing import List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray
import pygame
import config
from wave_inspector.formulas import COMPOSITE_CATALOG
from wave_inspector.renderers.base_renderer import BaseRenderer
from wave_inspector.state import InspectorState
from wave_inspector.wave_model import WaveFrame1D


class Renderer1D(BaseRenderer):
    """Draws component waves and their composite result in four panels."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Initializes base renderer and offscreen 1D frame cache."""
        super().__init__(screen)
        self.cached_surface: pygame.Surface = pygame.Surface(
            (self.width, self.height)
        )

    def update_surface(
        self,
        state: InspectorState,
        frame: WaveFrame1D,
    ) -> None:
        """Rebuilds all four oscilloscope panels onto the cached surface."""
        self.cached_surface.fill(config.BACKGROUND_COLOR)
        formula = state.formula_1d
        pal_name, active_lut, pal_desc = state.active_palette

        if state.net_enabled:
            fill_lut = None
            line_lut = active_lut
            net_status = "NET LINE"
        else:
            fill_lut = active_lut
            line_lut = None
            net_status = "COLOR FILL"

        b_tag = " [ACTIVE]" if state.selected_panel_index == 0 else ""
        b_step = (
            f" [STEP: {state.tile_size}px]"
            if state.tile_stepping_enabled
            else ""
        )
        b_title = (
            f"PANEL 1: BASE DETAIL WAVE D(x){b_tag}{b_step} | "
            f"CYCLES: {state.base_cycles:.1f} | "
            f"START: {config.BASE_START:.2f}"
        )
        self._draw_panel(
            panel_index=0,
            wave_data=frame.base,
            title=b_title,
            line_width=config.COMPONENT_LINE_WIDTH,
            is_selected=state.selected_panel_index == 0,
        )

        r_tag = " [ACTIVE]" if state.selected_panel_index == 1 else ""
        r_title = (
            f"PANEL 2: RELIEF MULTIPLIER M(x){r_tag} | "
            f"CYCLES: {state.relief_cycles:.1f} | "
            f"START: {config.RELIEF_START:.2f} | "
            f"MIN_RELIEF: {config.MIN_RELIEF_FACTOR:.2f}"
        )
        self._draw_panel(
            panel_index=1,
            wave_data=frame.relief,
            title=r_title,
            line_width=config.COMPONENT_LINE_WIDTH,
            is_selected=state.selected_panel_index == 1,
        )

        if formula.uses_crust:
            c_tag = " [ACTIVE]" if state.selected_panel_index == 2 else ""
            c_title = (
                f"PANEL 3: CONTINENTAL CRUST C(x){c_tag} | "
                f"CYCLES: {state.crust_cycles:.2f} | "
                f"START: {config.CRUST_START:.2f} | "
                f"BUDGET: {config.CRUST_BUDGET:.2f}"
            )
            c_data = frame.crust
            c_silenced = False
            c_selected = state.selected_panel_index == 2
        else:
            c_title = (
                "PANEL 3: CONTINENTAL CRUST C(x) | "
                "[SILENCED / NOT USED IN THIS 2-LAYER FORMULA]"
            )
            c_data = np.zeros_like(frame.crust)
            c_silenced = True
            c_selected = False

        self._draw_panel(
            panel_index=2,
            wave_data=c_data,
            title=c_title,
            line_width=config.COMPONENT_LINE_WIDTH,
            is_silenced=c_silenced,
            is_selected=c_selected,
        )

        min_v = float(np.min(frame.composite))
        max_v = float(np.max(frame.composite))
        layer_tag = "3-LAYER" if formula.uses_crust else "2-LAYER"
        p4_title = (
            f"PANEL 4: [{state.composite_index + 1}/"
            f"{len(COMPOSITE_CATALOG)}] [{layer_tag}] "
            f"{formula.name}: {formula.shorthand} | "
            f"RANGE: [{min_v:.3f}, {max_v:.3f}]"
        )
        self._draw_panel(
            panel_index=3,
            wave_data=frame.composite,
            title=p4_title,
            line_width=config.COMPOSITE_LINE_WIDTH,
            margin_bottom=config.PANEL_COMPOSITE_BOTTOM_MARGIN,
            fill_lut=fill_lut,
            line_lut=line_lut,
        )

        p4_pal_text = f"PALETTE: {pal_name} ({pal_desc}) | [{net_status}]"
        self._draw_palette_card(p4_pal_text)

    def render(self) -> None:
        """Blits the cached 1D frame and overlays the controls card."""
        self.screen.blit(self.cached_surface, (0, 0))
        self.draw_controls_card(is_dark_theme=False)

    def _draw_panel(
        self,
        panel_index: int,
        wave_data: NDArray[np.float32],
        title: str,
        line_width: int,
        is_silenced: bool = False,
        is_selected: bool = False,
        margin_bottom: int = config.PANEL_BOTTOM_MARGIN,
        fill_lut: Optional[NDArray[np.uint8]] = None,
        line_lut: Optional[NDArray[np.uint8]] = None,
    ) -> None:
        """Renders an oscilloscope panel with fill or multi-colored line."""
        panel_h = self.height // config.PANEL_COUNT
        y_top = panel_index * panel_h
        y_bottom = y_top + panel_h
        y_draw_min = y_bottom - margin_bottom
        y_draw_max = y_top + config.PANEL_TOP_MARGIN
        draw_h = float(y_draw_min - y_draw_max)
        int_draw_h = int(draw_h)

        pygame.draw.line(
            self.cached_surface,
            config.COLOR_PANEL_DIVIDER,
            (0, y_bottom),
            (self.width, y_bottom),
            config.PANEL_DIVIDER_WIDTH,
        )

        grid_levels: List[Tuple[float, Tuple[int, int, int]]] = [
            (1.00, (0, 0, 0)),
            (0.75, config.COLOR_GRID),
            (0.50, config.COLOR_GRID),
            (0.25, config.COLOR_GRID),
            (0.00, (0, 0, 0)),
        ]
        for level, color in grid_levels:
            lvl_y = int(round(y_draw_min - (level * draw_h)))
            pygame.draw.line(
                self.cached_surface,
                color,
                (0, lvl_y),
                (self.width, lvl_y),
                1,
            )

        pixel_x = np.arange(self.width, dtype=np.int32)
        pixel_y = np.round(y_draw_min - (wave_data * draw_h)).astype(np.int32)

        if fill_lut is not None and int_draw_h > 0:
            self._render_vectorized_fill(
                wave_data=wave_data,
                fill_lut=fill_lut,
                y_draw_max=y_draw_max,
                int_draw_h=int_draw_h,
            )

        if line_lut is not None and not is_silenced:
            indices = np.clip(wave_data * 1023.0, 0, 1023).astype(np.int32)
            rgb_cols = line_lut[indices]
            for x in range(self.width - 1):
                col = (
                    int(rgb_cols[x, 0]),
                    int(rgb_cols[x, 1]),
                    int(rgb_cols[x, 2]),
                )
                p0 = (int(pixel_x[x]), int(pixel_y[x]))
                p1 = (int(pixel_x[x + 1]), int(pixel_y[x + 1]))
                pygame.draw.line(self.cached_surface, col, p0, p1, line_width)
        else:
            wave_color = (
                config.COLOR_SILENCED_WAVE
                if is_silenced
                else config.COLOR_WAVE
            )
            points = np.column_stack((pixel_x, pixel_y))
            pygame.draw.lines(
                self.cached_surface,
                wave_color,
                False,
                points.tolist(),
                line_width,
            )

        if is_selected:
            pygame.draw.rect(
                self.cached_surface,
                config.COLOR_SELECTION,
                (1, y_top + 1, self.width - 2, panel_h - 2),
                config.PANEL_SELECTION_WIDTH,
            )

        title_color = (
            config.COLOR_SELECTION
            if is_selected
            else (
                config.COLOR_MUTED_TITLE
                if is_silenced
                else config.COLOR_TITLE
            )
        )
        title_surf = self.font.render(title, True, title_color)
        box_w = title_surf.get_width() + 16
        box_h = title_surf.get_height() + 6

        bg_card = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg_card.fill(config.COLOR_TITLE_CARD)

        tx = config.PANEL_TITLE_X
        ty = y_top + config.PANEL_TITLE_Y
        self.cached_surface.blit(bg_card, (tx, ty))
        self.cached_surface.blit(
            title_surf,
            (tx + config.PANEL_TITLE_TEXT_X, ty + config.PANEL_TITLE_TEXT_Y),
        )

    def _render_vectorized_fill(
        self,
        wave_data: NDArray[np.float32],
        fill_lut: NDArray[np.uint8],
        y_draw_max: int,
        int_draw_h: int,
    ) -> None:
        """Blits columnar hypsometric fills via vectorized NumPy buffer."""
        lut_idx = np.clip(wave_data * 1023.0, 0, 1023).astype(np.int32)
        cols_rgb = fill_lut[lut_idx]

        h_pixels = np.round(wave_data * float(int_draw_h)).astype(np.int32)
        h_clamped = np.clip(h_pixels, 0, int_draw_h)

        y_indices = np.arange(int_draw_h, dtype=np.int32)[:, None]
        active_mask = y_indices >= (int_draw_h - h_clamped[None, :])

        bg_rgb = np.array(config.BACKGROUND_COLOR, dtype=np.uint8)
        buffer = np.full(
            (int_draw_h, self.width, 3), bg_rgb, dtype=np.uint8
        )
        broadcast_cols = np.broadcast_to(
            cols_rgb[None, :, :], (int_draw_h, self.width, 3)
        )
        np.copyto(buffer, broadcast_cols, where=active_mask[:, :, None])

        surf_transposed = np.transpose(buffer, (1, 0, 2))
        fill_surface = pygame.surfarray.make_surface(surf_transposed)
        self.cached_surface.blit(fill_surface, (0, y_draw_max))

    def _draw_palette_card(self, text: str) -> None:
        """Renders active palette info in bottom-right footer of Panel 4."""
        surf = self.font.render(text, True, config.COLOR_TITLE)
        box_w = surf.get_width() + 16
        box_h = surf.get_height() + 6

        bg_card = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg_card.fill(config.COLOR_TITLE_CARD)

        rx = self.width - box_w - config.PANEL_TITLE_X
        ry = self.height - box_h - 10

        self.cached_surface.blit(bg_card, (rx, ry))
        self.cached_surface.blit(surf, (rx + 8, ry + 3))
