"""Runtime and tuning settings for the wave math inspector."""

APP_TITLE: str = "PySineBlend - Wave Math Inspector"  # title
SCREEN_WIDTH: int = 1760  # pixels
SCREEN_HEIGHT: int = 990  # pixels
FPS: int = 60  # hertz
BACKGROUND_COLOR: tuple[int, int, int] = (255, 255, 255)  # rgb

# ------ Viewport & Stepping Modes ------
DEFAULT_VIEW_MODE: int = 1  # mode
DEFAULT_TILE_SIZE: int = 8  # pixels
MIN_TILE_SIZE: int = 8  # pixels
MAX_TILE_SIZE: int = 32  # pixels
WARP_FACTOR: float = 0.15  # fraction

# ------ Relief Net (Isoline) Settings ------
DEFAULT_NET_ENABLED: bool = False  # toggle
DEFAULT_NET_INTERVALS: float = 9.0  # intervals
DEFAULT_NET_BANDWIDTH: float = 0.005  # fraction
COLOR_NET_BACKGROUND: tuple[int, int, int] = (10, 12, 18)  # rgb

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
BASE_MIN_CYCLES: float = 1.0  # cycles
BASE_MAX_CYCLES: float = 100.0  # cycles
RELIEF_MIN_CYCLES: float = 0.5  # cycles
RELIEF_MAX_CYCLES: float = 30.0  # cycles
CRUST_MIN_CYCLES: float = 0.25  # cycles
CRUST_MAX_CYCLES: float = 20.0  # cycles

# ------ Interactive Scrubbing Throttling ------
SCRUB_SUB_SAMPLE_FACTOR: int = 4  # divider
SCRUB_SETTLE_DELAY: float = 0.12  # seconds

# ------ Interface Colors & Metrics ------
COLOR_PANEL_DIVIDER: tuple[int, int, int] = (200, 205, 215)  # rgb
COLOR_GRID: tuple[int, int, int] = (230, 233, 240)  # rgb
COLOR_WAVE: tuple[int, int, int] = (20, 25, 35)  # rgb
COLOR_SILENCED_WAVE: tuple[int, int, int] = (185, 190, 200)  # rgb
COLOR_SELECTION: tuple[int, int, int] = (35, 105, 225)  # rgb
COLOR_TITLE: tuple[int, int, int] = (25, 30, 40)  # rgb
COLOR_MUTED_TITLE: tuple[int, int, int] = (130, 135, 145)  # rgb
COLOR_TITLE_CARD: tuple[int, int, int, int] = (255, 255, 255, 230)  # rgba
COLOR_HUD_CARD_2D: tuple[int, int, int, int] = (15, 15, 20, 210)  # rgba
COLOR_HUD_TEXT_ACTIVE: tuple[int, int, int] = (255, 220, 80)  # rgb
COLOR_HUD_TEXT_NORMAL: tuple[int, int, int] = (220, 220, 220)  # rgb

# ------ Panel Dimensions & Thickness ------
PANEL_COUNT: int = 4  # panels
PANEL_TOP_MARGIN: int = 36  # pixels
PANEL_BOTTOM_MARGIN: int = 14  # pixels
PANEL_COMPOSITE_BOTTOM_MARGIN: int = 38  # pixels
PANEL_TITLE_X: int = 20  # pixels
PANEL_TITLE_Y: int = 4  # pixels
PANEL_TITLE_TEXT_X: int = 8  # pixels
PANEL_TITLE_TEXT_Y: int = 3  # pixels
PANEL_DIVIDER_WIDTH: int = 1  # pixels
PANEL_SELECTION_WIDTH: int = 2  # pixels
COMPONENT_LINE_WIDTH: int = 2  # pixels
COMPOSITE_LINE_WIDTH: int = 3  # pixels
