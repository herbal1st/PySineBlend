"""Event processing and continuous input handling for the inspector."""

import math
from typing import List, Tuple
import pygame
import config
from wave_inspector.state import InspectorState


class InputHandler:
    """Handles keyboard events, smart mouse selection, drags, and zoom."""

    def __init__(self) -> None:
        """Initializes active mouse drag button and cursor tracking."""
        self.active_mouse_button: int = 0
        self.drag_start: Tuple[int, int] = (0, 0)

    def handle_input(self, state: InspectorState, dt: float) -> bool:
        """Processes discrete events and held keys. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if not self._handle_key_down(state, event):
                    return False
            elif (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button in (1, 3)
                and self.active_mouse_button == 0
            ):
                self._handle_mouse_down(state, event.button, event.pos)
            elif (
                event.type == pygame.MOUSEBUTTONUP
                and event.button == self.active_mouse_button
            ):
                self.active_mouse_button = 0
                keys = pygame.key.get_pressed()
                if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                    state.settle_scrubbing()
            elif (
                event.type == pygame.MOUSEMOTION
                and self.active_mouse_button != 0
            ):
                self._handle_mouse_motion(state, event.pos)

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
            self._reset_tuning(state, pygame.key.get_mods())

        return True

    def _handle_mouse_down(
        self,
        state: InspectorState,
        button: int,
        pos: Tuple[int, int],
    ) -> None:
        """Selects clicked panel/card layer or starts a mouse drag."""
        if state.active_mode == 1:
            panel_h = config.SCREEN_HEIGHT // config.PANEL_COUNT
            panel_idx = min(
                config.PANEL_COUNT - 1, max(0, pos[1] // panel_h)
            )
            if panel_idx not in self._get_valid_channels(state):
                return
            if state.selected_panel_index != panel_idx:
                state.selected_panel_index = panel_idx
                state.needs_rebuild_1d = True
            self.active_mouse_button = button
            self.drag_start = pos
            return

        for channel_idx, rect in state.channel_hitboxes.items():
            if rect.collidepoint(pos):
                state.selected_panel_index = channel_idx
                return

        self.active_mouse_button = button
        self.drag_start = pos

    def _handle_mouse_motion(
        self,
        state: InspectorState,
        pos: Tuple[int, int],
    ) -> None:
        """Dispatches active left or right mouse drag deltas."""
        dx = pos[0] - self.drag_start[0]
        dy = pos[1] - self.drag_start[1]
        self.drag_start = pos
        if dx == 0 and dy == 0:
            return

        shift_held = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)
        if self.active_mouse_button == 1:
            ndx = float(dx) / float(config.SCREEN_WIDTH)
            ndy = float(dy) / float(config.SCREEN_HEIGHT)
            single_layer = shift_held and state.selected_panel_index != 3
            self._shift_wave_offsets(state, ndx, ndy, single_layer)
            state.mark_scrubbing()
        elif self.active_mouse_button == 3 and dx != 0:
            factor = math.exp(float(dx) * config.MOUSE_ZOOM_SENSITIVITY)
            self._scale_channels(state, factor, single_layer=shift_held)
            state.mark_scrubbing()

    def _handle_held_keys(self, state: InspectorState, dt: float) -> None:
        """Scales channel frequencies continuously via held arrow keys."""
        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_LEFT]
        move_right = keys[pygame.K_RIGHT]

        if move_left == move_right or dt <= 0.0:
            return

        step_scale = 1.0 + (config.CYCLE_ZOOM_RATE * dt)
        factor = step_scale if move_right else (1.0 / step_scale)
        shift_held = bool(pygame.key.get_mods() & pygame.KMOD_SHIFT)

        self._scale_channels(state, factor, single_layer=shift_held)
        state.mark_scrubbing()

    def _shift_wave_offsets(
        self,
        state: InspectorState,
        ndx: float,
        ndy: float,
        single_layer: bool,
    ) -> None:
        """Applies normalized 2D drag deltas to wave channels."""
        if not single_layer or state.selected_panel_index == 0:
            state.base_offset_x += ndx
            state.base_offset_y += ndy
        if not single_layer or state.selected_panel_index == 1:
            state.relief_offset_x += ndx
            state.relief_offset_y += ndy
        if not single_layer or state.selected_panel_index == 2:
            state.crust_offset_x += ndx
            state.crust_offset_y += ndy

    def _get_valid_channels(
        self,
        state: InspectorState,
    ) -> Tuple[int, ...]:
        """Returns valid selectable channel indices for active mode."""
        if state.active_mode == 2:
            preset = state.preset_2d
            channels: List[int] = []
            if preset.uses_base:
                channels.append(0)
            if preset.uses_relief:
                channels.append(1)
            if preset.uses_crust:
                channels.append(2)
            return tuple(channels) if channels else (0,)

        formula = state.formula_1d
        channels = [0]
        if formula.uses_relief:
            channels.append(1)
        if formula.uses_crust:
            channels.append(2)
        channels.append(3)
        return tuple(channels)

    def _move_channel_focus(
        self,
        state: InspectorState,
        direction: int,
    ) -> None:
        """Navigates focus across valid input channels for active mode."""
        channels = self._get_valid_channels(state)
        if state.selected_panel_index in channels:
            cur_pos = channels.index(state.selected_panel_index)
            next_pos = (cur_pos + direction) % len(channels)
            state.selected_panel_index = channels[next_pos]
        else:
            state.selected_panel_index = channels[0]

        if state.active_mode == 1:
            state.needs_rebuild_1d = True

    def _clamp_focus_for_active_mode(self, state: InspectorState) -> None:
        """Clamps channel focus to valid channels for active mode."""
        channels = self._get_valid_channels(state)
        if state.selected_panel_index in channels:
            return
        state.selected_panel_index = channels[0]
        if state.active_mode == 1:
            state.needs_rebuild_1d = True

    def _reset_tuning(self, state: InspectorState, mods: int) -> None:
        """Resets all channels, or only focused channel when SHIFT held."""
        reset_all = not bool(mods & pygame.KMOD_SHIFT)
        state.reset_wave_channels(reset_all=reset_all)

    def _scale_channels(
        self,
        state: InspectorState,
        factor: float,
        single_layer: bool,
    ) -> None:
        """Scales all wave channels, or only focused one when single_layer."""
        scale_all = (not single_layer) or (
            state.active_mode == 1 and state.selected_panel_index == 3
        )
        anchor_2d = state.active_mode == 2

        if scale_all or state.selected_panel_index == 0:
            old_base = state.base_cycles
            new_base = self._clamp(
                old_base * factor,
                config.BASE_MIN_CYCLES,
                config.BASE_MAX_CYCLES,
            )
            if new_base != old_base:
                state.base_cycles = new_base
                if anchor_2d:
                    state.base_offset_x *= old_base / new_base

        if scale_all or state.selected_panel_index == 1:
            old_relief = state.relief_cycles
            new_relief = self._clamp(
                old_relief * factor,
                config.RELIEF_MIN_CYCLES,
                config.RELIEF_MAX_CYCLES,
            )
            if new_relief != old_relief:
                state.relief_cycles = new_relief
                if anchor_2d:
                    state.relief_offset_y *= old_relief / new_relief

        if scale_all or state.selected_panel_index == 2:
            old_crust = state.crust_cycles
            new_crust = self._clamp(
                old_crust * factor,
                config.CRUST_MIN_CYCLES,
                config.CRUST_MAX_CYCLES,
            )
            if new_crust != old_crust:
                state.crust_cycles = new_crust
                preset = state.preset_2d
                is_warped_2layer = (
                    preset.composite_index >= 0
                    and not preset.uses_relief
                    and state.is_warped
                )
                if anchor_2d and is_warped_2layer:
                    state.crust_offset_y *= old_crust / new_crust

    @staticmethod
    def _clamp(value: float, min_limit: float, max_limit: float) -> float:
        """Clamps scalar tuning value within inclusive bounds."""
        return max(min_limit, min(max_limit, value))
