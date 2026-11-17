"""Runtime and tuning settings for the wave math inspector."""

from typing import Tuple

# ------ Display & Resolution Settings ------
APP_TITLE: str = "PySineBlend - Wave Math Inspector"  # title
SCREEN_WIDTH: int = 1760  # pixels
SCREEN_HEIGHT: int = 990  # pixels
FPS: int = 60  # hertz
BACKGROUND_COLOR: Tuple[int, int, int] = (255, 255, 255)  # rgb

# ------ Viewport & Stepping Modes ------
DEFAULT_VIEW_MODE: int = 1  # mode
DEFAULT_TILE_SIZE: int = 4  # pixels
MIN_TILE_SIZE: int = 4  # pixels
MAX_TILE_SIZE: int = 16  # pixels
WARP_FACTOR: float = 0.15  # fraction

# ------ Relief Net (Isoline) Settings ------
DEFAULT_NET_ENABLED: bool = False  # toggle
DEFAULT_NET_INTERVALS: float = 9.0  # intervals
DEFAULT_NET_BANDWIDTH: float = 0.005  # fraction
COLOR_NET_BACKGROUND: Tuple[int, int, int] = (10, 12, 18)  # rgb

# ------ Wave Frequency Defaults ------
DEFAULT_BASE_CYCLES: float = 6.0  # cycles
DEFAULT_RELIEF_CYCLES: float = 5.0  # cycles
DEFAULT_CRUST_CYCLES: float = 1.5  # cycles

# ------ Starting Elevation Phase Offsets ------
BASE_START: float = 1.00  # height
RELIEF_START: float = 1.00  # height
CRUST_START: float = 1.00  # height

# ------ Mathematical Elevation Budgets ------
CRUST_BUDGET: float = 0.4  # fraction
RELIEF_BUDGET: float = 0.6  # fraction
MIN_RELIEF_FACTOR: float = 0.05  # fraction

# ------ Frequency Tuning Rates & Clamps ------
CYCLE_ZOOM_RATE: float = 0.75  # rate
MOUSE_ZOOM_SENSITIVITY: float = 0.005  # rate/px
BASE_MIN_CYCLES: float = 1.0  # cycles
BASE_MAX_CYCLES: float = 100.0  # cycles
RELIEF_MIN_CYCLES: float = 0.5  # cycles
RELIEF_MAX_CYCLES: float = 30.0  # cycles
CRUST_MIN_CYCLES: float = 0.25  # cycles
CRUST_MAX_CYCLES: float = 20.0  # cycles

# ------ Interactive Scrubbing Throttling ------
SCRUB_SUB_SAMPLE_FACTOR: int = 4  # divider
SCRUB_SETTLE_DELAY: float = 0.12  # seconds

# ------ Interface Colors ------
COLOR_PANEL_DIVIDER: Tuple[int, int, int] = (200, 205, 215)  # rgb
COLOR_GRID: Tuple[int, int, int] = (230, 233, 240)  # rgb
COLOR_WAVE: Tuple[int, int, int] = (20, 25, 35)  # rgb
COLOR_SILENCED_WAVE: Tuple[int, int, int] = (185, 190, 200)  # rgb
COLOR_SELECTION: Tuple[int, int, int] = (35, 105, 225)  # rgb
COLOR_HUD_CARD_2D: Tuple[int, int, int, int] = (15, 15, 20, 210)  # rgba
COLOR_HUD_TEXT_ACTIVE: Tuple[int, int, int] = (255, 220, 80)  # rgb
COLOR_HUD_TEXT_NORMAL: Tuple[int, int, int] = (220, 220, 220)  # rgb
COLOR_HUD_TEXT_MUTED: Tuple[int, int, int] = (130, 135, 145)  # rgb
COLOR_INPUT_ACTIVE: Tuple[int, int, int] = (80, 200, 255)  # rgb
