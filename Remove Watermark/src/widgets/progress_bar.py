"""Custom segmented progress bar widget — sci-fi style with visible border."""

from __future__ import annotations

import tkinter as tk

from config import (
    ACCENT, ACCENT_DIM, BG, BORDER_LIGHT, FONT_FAMILY,
    FONT_SIZE, FONT_SIZE_SM, FONT_SIZE_LG, PROGRESS_BG,
    PROGRESS_FILL, PROGRESS_SEGMENTS, SURFACE, SURFACE_CARD, TEXT, TEXT_DIM, TEXT_MID,
)


class ProgressBar(tk.Frame):
    """Segmented progress bar with sci-fi styling and visible border."""

    def __init__(self, master, **kw):
        super().__init__(master, bg=SURFACE_CARD, **kw)
        self._progress = 0.0
        self._current = 0
        self._total = 0
        self._build_ui()

    def _build_ui(self):
        # ── Bar container with visible border ──────────
        bar_container = tk.Frame(
            self, bg=PROGRESS_BG,
            highlightbackground=BORDER_LIGHT,
            highlightthickness=1,
        )
        bar_container.pack(fill=tk.X, padx=4, pady=4)

        # ── Percentage display ─────────────────────────
        pct_frame = tk.Frame(bar_container, bg=PROGRESS_BG)
        pct_frame.pack(fill=tk.X, padx=8, pady=(8, 4))

        self._pct_label = tk.Label(
            pct_frame,
            text="0%",
            bg=PROGRESS_BG,
            fg=ACCENT,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            anchor=tk.W,
        )
        self._pct_label.pack(side=tk.LEFT)

        self._count_label = tk.Label(
            pct_frame,
            text="(0/0)",
            bg=PROGRESS_BG,
            fg=TEXT_DIM,
            font=(FONT_FAMILY, FONT_SIZE),
            anchor=tk.E,
        )
        self._count_label.pack(side=tk.RIGHT)

        # ── Segmented bar ──────────────────────────────
        bar_frame = tk.Frame(bar_container, bg=PROGRESS_BG)
        bar_frame.pack(fill=tk.X, padx=8, pady=(4, 8))

        self._segments: list[tk.Frame] = []
        for i in range(PROGRESS_SEGMENTS):
            seg = tk.Frame(
                bar_frame,
                bg=PROGRESS_BG,
                width=20,
                height=10,
            )
            seg.pack(side=tk.LEFT, padx=(0, 2))
            self._segments.append(seg)

        # ── Status row ─────────────────────────────────
        status_frame = tk.Frame(bar_container, bg=PROGRESS_BG)
        status_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self._status_label = tk.Label(
            status_frame,
            text="Ready",
            bg=PROGRESS_BG,
            fg=TEXT_DIM,
            font=(FONT_FAMILY, FONT_SIZE),
            anchor=tk.W,
        )
        self._status_label.pack(side=tk.LEFT)

        self._detail_label = tk.Label(
            status_frame,
            text="",
            bg=PROGRESS_BG,
            fg=TEXT_DIM,
            font=(FONT_FAMILY, FONT_SIZE_SM),
            anchor=tk.E,
        )
        self._detail_label.pack(side=tk.RIGHT)

    def set_progress(self, current: int, total: int):
        """Update the progress bar and labels."""
        self._current = current
        self._total = total

        if total == 0:
            self._progress = 0.0
        else:
            self._progress = current / total

        pct = int(self._progress * 100)
        self._pct_label.config(text=f"{pct}%")
        self._count_label.config(text=f"({current}/{total})")

        filled = int(self._progress * PROGRESS_SEGMENTS)
        for i, seg in enumerate(self._segments):
            if i < filled:
                seg.config(bg=PROGRESS_FILL)
            else:
                seg.config(bg=PROGRESS_BG)

        if current >= total and total > 0:
            self._status_label.config(text="All done!", fg=ACCENT)
            self._detail_label.config(text="Batch complete")
        elif current > 0:
            remaining = total - current
            self._status_label.config(text="Processing...", fg=TEXT_MID)
            self._detail_label.config(
                text=f"{current}/{total} completed  ·  {remaining} remaining",
                fg=TEXT_DIM,
            )
        else:
            self._status_label.config(text="Ready", fg=TEXT_DIM)
            self._detail_label.config(text="")

    def reset(self):
        """Reset to zero."""
        self._progress = 0.0
        self._current = 0
        self._total = 0
        self._pct_label.config(text="0%")
        self._status_label.config(text="Ready", fg=TEXT_DIM)
        self._count_label.config(text="(0/0)")
        self._detail_label.config(text="")
        for seg in self._segments:
            seg.config(bg=PROGRESS_BG)
