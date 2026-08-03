"""Top status bar showing bot state and quick controls."""

import tkinter as tk

from ui.config import (
    SURFACE,
    SURFACE_HOVER,
    BORDER,
    BORDER_ACCENT,
    ACCENT,
    ACCENT_DIM,
    TEXT,
    TEXT_DIM,
    TEXT_BRIGHT,
    ERROR,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_SM,
    PAD_X,
    PAD_Y,
)


class StatusBar(tk.Frame):
    """Top status bar with start/stop and mode indicator."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        self.app = app
        self._running = False
        self._build_ui()
    
    def _build_ui(self):
        """Build status bar UI."""
        self.pack(fill=tk.X, padx=0, pady=0)
        self.pack_propagate(False)
        self.config(height=46)
        
        # Left: status
        left = tk.Frame(self, bg=SURFACE)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=PAD_X)
        
        self.status_dot = tk.Label(left, text="●", font=(FONT_FAMILY, FONT_SIZE, "bold"), fg=TEXT_DIM, bg=SURFACE)
        self.status_dot.pack(side=tk.LEFT)
        
        self.status_text = tk.Label(left, text="Bot Stopped", font=(FONT_FAMILY, FONT_SIZE, "bold"), fg=TEXT_DIM, bg=SURFACE)
        self.status_text.pack(side=tk.LEFT, padx=(6, 12))
        
        self.mode_text = tk.Label(left, text="PAPER", font=(FONT_FAMILY, FONT_SIZE_SM, "bold"), fg=ACCENT, bg=SURFACE)
        self.mode_text.pack(side=tk.LEFT)
        
        # Center: quick info
        center = tk.Frame(self, bg=SURFACE)
        center.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        
        self.info_text = tk.Label(center, text="Ready to start", font=(FONT_FAMILY, FONT_SIZE, "normal"), fg=TEXT_DIM, bg=SURFACE)
        self.info_text.pack()
        
        # Right: controls
        right = tk.Frame(self, bg=SURFACE)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=PAD_X)
        
        self.start_btn = tk.Label(
            right,
            text="▶ START",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg=TEXT_BRIGHT,
            bg=ACCENT_DIM,
            cursor="hand2",
            padx=16,
            pady=6,
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.start_btn.bind("<Enter>", lambda e: self.start_btn.config(bg=ACCENT, fg=SURFACE))
        self.start_btn.bind("<Leave>", lambda e: self.start_btn.config(bg=ACCENT_DIM, fg=TEXT_BRIGHT))
        self.start_btn.bind("<Button-1>", lambda e: self.app.start_bot())
        
        self.stop_btn = tk.Label(
            right,
            text="■ STOP",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg=TEXT_BRIGHT,
            bg=ERROR,
            cursor="hand2",
            padx=16,
            pady=6,
        )
        self.stop_btn.pack(side=tk.LEFT)
        self.stop_btn.bind("<Enter>", lambda e: self.stop_btn.config(bg="#ff5555"))
        self.stop_btn.bind("<Leave>", lambda e: self.stop_btn.config(bg=ERROR))
        self.stop_btn.bind("<Button-1>", lambda e: self.app.stop_bot())
    
    def set_running(self, running):
        """Update running state."""
        self._running = running
        if running:
            self.status_dot.config(fg=ACCENT)
            self.status_text.config(text="Bot Running", fg=ACCENT)
            self.info_text.config(text="Actively monitoring markets")
        else:
            self.status_dot.config(fg=TEXT_DIM)
            self.status_text.config(text="Bot Stopped", fg=TEXT_DIM)
            self.info_text.config(text="Ready to start")
    
    def set_mode(self, mode):
        """Update mode display."""
        mode = mode.upper()
        self.mode_text.config(text=mode, fg=ERROR if mode == "LIVE" else ACCENT)
    
    def set_info(self, text):
        """Update info text."""
        self.info_text.config(text=text)
