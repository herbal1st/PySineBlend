"""Pygame rendering for the four-panel wave math inspector."""

from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray
import pygame

import config
from wave_inspector.formulas import FORMULA_CATALOG
from wave_inspector.state import InspectorState
from wave_inspector.wave_model import WaveFrame


class WaveRenderer:
    """Draws component waves and their composite result."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Binds the window surface and creates the panel title font."""
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.font_title = pygame.font.SysFont("monospace", 13, bold=True)

    def render(
        self,
        state: InspectorState,
        frame: WaveFrame,
    ) -> None:
        """Draws all four panels for the current inspector state."""
        formula = FORMULA_CATALOG[state.active_formula_index]
        self.screen.fill(config.BACKGROUND_COLOR)

        base_tag = (
            " [ACTIVE]" if state.selected_panel_index == 0 else ""
        )
        base_title = (
            f"PANEL 1: BASE DETAIL WAVE D(x){base_tag} | "
            f"CYCLES: {state.base_cycles:.1f} | "
            f"START: {config.BASE_START:.2f}"
        )
        self._draw_panel(
            panel_index=0,
            wave_data=frame.base,
            title=base_title,
            line_width=config.COMPONENT_LINE_WIDTH,
            is_selected=state.selected_panel_index == 0,
        )

        relief_tag = (
            " [ACTIVE]" if state.selected_panel_index == 1 else ""
        )
        relief_title = (
            f"PANEL 2: RELIEF MULTIPLIER M(x){relief_tag} | "
            f"CYCLES: {state.relief_cycles:.1f} | "
            f"START: {config.RELIEF_START:.2f} | "
            f"MIN_RELIEF: {config.MIN_RELIEF_FACTOR:.2f}"
        )
        self._draw_panel(
            panel_index=1,
            wave_data=frame.relief,
            title=relief_title,
            line_width=config.COMPONENT_LINE_WIDTH,
            is_selected=state.selected_panel_index == 1,
        )

        if formula.uses_crust:
            crust_tag = (
                " [ACTIVE]" if state.selected_panel_index == 2 else ""
            )
            crust_title = (
                f"PANEL 3: CONTINENTAL CRUST C(x){crust_tag} | "
                f"CYCLES: {state.crust_cycles:.2f} | "
                f"START: {config.CRUST_START:.2f} | "
                f"BUDGET: {config.CRUST_BUDGET:.2f}"
            )
            crust_data = frame.crust
            crust_silenced = False
            crust_selected = state.selected_panel_index == 2
        else:
            crust_title = (
                "PANEL 3: CONTINENTAL CRUST C(x) | "
                "[SILENCED / NOT USED IN THIS 2-LAYER FORMULA]"
            )
            crust_data = np.zeros_like(frame.crust)
            crust_silenced = True
            crust_selected = False

        self._draw_panel(
            panel_index=2,
            wave_data=crust_data,
            title=crust_title,
            line_width=config.COMPONENT_LINE_WIDTH,
            is_silenced=crust_silenced,
            is_selected=crust_selected,
        )

        min_value = float(np.min(frame.composite))
        max_value = float(np.max(frame.composite))
        layer_tag = "3-LAYER" if formula.uses_crust else "2-LAYER"
        result_title = (
            f"PANEL 4: [{state.active_formula_index + 1}/"
            f"{len(FORMULA_CATALOG)}] [{layer_tag}] "
            f"{formula.name}: {formula.shorthand} | "
            f"RANGE: [{min_value:.3f}, {max_value:.3f}] | "
            "[UP/DN]: Focus | [LF/RT]: Cycles | [TAB]: Formula"
        )
        self._draw_panel(
            panel_index=3,
            wave_data=frame.composite,
            title=result_title,
            line_width=config.COMPOSITE_LINE_WIDTH,
        )

    def _draw_panel(
        self,
        panel_index: int,
        wave_data: NDArray[np.float32],
        title: str,
        line_width: int,
        is_silenced: bool = False,
        is_selected: bool = False,
    ) -> None:
        """Draws one plot panel, including its grid, wave, and title card."""
        panel_height = self.height // config.PANEL_COUNT
        y_top = panel_index * panel_height
        y_bottom = y_top + panel_height
        y_draw_min = y_bottom - config.PANEL_BOTTOM_MARGIN
        y_draw_max = y_top + config.PANEL_TOP_MARGIN
        draw_height = float(y_draw_min - y_draw_max)

        pygame.draw.line(
            self.screen,
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
            level_y = int(round(y_draw_min - (level * draw_height)))
            pygame.draw.line(
                self.screen,
                color,
                (0, level_y),
                (self.width, level_y),
                1,
            )

        pixel_x = np.arange(self.width, dtype=np.int32)
        pixel_y = np.round(
            y_draw_min - (wave_data * draw_height)
        ).astype(np.int32)
        points = np.column_stack((pixel_x, pixel_y))

        wave_color = (
            config.COLOR_SILENCED_WAVE
            if is_silenced
            else config.COLOR_WAVE
        )
        pygame.draw.lines(
            self.screen,
            wave_color,
            False,
            points.tolist(),
            line_width,
        )

        if is_selected:
            pygame.draw.rect(
                self.screen,
                config.COLOR_SELECTION,
                (
                    1,
                    y_top + 1,
                    self.width - 2,
                    panel_height - 2,
                ),
                config.PANEL_SELECTION_WIDTH,
            )

        if is_selected:
            title_color = config.COLOR_SELECTION
        elif is_silenced:
            title_color = config.COLOR_MUTED_TITLE
        else:
            title_color = config.COLOR_TITLE

        title_surface = self.font_title.render(title, True, title_color)
        box_width = title_surface.get_width() + 16
        box_height = title_surface.get_height() + 6
        title_card = pygame.Surface(
            (box_width, box_height),
            pygame.SRCALPHA,
        )
        title_card.fill(config.COLOR_TITLE_CARD)

        title_x = config.PANEL_TITLE_X
        title_y = y_top + config.PANEL_TITLE_Y
        self.screen.blit(title_card, (title_x, title_y))
        self.screen.blit(
            title_surface,
            (
                title_x + config.PANEL_TITLE_TEXT_X,
                title_y + config.PANEL_TITLE_TEXT_Y,
            ),
        )
