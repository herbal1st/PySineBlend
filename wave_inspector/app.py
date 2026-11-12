"""Application loop coordinating input, wave math, and renderers."""

from typing import Dict
import numpy as np
from numpy.typing import NDArray
import pygame
import config
from wave_inspector.input_handler import InputHandler
from wave_inspector.renderers.renderer_1d import Renderer1D
from wave_inspector.renderers.renderer_2d import Renderer2D
from wave_inspector.state import InspectorState
from wave_inspector.wave_model import (
    CoordinateMesh2D,
    build_coarse_mesh_2d,
    build_coordinate_mesh_2d,
    build_wave_frame_1d,
    build_wave_frame_2d,
)


class WaveMathInspector:
    """Coordinates window lifecycle, dual viewports, and dirty re-bakes."""

    def __init__(self) -> None:
        """Initializes Pygame, state, mesh cache, and sub-renderers."""
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(config.APP_TITLE)
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.state: InspectorState = InspectorState()
        self.input_handler: InputHandler = InputHandler()

        self.x_coordinates: NDArray[np.float32] = np.linspace(
            0.0,
            1.0,
            config.SCREEN_WIDTH,
            dtype=np.float32,
        )
        self.continuous_mesh: CoordinateMesh2D = build_coordinate_mesh_2d(
            config.SCREEN_WIDTH,
            config.SCREEN_HEIGHT,
        )
        self.coarse_meshes: Dict[int, CoordinateMesh2D] = {
            sz: build_coarse_mesh_2d(
                config.SCREEN_WIDTH, config.SCREEN_HEIGHT, sz
            )
            for sz in (8, 16, 32)
        }

        self.renderer_1d: Renderer1D = Renderer1D(self.screen)
        self.renderer_2d: Renderer2D = Renderer2D(self.screen)

    def run(self) -> None:
        """Executes main event polling, mathematical evaluation, and drawing."""
        running = True
        try:
            while running:
                raw_dt = self.clock.tick(config.FPS) / 1000.0
                dt = min(0.05, max(0.001, raw_dt))

                running = self.input_handler.handle_input(self.state, dt)
                if not running:
                    break

                self._render_active_mode()
                pygame.display.flip()
        finally:
            pygame.quit()

    def _render_active_mode(self) -> None:
        """Delegates frame generation and rendering to the active viewport."""
        _, active_lut, _ = self.state.active_palette

        if self.state.active_mode == 1:
            frame_1d = build_wave_frame_1d(
                x_coordinates=self.x_coordinates,
                formula=self.state.formula_1d,
                base_cycles=self.state.base_cycles,
                relief_cycles=self.state.relief_cycles,
                crust_cycles=self.state.crust_cycles,
                tile_stepping=self.state.tile_stepping_enabled,
                tile_size=self.state.tile_size,
            )
            self.renderer_1d.render(self.state, frame_1d)
        else:
            if self.state.needs_rebuild_2d:
                tile_sz = (
                    self.state.tile_size
                    if self.state.tile_stepping_enabled
                    else 0
                )
                mesh = (
                    self.coarse_meshes.get(tile_sz, self.continuous_mesh)
                    if self.state.tile_stepping_enabled
                    else self.continuous_mesh
                )

                heightfield_2d = build_wave_frame_2d(
                    mesh=mesh,
                    preset=self.state.preset_2d,
                    base_cycles=self.state.base_cycles,
                    relief_cycles=self.state.relief_cycles,
                    crust_cycles=self.state.crust_cycles,
                    is_warped=self.state.is_warped,
                    target_width=config.SCREEN_WIDTH,
                    target_height=config.SCREEN_HEIGHT,
                    tile_size=tile_sz,
                )
                self.renderer_2d.update_surface(
                    heightfield=heightfield_2d,
                    lut=active_lut,
                    state=self.state,
                )
                self.state.needs_rebuild_2d = False

            fps = self.clock.get_fps()
            self.renderer_2d.render(self.state, fps)


def run_app() -> None:
    """Boots the standalone wave inspector application."""
    WaveMathInspector().run()
