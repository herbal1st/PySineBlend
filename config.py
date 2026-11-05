"""Runtime and tuning settings for the standalone wave inspector."""

APP_TITLE: str = "PySineBlend - 1D Wave Math Inspector"  # text
SCREEN_WIDTH: int = 1760  # pixels
SCREEN_HEIGHT: int = 990  # pixels
FPS: int = 60  # hertz
BACKGROUND_COLOR: tuple[int, int, int] = (255, 255, 255)  # rgb

DEFAULT_BASE_CYCLES: float = 35.0  # cycles
DEFAULT_RELIEF_CYCLES: float = 6.0  # cycles
DEFAULT_CRUST_CYCLES: float = 2.5  # cycles

BASE_START: float = 0.50  # height
RELIEF_START: float = 1.00  # height
CRUST_START: float = 0.00  # height

CRUST_BUDGET: float = 0.35  # fraction
RELIEF_BUDGET: float = 0.65  # fraction
MIN_RELIEF_FACTOR: float = 0.05  # fraction

CYCLE_ZOOM_RATE: float = 0.75  # per_second

BASE_MIN_CYCLES: float = 1.0  # cycles
BASE_MAX_CYCLES: float = 100.0  # cycles
RELIEF_MIN_CYCLES: float = 0.5  # cycles
RELIEF_MAX_CYCLES: float = 30.0  # cycles
CRUST_MIN_CYCLES: float = 0.5  # cycles
CRUST_MAX_CYCLES: float = 20.0  # cycles

COLOR_PANEL_DIVIDER: tuple[int, int, int] = (200, 205, 215)  # rgb
COLOR_GRID: tuple[int, int, int] = (230, 233, 240)  # rgb
COLOR_WAVE: tuple[int, int, int] = (20, 25, 35)  # rgb
COLOR_SILENCED_WAVE: tuple[int, int, int] = (185, 190, 200)  # rgb
COLOR_SELECTION: tuple[int, int, int] = (35, 105, 225)  # rgb
COLOR_TITLE: tuple[int, int, int] = (25, 30, 40)  # rgb
COLOR_MUTED_TITLE: tuple[int, int, int] = (130, 135, 145)  # rgb
COLOR_TITLE_CARD: tuple[int, int, int, int] = (255, 255, 255, 230)  # rgba

PANEL_COUNT: int = 4  # panels
PANEL_TOP_MARGIN: int = 36  # pixels
PANEL_BOTTOM_MARGIN: int = 14  # pixels
PANEL_TITLE_X: int = 20  # pixels
PANEL_TITLE_Y: int = 4  # pixels
PANEL_TITLE_TEXT_X: int = 8  # pixels
PANEL_TITLE_TEXT_Y: int = 3  # pixels
PANEL_DIVIDER_WIDTH: int = 1  # pixels
PANEL_SELECTION_WIDTH: int = 2  # pixels
COMPONENT_LINE_WIDTH: int = 2  # pixels
COMPOSITE_LINE_WIDTH: int = 3  # pixels
