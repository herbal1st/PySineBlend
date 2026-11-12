"""2D spatial synthesizer renderer generating surfaces and relief nets."""

from typing import List, Optional, Tuple
import numpy as np
from numpy.typing import NDArray
import pygame
import config
from wave_inspector.formulas import PRESETS_2D
from wave_inspector.renderers.base_renderer import BaseRenderer
from wave_inspector.state import InspectorState


class Renderer2D(BaseRenderer):
    """Bakes 2D float32 heightfield into surface or topographical net."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Initializes base renderer and surface cache."""
        super().__init__(screen)
        self.rendered_surface: pygame.Surface = pygame.Surface(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )

    def update_surface(
        self,
        heightfield: NDArray[np.float32],
        lut: Optional[NDArray[np.uint8]],
        state: InspectorState,
    ) -> None:
        """Renders either continuous colormap surface or contour net."""
        indices = np.clip(heightfield * 1023.0, 0, 1023).astype(np.int32)
        color_source = (
            lut
            if lut is not None
            else np.repeat(
                (heightfield * 255.0).astype(np.uint8)[..., np.newaxis],
                3,
                axis=-1,
            )
        )

        if state.net_enabled:
            rgb_buffer = self._bake_contour_net(
                heightfield=heightfield,
                lut=color_source,
                indices=indices,
                intervals=state.net_intervals,
                bandwidth=state.net_bandwidth,
                tile_stepping=state.tile_stepping_enabled,
            )
        else:
            rgb_buffer = color_source[indices]

        transposed_buffer = np.transpose(rgb_buffer, (1, 0, 2))
        pygame.surfarray.blit_array(self.rendered_surface, transposed_buffer)

    def _bake_contour_net(
        self,
        heightfield: NDArray[np.float32],
        lut: NDArray[np.uint8],
        indices: NDArray[np.int32],
        intervals: float,
        bandwidth: float,
        tile_stepping: bool,
    ) -> NDArray[np.uint8]:
        """Synthesizes contour lines via cell-crossing or tolerance bands."""
        bg_rgb = np.array(config.COLOR_NET_BACKGROUND, dtype=np.uint8)
        buffer = np.full(
            (self.height, self.width, 3),
            bg_rgb,
            dtype=np.uint8,
        )

        count = max(1, int(round(intervals))) + 1
        levels = np.linspace(0.0, 1.0, count, dtype=np.float32)

        if tile_stepping:
            h_left = np.roll(heightfield, 1, axis=1)
            h_right = np.roll(heightfield, -1, axis=1)
            h_up = np.roll(heightfield, 1, axis=0)
            h_down = np.roll(heightfield, -1, axis=0)

            h_min = np.minimum.reduce(
                [heightfield, h_left, h_right, h_up, h_down]
            )
            h_max = np.maximum.reduce(
                [heightfield, h_left, h_right, h_up, h_down]
            )

            for lvl in levels:
                lvl_idx = int(np.clip(lvl * 1023.0, 0, 1023))
                lvl_color = lut[lvl_idx]

                if lvl <= 0.001:
                    mask = (heightfield <= bandwidth) | (h_min <= 0.001)
                elif lvl >= 0.999:
                    mask = (heightfield >= 1.0 - bandwidth) | (h_max >= 0.999)
                else:
                    mask = (h_min <= lvl) & (lvl <= h_max)

                buffer[mask] = lvl_color
        else:
            contour_mask = np.zeros((self.height, self.width), dtype=bool)
            for lvl in levels:
                diff = np.abs(heightfield - lvl)
                contour_mask |= diff <= bandwidth

            colored_pixels = lut[indices]
            buffer[contour_mask] = colored_pixels[contour_mask]

        return buffer

    def render(self, state: InspectorState, fps: float) -> None:
        """Blits baked 2D surface, metadata, and controls."""
        self.screen.blit(self.rendered_surface, (0, 0))
        self._draw_hud(state, fps)
        self.draw_controls_card(is_dark_theme=True)

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
