"""Custom titlebar widget — draggable, sci-fi glassmorphism style."""

from __future__ import annotations

import tkinter as tk
from PIL import Image, ImageTk

from config import (
    ACCENT, BG, SURFACE, SURFACE_LIGHT, TEXT, TEXT_DIM,
    FONT_FAMILY, FONT_SIZE_LG, TITLEBAR_HEIGHT, APP_TITLE, ASSETS_DIR,
)


class Titlebar(tk.Frame):
    """Custom sci-fi title bar with icon, glow effects, window controls."""

    def __init__(self, master: tk.Tk, on_close=None, on_minimize=None, **kw):
        super().__init__(master, bg=BG, height=TITLEBAR_HEIGHT, **kw)
        self.pack_propagate(False)
        self._master_win = master
        self._on_close = on_close
        self._on_minimize = on_minimize

        self._icon_photo = None
        try:
            icon_path = ASSETS_DIR / "icon.avif"
            if icon_path.exists():
                img = Image.open(icon_path)
                img = img.resize((28, 28), Image.LANCZOS)
                self._icon_photo = ImageTk.PhotoImage(img)
        except Exception:
            pass

        # ── Left: icon + title ─────────────────────────
        left = tk.Frame(self, bg=BG)
        left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 0))

        if self._icon_photo:
            icon_label = tk.Label(left, image=self._icon_photo, bg=BG)
            icon_label.pack(side=tk.LEFT, padx=(0, 10))

        self._title = tk.Label(
            left,
            text=APP_TITLE,
            bg=BG,
            fg=ACCENT,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            anchor=tk.W,
        )
        self._title.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ── Right: window controls ─────────────────────
        right = tk.Frame(self, bg=BG)
        right.pack(side=tk.RIGHT, padx=(0, 8))

        def make_btn(parent, text, cmd, fg_color=TEXT_DIM, active_bg=SURFACE_LIGHT, active_fg=TEXT):
            b = tk.Button(
                parent,
                text=text,
                bg=BG,
                fg=fg_color,
                font=(FONT_FAMILY, 14),
                width=4,
                height=1,
                relief=tk.FLAT,
                bd=0,
                activebackground=active_bg,
                activeforeground=active_fg,
                cursor="hand2",
                command=cmd,
            )
            return b

        self._btn_min = make_btn(right, "─", self._minimize)
        self._btn_min.pack(side=tk.LEFT, padx=2)

        self._btn_max = make_btn(right, "▢", self._maximize)
        self._btn_max.pack(side=tk.LEFT, padx=2)

        self._btn_close = make_btn(
            right, "✕", self._close,
            fg_color="#ef4444",
            active_bg="#ef4444",
            active_fg="#ffffff",
        )
        self._btn_close.pack(side=tk.LEFT, padx=2)

        # ── Glow line at bottom ────────────────────────
        self._glow_line = tk.Frame(self, bg=ACCENT, height=2)
        self._glow_line.pack(fill=tk.X, side=tk.BOTTOM)

    def _close(self):
        if self._on_close:
            self._on_close()
        else:
            self._master_win.destroy()

    def _minimize(self):
        if self._on_minimize:
            self._on_minimize()
        else:
            self._master_win.iconify()

    def _maximize(self):
        if self._master_win.state() == "zoomed":
            self._master_win.state("normal")
        else:
            self._master_win.state("zoomed")
