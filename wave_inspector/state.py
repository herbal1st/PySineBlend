"""Mutable runtime selections and tuning state for the inspector."""

from dataclasses import dataclass, field
from typing import Dict, List
import pygame
import config
from wave_inspector.formulas import (
    COMPOSITE_CATALOG,
    PRESETS_2D,
    FormulaPreset,
    Preset2D,
)
from wave_inspector.heatmaps import (
    PaletteEntry,
    get_heatmap_catalog,
    invert_lut,
)


@dataclass(slots=True)
class InspectorState:
    """Holds active viewport, formula pointers, focus, and wave state."""

    active_mode: int = config.DEFAULT_VIEW_MODE
    composite_index: int = 0
    preset_index_2d: int = 3
    selected_panel_index: int = 0
    active_palette_index: int = 0
    is_inverted: bool = False
    is_warped: bool = False
    net_enabled: bool = config.DEFAULT_NET_ENABLED
    net_intervals: float = config.DEFAULT_NET_INTERVALS
    net_bandwidth: float = config.DEFAULT_NET_BANDWIDTH
    base_cycles: float = config.DEFAULT_BASE_CYCLES
    relief_cycles: float = config.DEFAULT_RELIEF_CYCLES
    crust_cycles: float = config.DEFAULT_CRUST_CYCLES
    base_offset_x: float = 0.0
    base_offset_y: float = 0.0
    relief_offset_x: float = 0.0
    relief_offset_y: float = 0.0
    crust_offset_x: float = 0.0
    crust_offset_y: float = 0.0
    tile_stepping_enabled: bool = False
    tile_size: int = config.DEFAULT_TILE_SIZE
    needs_rebuild_1d: bool = True
    needs_rebuild_2d: bool = True
    is_scrubbing: bool = False
    scrub_timer: float = 0.0
    channel_hitboxes: Dict[int, pygame.Rect] = field(default_factory=dict)
    palettes: List[PaletteEntry] = field(
        default_factory=get_heatmap_catalog
    )

    @property
    def formula_1d(self) -> FormulaPreset:
        """Returns active composite formula for Mode 1."""
        return COMPOSITE_CATALOG[self.composite_index]

    @property
    def preset_2d(self) -> Preset2D:
        """Returns active 2D preset specification."""
        return PRESETS_2D[self.preset_index_2d]

    @property
    def active_palette(self) -> PaletteEntry:
        """Returns active palette tuple with dynamic inversion applied."""
        name, raw_lut, desc = self.palettes[self.active_palette_index]
        if not self.is_inverted or raw_lut is None:
            return name, raw_lut, desc

        display_name = f"[INV] {name}"
        inverted_lut = invert_lut(raw_lut)
        return display_name, inverted_lut, desc

    def mark_scrubbing(self) -> None:
        """Engages coarse scrubbing mode and resets the settle timer."""
        self.is_scrubbing = True
        self.scrub_timer = config.SCRUB_SETTLE_DELAY
        self.needs_rebuild_1d = True
        self.needs_rebuild_2d = True

    def mark_discrete_change(self) -> None:
        """Cancels active scrubbing and marks viewports for crisp rebuild."""
        self.is_scrubbing = False
        self.scrub_timer = 0.0
        self.needs_rebuild_1d = True
        self.needs_rebuild_2d = True

    def settle_scrubbing(self) -> None:
        """Immediately settles active scrubbing into full-detail rebuild."""
        if not self.is_scrubbing:
            return
        self.is_scrubbing = False
        self.scrub_timer = 0.0
        self.needs_rebuild_1d = True
        self.needs_rebuild_2d = True

    def tick_timers(self, dt: float) -> None:
        """Advances settle debounce timer and triggers final refinement."""
        if not self.is_scrubbing:
            return

        self.scrub_timer -= dt
        if self.scrub_timer <= 0.0:
            self.settle_scrubbing()

    def reset_wave_channels(self, reset_all: bool) -> None:
        """Restores focused or all wave cycles and spatial offsets."""
        all_channels = reset_all or (self.selected_panel_index == 3)
        if all_channels or self.selected_panel_index == 0:
            self.base_cycles = config.DEFAULT_BASE_CYCLES
            self.base_offset_x = 0.0
            self.base_offset_y = 0.0
        if all_channels or self.selected_panel_index == 1:
            self.relief_cycles = config.DEFAULT_RELIEF_CYCLES
            self.relief_offset_x = 0.0
            self.relief_offset_y = 0.0
        if all_channels or self.selected_panel_index == 2:
            self.crust_cycles = config.DEFAULT_CRUST_CYCLES
            self.crust_offset_x = 0.0
            self.crust_offset_y = 0.0

        self.mark_discrete_change()

    def cycle_formula_1d(self, direction: int) -> None:
        """Cycles 1D composite catalog and syncs corresponding 2D preset."""
        self.composite_index = (
            self.composite_index + direction
        ) % len(COMPOSITE_CATALOG)

        for idx, p in enumerate(PRESETS_2D):
            if p.composite_index == self.composite_index:
                self.preset_index_2d = idx
                break

        self.mark_discrete_change()

    def cycle_formula_2d(self, direction: int) -> None:
        """Cycles all 2D presets and syncs 1D pointer when non-solo."""
        self.preset_index_2d = (
            self.preset_index_2d + direction
        ) % len(PRESETS_2D)

        target_comp = self.preset_2d.composite_index
        if target_comp >= 0:
            self.composite_index = target_comp

        self.mark_discrete_change()

    def cycle_palette(self, direction: int) -> None:
        """Cycles active color palette forward or backward."""
        self.active_palette_index = (
            self.active_palette_index + direction
        ) % len(self.palettes)
        self.mark_discrete_change()

    def toggle_inversion(self) -> None:
        """Toggles color ramp inversion on and off."""
        self.is_inverted = not self.is_inverted
        self.mark_discrete_change()

    def toggle_perspective(self) -> None:
        """Toggles spatial perspective between standard/radial and warped."""
        self.is_warped = not self.is_warped
        self.mark_discrete_change()

    def toggle_net_mode(self) -> None:
        """Toggles topographical relief net (isoline) mode on and off."""
        self.net_enabled = not self.net_enabled
        self.mark_discrete_change()

    def step_tile_size(self, direction: int) -> None:
        """Cycles tile stepping power-of-two sizes and toggles off at ends."""
        if direction > 0:
            if not self.tile_stepping_enabled:
                self.tile_stepping_enabled = True
                self.tile_size = config.MIN_TILE_SIZE
            else:
                next_size = self.tile_size * 2
                if next_size > config.MAX_TILE_SIZE:
                    self.tile_stepping_enabled = False
                else:
                    self.tile_size = next_size
        else:
            if not self.tile_stepping_enabled:
                self.tile_stepping_enabled = True
                self.tile_size = config.MAX_TILE_SIZE
            else:
                next_size = self.tile_size // 2
                if next_size < config.MIN_TILE_SIZE:
                    self.tile_stepping_enabled = False
                else:
                    self.tile_size = next_size

        self.mark_discrete_change()

    def sync_to_mode(self, mode: int) -> None:
        """Aligns active formula and clears hitboxes on viewport switch."""
        self.active_mode = mode
        self.channel_hitboxes.clear()
        if mode == 1 and self.preset_2d.composite_index < 0:
            self.composite_index = 0
            for idx, p in enumerate(PRESETS_2D):
                if p.composite_index == 0:
                    self.preset_index_2d = idx
                    break
        self.mark_discrete_change()
