"""Mutable runtime selections and tuning state for the inspector."""

from dataclasses import dataclass, field
from typing import List
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
    """Holds active viewport, formula pointers, channel focus, and cycles."""

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
    tile_stepping_enabled: bool = False
    tile_size: int = config.DEFAULT_TILE_SIZE
    needs_rebuild_2d: bool = True
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

    def cycle_formula_1d(self, direction: int) -> None:
        """Cycles 1D composite catalog and syncs corresponding 2D preset."""
        self.composite_index = (
            self.composite_index + direction
        ) % len(COMPOSITE_CATALOG)

        for idx, p in enumerate(PRESETS_2D):
            if p.composite_index == self.composite_index:
                self.preset_index_2d = idx
                break

        self.needs_rebuild_2d = True

    def cycle_formula_2d(self, direction: int) -> None:
        """Cycles all 2D presets and syncs 1D pointer when non-solo."""
        self.preset_index_2d = (
            self.preset_index_2d + direction
        ) % len(PRESETS_2D)

        target_comp = self.preset_2d.composite_index
        if target_comp >= 0:
            self.composite_index = target_comp

        self.needs_rebuild_2d = True

    def cycle_palette(self, direction: int) -> None:
        """Cycles active color palette forward or backward."""
        self.active_palette_index = (
            self.active_palette_index + direction
        ) % len(self.palettes)
        self.needs_rebuild_2d = True

    def toggle_inversion(self) -> None:
        """Toggles color ramp inversion on and off."""
        self.is_inverted = not self.is_inverted
        self.needs_rebuild_2d = True

    def toggle_perspective(self) -> None:
        """Toggles spatial perspective between standard/radial and warped."""
        self.is_warped = not self.is_warped
        self.needs_rebuild_2d = True

    def toggle_net_mode(self) -> None:
        """Toggles topographical relief net (isoline) mode on and off."""
        self.net_enabled = not self.net_enabled
        self.needs_rebuild_2d = True

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

        self.needs_rebuild_2d = True

    def sync_to_mode(self, mode: int) -> None:
        """Aligns active formula when toggling viewports."""
        self.active_mode = mode
        if mode == 1:
            if self.preset_2d.composite_index < 0:
                self.composite_index = 0
                for idx, p in enumerate(PRESETS_2D):
                    if p.composite_index == 0:
                        self.preset_index_2d = idx
                        break
        else:
            self.needs_rebuild_2d = True
