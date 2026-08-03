"""Custom titlebar for the trading bot dashboard."""

import tkinter as tk

from ui.config import (
    BG,
    SURFACE,
    SURFACE_LIGHT,
    SURFACE_HOVER,
    SURFACE_ACTIVE,
    BORDER,
    BORDER_LIGHT,
    BORDER_ACCENT,
    ACCENT,
    ACCENT_DIM,
    TEXT,
    TEXT_DIM,
    TEXT_BRIGHT,
    ERROR,
    FONT_FAMILY,
    FONT_SIZE_LG,
    FONT_SIZE,
    TITLEBAR_HEIGHT,
)


class Titlebar(tk.Frame):
    """Custom draggable titlebar with window controls."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE, height=TITLEBAR_HEIGHT, highlightbackground=BORDER_ACCENT, highlightthickness=0)
        self.app = app
        self._offsetx = 0
        self._offsety = 0
        
        self.pack(side=tk.TOP, fill=tk.X)
        self.pack_propagate(False)
        
        # Glow line at bottom
        self.glow = tk.Frame(self, bg=ACCENT_DIM, height=1)
        self.glow.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Title (no icon — Windows .exe icon is set via PyInstaller)
        self.title_lbl = tk.Label(
            self,
            text="PolyCryptoAlpha",
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            fg=TEXT_BRIGHT,
            bg=SURFACE,
        )
        self.title_lbl.pack(side=tk.LEFT)
        
        self.subtitle_lbl = tk.Label(
            self,
            text="Trading Bot",
            font=(FONT_FAMILY, FONT_SIZE, "normal"),
            fg=TEXT_DIM,
            bg=SURFACE,
        )
        self.subtitle_lbl.pack(side=tk.LEFT, padx=(8, 0))
        
        # Window controls
        self.controls = tk.Frame(self, bg=SURFACE)
        self.controls.pack(side=tk.RIGHT, padx=8)
        
        self._create_control("—", self.app.minimize_window, TEXT_DIM)
        self._create_control("□", self.app.maximize_window, TEXT_DIM)
        self._create_control("×", self.app.close_window, ERROR, hover_fg=TEXT_BRIGHT)
        
        # Drag bindings
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<Double-Button-1>", self._on_double_click)
        self.title_lbl.bind("<Button-1>", self._on_click)
        self.title_lbl.bind("<B1-Motion>", self._on_drag)
        self.title_lbl.bind("<Double-Button-1>", self._on_double_click)
    
    def _create_control(self, text, command, fg, hover_fg=None):
        """Create a window control button."""
        hover_fg = hover_fg or fg
        
        btn = tk.Label(
            self.controls,
            text=text,
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            fg=fg,
            bg=SURFACE,
            width=3,
            cursor="hand2",
        )
        btn.pack(side=tk.LEFT)
        
        def on_enter(e):
            btn.config(bg=SURFACE_HOVER, fg=hover_fg)
        
        def on_leave(e):
            btn.config(bg=SURFACE, fg=fg)
        
        def on_click(e):
            command()
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)
    
    def _on_click(self, event):
        self._offsetx = event.x
        self._offsety = event.y
    
    def _on_double_click(self, event):
        """Toggle maximize on double-click."""
        self.app.maximize_window()
    
    def _on_drag(self, event):
        # Use winfo_pointerx/y for positioning (works with DPI scaling)
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        
        # Clamp to screen bounds
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, min(x, screen_w - 100))
        y = max(0, min(y, screen_h - 50))
        
        self.app.geometry(f"+{x}+{y}")
