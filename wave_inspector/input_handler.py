"""Event processing and continuous input handling for the inspector."""

import pygame
import config
from wave_inspector.state import InspectorState


class InputHandler:
    """Handles keyboard events, focus navigation, and frequency scaling."""

    def handle_input(self, state: InspectorState, dt: float) -> bool:
        """Processes discrete events and held keys. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if not self._handle_key_down(state, event):
                    return False

        self._handle_held_keys(state, dt)
        return True

    def _handle_key_down(
        self,
        state: InspectorState,
        event: pygame.event.Event,
    ) -> bool:
        """Processes discrete key presses."""
        if event.key == pygame.K_ESCAPE:
            return False

        if event.key == pygame.K_1:
            state.sync_to_mode(1)
            self._clamp_focus_for_active_mode(state)
        elif event.key == pygame.K_2:
            state.sync_to_mode(2)
            self._clamp_focus_for_active_mode(state)
        elif event.key == pygame.K_SPACE:
            mods = pygame.key.get_mods()
            direction = -1 if mods & pygame.KMOD_SHIFT else 1
            state.step_tile_size(direction)
        elif event.key == pygame.K_TAB:
            mods = pygame.key.get_mods()
            direction = -1 if mods & pygame.KMOD_SHIFT else 1
            if state.active_mode == 1:
                state.cycle_formula_1d(direction)
            else:
                state.cycle_formula_2d(direction)
            self._clamp_focus_for_active_mode(state)
        elif event.key == pygame.K_c:
            mods = pygame.key.get_mods()
            direction = -1 if mods & pygame.KMOD_SHIFT else 1
            state.cycle_palette(direction)
        elif event.key == pygame.K_i:
            state.toggle_inversion()
        elif event.key == pygame.K_p:
            if state.active_mode == 2:
                state.toggle_perspective()
        elif event.key == pygame.K_n:
            state.toggle_net_mode()
        elif event.key == pygame.K_UP:
            self._move_channel_focus(state, -1)
        elif event.key == pygame.K_DOWN:
            self._move_channel_focus(state, 1)
        elif event.key == pygame.K_r:
            self._reset_cycles(state, pygame.key.get_mods())

        return True

    def _move_channel_focus(
        self,
        state: InspectorState,
        direction: int,
    ) -> None:
        """Navigates focus across valid input channels for active formula."""
        formula = (
            state.formula_1d if state.active_mode == 1 else state.preset_2d
        )
        channel_count = 3 if formula.uses_crust else 2
        state.selected_panel_index = (
            state.selected_panel_index + direction
        ) % channel_count

    def _clamp_focus_for_active_mode(self, state: InspectorState) -> None:
        """Clamps channel focus off crust when formula does not use crust."""
        formula = (
            state.formula_1d if state.active_mode == 1 else state.preset_2d
        )
        if not formula.uses_crust and state.selected_panel_index >= 2:
            state.selected_panel_index = 1

    def _reset_cycles(self, state: InspectorState, mods: int) -> None:
        """Resets focused channel or all channels to default frequencies."""
        if mods & pygame.KMOD_SHIFT:
            state.base_cycles = config.DEFAULT_BASE_CYCLES
            state.relief_cycles = config.DEFAULT_RELIEF_CYCLES
            state.crust_cycles = config.DEFAULT_CRUST_CYCLES
        elif state.selected_panel_index == 0:
            state.base_cycles = config.DEFAULT_BASE_CYCLES
        elif state.selected_panel_index == 1:
            state.relief_cycles = config.DEFAULT_RELIEF_CYCLES
        elif state.selected_panel_index == 2:
            state.crust_cycles = config.DEFAULT_CRUST_CYCLES

        state.needs_rebuild_2d = True

    def _handle_held_keys(self, state: InspectorState, dt: float) -> None:
        """Scales active channel frequency continuously via held arrows."""
        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_LEFT]
        move_right = keys[pygame.K_RIGHT]

        if move_left == move_right or dt <= 0.0:
            return

        direction = 1.0 if move_right else -1.0
        scale = 1.0 + (config.CYCLE_ZOOM_RATE * dt)

        if state.selected_panel_index == 0:
            state.base_cycles = self._apply_scale(
                state.base_cycles,
                scale,
                direction,
                config.BASE_MIN_CYCLES,
                config.BASE_MAX_CYCLES,
            )
        elif state.selected_panel_index == 1:
            state.relief_cycles = self._apply_scale(
                state.relief_cycles,
                scale,
                direction,
                config.RELIEF_MIN_CYCLES,
                config.RELIEF_MAX_CYCLES,
            )
        elif state.selected_panel_index == 2:
            state.crust_cycles = self._apply_scale(
                state.crust_cycles,
                scale,
                direction,
                config.CRUST_MIN_CYCLES,
                config.CRUST_MAX_CYCLES,
            )

        state.needs_rebuild_2d = True

    @staticmethod
    def _apply_scale(
        current: float,
        scale: float,
        direction: float,
        min_limit: float,
        max_limit: float,
    ) -> float:
        """Applies zoom multiplier and clamps to configured bounds."""
        target = current * scale if direction > 0.0 else current / scale
        return max(min_limit, min(max_limit, target))
