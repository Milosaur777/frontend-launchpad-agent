"""Overwrite dialog — modal popup with three choices, bigger fonts."""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from config import (
    ACCENT, BG, BORDER, BORDER_LIGHT, FONT_FAMILY, FONT_SIZE, FONT_SIZE_SM, FONT_SIZE_LG,
    SURFACE, SURFACE_HOVER, TEXT, TEXT_DIM, TEXT_MID, ERROR, WARNING,
)


class OverwriteDialog(tk.Toplevel):
    """Modal dialog asking the user how to handle an existing file."""

    def __init__(self, master, filename: str, **kw):
        super().__init__(master, **kw)
        self.result: str | None = None

        self.title("File Exists")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        w, h = 460, 260
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui(filename)

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window()

    def _build_ui(self, filename: str):
        # ── Header ─────────────────────────────────────
        header = tk.Frame(self, bg=SURFACE)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="  ⚠  File Already Exists",
            bg=SURFACE,
            fg=WARNING,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            anchor=tk.W,
            pady=14,
        ).pack(fill=tk.X, padx=12)

        # ── Body ───────────────────────────────────────
        body = tk.Frame(self, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=24, pady=(20, 0))

        tk.Label(
            body,
            text=f'"{filename}"',
            bg=BG,
            fg=TEXT,
            font=(FONT_FAMILY, FONT_SIZE),
            wraplength=400,
        ).pack(anchor=tk.W)

        tk.Label(
            body,
            text="already exists in the output folder.",
            bg=BG,
            fg=TEXT_DIM,
            font=(FONT_FAMILY, FONT_SIZE),
        ).pack(anchor=tk.W, pady=(6, 0))

        # ── Buttons ────────────────────────────────────
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(fill=tk.X, padx=24, pady=(24, 20))

        buttons = [
            ("Overwrite", "overwrite", ACCENT, "#000000"),
            ("Add Number", "number", SURFACE, TEXT),
            ("Cancel", "cancel", BG, ERROR),
        ]

        for label, value, bg_color, fg_color in buttons:
            btn = tk.Button(
                btn_frame,
                text=label,
                bg=bg_color,
                fg=fg_color,
                activebackground=SURFACE_HOVER,
                activeforeground=TEXT,
                font=(FONT_FAMILY, FONT_SIZE, "bold"),
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                padx=18,
                pady=10,
                command=lambda v=value: self._choose(v),
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=SURFACE_HOVER))
            btn.bind("<Leave>", lambda e, b=btn, c=bg_color: b.config(bg=c))

    def _choose(self, value: str):
        self.result = value
        self.destroy()

    def _on_cancel(self):
        self.result = "cancel"
        self.destroy()
