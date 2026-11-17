"""Base rendering helpers and shared HUD card components."""

from typing import Dict, List, Optional, Tuple
import pygame
import config


class BaseRenderer:
    """Provides shared typography and padded HUD background blitting."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Initializes typography resources and card surface cache."""
        self.screen: pygame.Surface = screen
        self.width: int = screen.get_width()
        self.height: int = screen.get_height()
        self.font: pygame.font.Font = pygame.font.SysFont(
            "monospace", 13, bold=True
        )
        self._card_bg_cache: Dict[
            Tuple[int, int, Tuple[int, int, int, int]], pygame.Surface
        ] = {}

    def get_translucent_card_surface(
        self,
        width: int,
        height: int,
        bg_rgba: Tuple[int, int, int, int],
    ) -> pygame.Surface:
        """Returns cached translucent surface for given size and RGBA."""
        key = (width, height, bg_rgba)
        cached = self._card_bg_cache.get(key)
        if cached is not None:
            return cached

        if len(self._card_bg_cache) >= 32:
            self._card_bg_cache.clear()

        bg_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        bg_surf.fill(bg_rgba)
        self._card_bg_cache[key] = bg_surf
        return bg_surf

    def draw_card(
        self,
        x: int,
        y: int,
        lines: List[Tuple[str, Tuple[int, int, int]]],
        bg_rgba: Tuple[int, int, int, int],
        pad: int = 8,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 2,
    ) -> int:
        """Renders dynamic auto-sizing card and returns its total height."""
        rendered = [
            self.font.render(text, True, color) for text, color in lines
        ]
        line_h = self.font.get_linesize()
        max_w = max(surf.get_width() for surf in rendered)

        box_w = max_w + (pad * 2)
        box_h = (len(rendered) * line_h) + (pad * 2)

        bg_surf = self.get_translucent_card_surface(box_w, box_h, bg_rgba)
        self.screen.blit(bg_surf, (x, y))

        if border_color is not None:
            pygame.draw.rect(
                self.screen,
                border_color,
                (x, y, box_w, box_h),
                border_width,
            )

        for idx, surf in enumerate(rendered):
            self.screen.blit(surf, (x + pad, y + pad + (idx * line_h)))

        return box_h

    def draw_studio_footer(self, active_mode: int = 1) -> None:
        """Renders combined two-line studio nav and controls card."""
        pad = 6
        line_gap = 4
        line_h = self.font.get_linesize()

        segments = self._build_footer_segments(active_mode)
        nav_w = sum(surf.get_width() for surf, _ in segments)

        ctrl_str = self._build_footer_controls_text(active_mode)
        ctrl_surf = self.font.render(
            ctrl_str, True, config.COLOR_HUD_TEXT_NORMAL
        )

        box_w = max(nav_w, ctrl_surf.get_width()) + (pad * 2)
        box_h = (2 * line_h) + line_gap + (pad * 2)
        rx = 10
        ry = self.height - box_h - 10

        bg_surf = self.get_translucent_card_surface(
            box_w, box_h, config.COLOR_HUD_CARD_2D
        )
        self.screen.blit(bg_surf, (rx, ry))

        self._draw_footer_nav_line(segments, rx + pad, ry + pad, line_h)
        self.screen.blit(
            ctrl_surf, (rx + pad, ry + pad + line_h + line_gap)
        )

    def _build_footer_segments(
        self,
        active_mode: int,
    ) -> List[Tuple[pygame.Surface, bool]]:
        """Renders footer mode tags and marks the active mode segment."""
        mode_tags = (
            ("[1] Wave Math", 1),
            ("[2] 2D Strata", 2),
        )
        prefix_surf = self.font.render(
            "STUDIO: ", True, config.COLOR_HUD_TEXT_ACTIVE
        )
        pipe_surf = self.font.render(
            " | ", True, config.COLOR_HUD_TEXT_MUTED
        )

        segments: List[Tuple[pygame.Surface, bool]] = [(prefix_surf, False)]
        for idx, (lbl, mid) in enumerate(mode_tags):
            if idx > 0:
                segments.append((pipe_surf, False))
            is_active = mid == active_mode
            color = (
                config.COLOR_HUD_TEXT_ACTIVE
                if is_active
                else config.COLOR_HUD_TEXT_NORMAL
            )
            surf = self.font.render(lbl, True, color)
            segments.append((surf, is_active))

        return segments

    def _build_footer_controls_text(self, active_mode: int) -> str:
        """Formats context-sensitive control hints for the active mode."""
        persp_str = "[P]: Persp | " if active_mode == 2 else ""
        return (
            f"[1/2]: View | [TAB]: Formula | "
            f"[LMB/RMB/Arrows]: Nav/Zoom (+SHIFT: Layer) | "
            f"[SPACE]: Step | [C/I]: Palette | {persp_str}"
            f"[N]: Net | [R]: Reset"
        )

    def _draw_footer_nav_line(
        self,
        segments: List[Tuple[pygame.Surface, bool]],
        start_x: int,
        start_y: int,
        line_h: int,
    ) -> None:
        """Blits mode segments and frames the active mode in selection blue."""
        curr_x = start_x
        for surf, is_active in segments:
            self.screen.blit(surf, (curr_x, start_y))
            if is_active:
                rect = (
                    curr_x - 3,
                    start_y - 1,
                    surf.get_width() + 6,
                    line_h + 2,
                )
                pygame.draw.rect(
                    self.screen,
                    config.COLOR_SELECTION,
                    rect,
                    2,
                )
            curr_x += surf.get_width()
