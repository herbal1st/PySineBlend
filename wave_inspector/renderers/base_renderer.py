"""Base rendering helpers and shared HUD card components."""

from typing import List, Optional, Tuple
import pygame
import config


class BaseRenderer:
    """Provides shared typography and padded HUD background blitting."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Initializes typography resources."""
        self.screen: pygame.Surface = screen
        self.width: int = screen.get_width()
        self.height: int = screen.get_height()
        self.font: pygame.font.Font = pygame.font.SysFont(
            "monospace", 13, bold=True
        )

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

        bg_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg_surf.fill(bg_rgba)
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

    def draw_controls_card(self, is_dark_theme: bool = False) -> None:
        """Renders standardized keyboard cheat sheet docked to bottom-left."""
        if is_dark_theme:
            text = (
                "[1/2]: View | [TAB]: Formula | "
                "[LMB/RMB]: Pan/Zoom (+SHIFT: Layer) | [SPACE]: Step | "
                "[C/I]: Pal | [P]: Persp | [N]: Net | [R]: Reset"
            )
            text_color = config.COLOR_HUD_TEXT_NORMAL
            bg_color = config.COLOR_HUD_CARD_2D
            rx = 10
        else:
            text = (
                "[1/2]: View | [TAB]: Formula | "
                "[LMB/RMB]: Pan/Zoom (+SHIFT: Layer) | [SPACE]: Step | "
                "[C/I]: Pal | [N]: Net | [R]: Reset"
            )
            text_color = config.COLOR_TITLE
            bg_color = config.COLOR_TITLE_CARD
            rx = config.PANEL_TITLE_X

        surf = self.font.render(text, True, text_color)
        box_w = surf.get_width() + 16
        box_h = surf.get_height() + 6

        bg_card = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg_card.fill(bg_color)

        ry = self.height - box_h - 10

        self.screen.blit(bg_card, (rx, ry))
        self.screen.blit(surf, (rx + 8, ry + 3))
