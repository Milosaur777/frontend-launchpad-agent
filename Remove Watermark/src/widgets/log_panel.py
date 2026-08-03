"""Log panel widget — styled with custom scrollbar."""

from __future__ import annotations

import tkinter as tk

from config import (
    ACCENT, ACCENT_DIM, BG, BORDER_LIGHT, FONT_FAMILY, FONT_MONO, FONT_SIZE, FONT_SIZE_SM,
    LOG_BG, SURFACE, SURFACE_CARD, TEXT, TEXT_DIM, TEXT_MID,
)


class LogPanel(tk.Frame):
    """Scrollable log console with colored output."""

    def __init__(self, master, **kw):
        super().__init__(master, bg=SURFACE_CARD, **kw)
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=LOG_BG, highlightbackground=BORDER_LIGHT, highlightthickness=1)
        container.pack(fill=tk.BOTH, expand=True)

        # Use Canvas + Text to match sidebar/filelist scrollbar style (no arrows)
        self._log_canvas = tk.Canvas(container, bg=LOG_BG, highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL, command=self._log_canvas.yview,
                                  bg=SURFACE, troughcolor=SURFACE_CARD,
                                  activebackground=ACCENT_DIM, width=10)

        self._text_frame = tk.Frame(self._log_canvas, bg=LOG_BG)
        self._text_frame_window = self._log_canvas.create_window(0, 0, window=self._text_frame, anchor=tk.NW, tags="textwin")

        self._text = tk.Text(
            self._text_frame, bg=LOG_BG, fg=TEXT_DIM,
            font=(FONT_MONO, FONT_SIZE), relief=tk.FLAT, bd=0,
            wrap=tk.WORD, insertbackground=TEXT, selectbackground=ACCENT_DIM,
            state=tk.DISABLED, padx=12, pady=8,
        )

        self._text_frame.bind("<Configure>", lambda e: self._log_canvas.configure(scrollregion=self._log_canvas.bbox("all")))
        self._log_canvas.configure(yscrollcommand=scrollbar.set)
        self._log_canvas.bind("<Configure>", lambda e: self._log_canvas.itemconfig("textwin", width=e.width))

        self._text.pack(fill=tk.BOTH, expand=True)
        self._log_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._log_canvas.bind("<Enter>", lambda e: self._log_canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self._log_canvas.bind("<Leave>", lambda e: self._log_canvas.unbind_all("<MouseWheel>"))

        self._text.tag_configure("success", foreground="#33CC99")
        self._text.tag_configure("warning", foreground="#f59e0b")
        self._text.tag_configure("error", foreground="#ef4444")
        self._text.tag_configure("dim", foreground="#555555")
        self._text.tag_configure("accent", foreground="#33CC99")
        self._text.tag_configure("normal", foreground=TEXT_DIM)

    def append(self, message: str):
        self._text.configure(state=tk.NORMAL)
        tag = "normal"
        if "✅" in message: tag = "success"
        elif "❌" in message: tag = "error"
        elif "⚠" in message: tag = "warning"
        elif "─" in message: tag = "dim"
        elif "→" in message: tag = "accent"
        self._text.insert(tk.END, message + "\n", tag)
        self._text.see(tk.END)
        self._text.configure(state=tk.DISABLED)

    def clear(self):
        self._text.configure(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.configure(state=tk.DISABLED)

    def _on_mousewheel(self, event):
        self._log_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
