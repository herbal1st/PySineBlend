"""Application loop and input state for the wave math inspector."""

import numpy as np
from numpy.typing import NDArray
import pygame

import config
from wave_inspector.formulas import FORMULA_CATALOG
from wave_inspector.renderer import WaveRenderer
from wave_inspector.state import InspectorState
from wave_inspector.wave_model import WaveFrame, build_wave_frame


class WaveMathInspector:
    """Coordinates window lifecycle, input, wave generation, and drawing."""

    def __init__(self) -> None:
        """Initializes Pygame, state, coordinates, and the renderer."""
        pygame.init()
        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(config.APP_TITLE)
        self.clock = pygame.time.Clock()
        self.state = InspectorState()
        self.x_coordinates: NDArray[np.float32] = np.linspace(
            0.0,
            1.0,
            config.SCREEN_WIDTH,
            dtype=np.float32,
        )
        self.renderer = WaveRenderer(self.screen)

    def run(self) -> None:
        """Runs the event, update, and render loop until the user exits."""
        running = True
        try:
            while running:
                dt = self.clock.tick(config.FPS) / 1000.0
                running = self._handle_events()
                if not running:
                    break

                self._update_cycles(dt)
                frame = self._build_frame()
                self.renderer.render(self.state, frame)
                pygame.display.flip()
        finally:
            pygame.quit()

    def _handle_events(self) -> bool:
        """Handles quit, formula cycling, and focused-panel selection."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                return False

            if event.key == pygame.K_TAB:
                direction = (
                    -1 if event.mod & pygame.KMOD_SHIFT else 1
                )
                self.state.active_formula_index = (
                    self.state.active_formula_index + direction
                ) % len(FORMULA_CATALOG)
                self._limit_selected_panel()
            elif event.key == pygame.K_UP:
                self._move_panel_focus(-1)
            elif event.key == pygame.K_DOWN:
                self._move_panel_focus(1)

        return True

    def _move_panel_focus(self, direction: int) -> None:
        """Moves focus through the layers used by the active formula."""
        formula = FORMULA_CATALOG[self.state.active_formula_index]
        panel_count = 3 if formula.uses_crust else 2
        self.state.selected_panel_index = (
            self.state.selected_panel_index + direction
        ) % panel_count

    def _limit_selected_panel(self) -> None:
        """Moves focus off crust when the new formula does not use it."""
        formula = FORMULA_CATALOG[self.state.active_formula_index]
        if not formula.uses_crust and self.state.selected_panel_index >= 2:
            self.state.selected_panel_index = 1

    def _update_cycles(self, dt: float) -> None:
        """Adjusts focused cycles continuously while one arrow is held."""
        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_LEFT]
        move_right = keys[pygame.K_RIGHT]
        if move_left == move_right:
            return

        direction = 1.0 if move_right else -1.0
        self._adjust_selected_cycles(direction, dt)

    def _adjust_selected_cycles(
        self,
        direction: float,
        dt: float,
    ) -> None:
        """Scales the focused frequency and clamps it to its config bounds."""
        panel_index = self.state.selected_panel_index
        if panel_index == 0:
            self.state.base_cycles = self._scale_cycles(
                self.state.base_cycles,
                config.BASE_MIN_CYCLES,
                config.BASE_MAX_CYCLES,
                direction,
                dt,
            )
        elif panel_index == 1:
            self.state.relief_cycles = self._scale_cycles(
                self.state.relief_cycles,
                config.RELIEF_MIN_CYCLES,
                config.RELIEF_MAX_CYCLES,
                direction,
                dt,
            )
        elif panel_index == 2:
            self.state.crust_cycles = self._scale_cycles(
                self.state.crust_cycles,
                config.CRUST_MIN_CYCLES,
                config.CRUST_MAX_CYCLES,
                direction,
                dt,
            )

    def _build_frame(self) -> WaveFrame:
        """Builds the current wave data using the selected formula."""
        formula = FORMULA_CATALOG[self.state.active_formula_index]
        return build_wave_frame(
            self.x_coordinates,
            formula,
            self.state.base_cycles,
            self.state.relief_cycles,
            self.state.crust_cycles,
        )

    @staticmethod
    def _scale_cycles(
        value: float,
        minimum: float,
        maximum: float,
        direction: float,
        dt: float,
    ) -> float:
        """Applies the time-based cycle multiplier within the given bounds."""
        if dt <= 0.0:
            return value

        scale = 1.0 + (config.CYCLE_ZOOM_RATE * dt)
        adjusted = value * scale if direction > 0.0 else value / scale
        return max(minimum, min(maximum, adjusted))


def run_app() -> None:
    """Creates and runs the standalone wave math inspector."""
    WaveMathInspector().run()
