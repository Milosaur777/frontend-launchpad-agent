"""Configuration: colors, paths, constants for AI Watermark Cleaner."""

from __future__ import annotations

import json
from pathlib import Path

# ── Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
SETTINGS_FILE = BASE_DIR / "settings.json"
ASSETS_DIR = Path(__file__).parent / "assets"

DEFAULT_INPUT_DIR = BASE_DIR / "input"
DEFAULT_OUTPUT_DIR = BASE_DIR / "output"

SUPPORTED_FORMATS = {
    ".png", ".jpg", ".jpeg", ".avif", ".webp",
    ".heif", ".heic", ".bmp", ".tiff", ".tif",
}

# ── Window ─────────────────────────────────────────────
APP_TITLE = "AI Image Cleaner"
DEFAULT_WIDTH = 1300
DEFAULT_HEIGHT = 850
MIN_WIDTH = 1000
MIN_HEIGHT = 650
SIDEBAR_WIDTH = 340

# ── Sci-Fi Dark Theme ───────────────────────────
BG = "#08080a"
BG_SECONDARY = "#0a0a0d"
SURFACE = "#111115"
SURFACE_LIGHT = "#16161a"
SURFACE_CARD = "#131318"
SURFACE_HOVER = "#1c1c22"
SURFACE_ACTIVE = "#222228"

# Borders - MORE VISIBLE
BORDER = "#1e1e24"
BORDER_LIGHT = "#2a2a32"
BORDER_VISIBLE = "#2a3d35"  # Visible accent border (6-digit hex only!)
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

TITLEBAR_HEIGHT = 44
SIDEBAR_BG = "#0c0c10"
LOG_BG = "#0a0a0d"
PROGRESS_BG = "#1a1a1e"
PROGRESS_FILL = "#33CC99"
PROGRESS_SEGMENTS = 40

# ── Fonts ──────────────────────────────────────────────
# BIGGER FONTS
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"
FONT_SIZE = 12
FONT_SIZE_SM = 10
FONT_SIZE_LG = 14
FONT_SIZE_XL = 16
FONT_SIZE_TITLE = 20

# ── Rounded corners ────────────────────────────────────
CORNER_RADIUS = 10
CARD_RADIUS = 12

# ── Settings persistence ───────────────────────────────
def load_settings() -> dict:
    """Load saved settings from disk."""
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def save_settings(settings: dict) -> None:
    """Persist settings to disk."""
    try:
        SETTINGS_FILE.write_text(
            json.dumps(settings, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


def get_last_input() -> Path:
    s = load_settings()
    p = Path(s.get("input_dir", str(DEFAULT_INPUT_DIR)))
    return p if p.is_dir() else DEFAULT_INPUT_DIR


def get_last_output() -> Path:
    s = load_settings()
    p = Path(s.get("output_dir", str(DEFAULT_OUTPUT_DIR)))
    return p if p.is_dir() else DEFAULT_OUTPUT_DIR


def set_last_input(path: Path) -> None:
    s = load_settings()
    s["input_dir"] = str(path)
    save_settings(s)


def set_last_output(path: Path) -> None:
    s = load_settings()
    s["output_dir"] = str(path)
    save_settings(s)
