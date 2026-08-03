"""UI configuration: colors, fonts, spacing for the trading bot dashboard."""

from pathlib import Path

# ── Paths ────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
ASSETS_DIR = Path(__file__).parent / "assets"

# ── Window ───────────────────────────────────────────────
APP_TITLE = "PolyCryptoAlpha Trading Bot"
DEFAULT_WIDTH = 1400
DEFAULT_HEIGHT = 900
MIN_WIDTH = 1100
MIN_HEIGHT = 700
SIDEBAR_WIDTH = 280

# ── Sci-Fi Dark Theme ───────────────────────────
BG = "#08080a"
BG_SECONDARY = "#0a0a0d"
SURFACE = "#111115"
SURFACE_LIGHT = "#16161a"
SURFACE_CARD = "#131318"
SURFACE_HOVER = "#1c1c22"
SURFACE_ACTIVE = "#222228"

BORDER = "#1e1e24"
BORDER_LIGHT = "#2a2a32"
BORDER_VISIBLE = "#2a3d35"
BORDER_GLOW = "#2a3d35"
BORDER_ACCENT = "#33CC99"

ACCENT = "#33CC99"
ACCENT_DIM = "#1a6650"
ACCENT_BRIGHT = "#44e0ab"
ACCENT_GLOW = "#1a6650"
ACCENT_FAINT = "#1a3d30"

TEXT = "#e8eaed"
TEXT_DIM = "#6a6a75"
TEXT_MID = "#9999a5"
TEXT_BRIGHT = "#ffffff"

WARNING = "#f59e0b"
ERROR = "#ef4444"
SUCCESS = "#33CC99"
INFO = "#3b82f6"

TITLEBAR_HEIGHT = 44
SIDEBAR_BG = "#0c0c10"
LOG_BG = "#0a0a0d"

# ── Fonts ──────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"
FONT_SIZE = 12
FONT_SIZE_SM = 10
FONT_SIZE_LG = 14
FONT_SIZE_XL = 16
FONT_SIZE_TITLE = 20
FONT_SIZE_HERO = 28

# ── Rounded corners ────────────────────────────────────
CORNER_RADIUS = 10
CARD_RADIUS = 12

# ── Spacing ────────────────────────────────────────────
PAD_X = 16
PAD_Y = 12
CARD_PAD = 14
