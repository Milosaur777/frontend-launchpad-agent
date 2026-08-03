"""Navigation sidebar for the trading bot dashboard."""

import tkinter as tk

from ui.config import (
    SIDEBAR_BG,
    SURFACE,
    SURFACE_HOVER,
    SURFACE_ACTIVE,
    BORDER,
    BORDER_VISIBLE,
    BORDER_ACCENT,
    ACCENT,
    ACCENT_DIM,
    TEXT,
    TEXT_DIM,
    TEXT_MID,
    TEXT_BRIGHT,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_SM,
    FONT_SIZE_LG,
    SIDEBAR_WIDTH,
    PAD_X,
    PAD_Y,
)


class Sidebar(tk.Frame):
    """Navigation sidebar with menu items and bot status."""
    
    MENU_ITEMS = [
        ("dashboard", "Dashboard", "◈"),
        ("watchlist", "Watchlist", "◎"),
        ("sniper", "Robinhood Sniper", "⊕"),
        ("positions", "Positions", "◫"),
        ("trades", "Trade History", "◧"),
        ("ml", "ML Status", "◉"),
        ("journal", "Journal", "◬"),
        ("settings", "Settings", "⚙"),
    ]
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SIDEBAR_BG, width=SIDEBAR_WIDTH, highlightbackground=BORDER_VISIBLE, highlightthickness=1)
        self.app = app
        self._buttons = {}
        self._selected = "dashboard"
        
        self.pack(side=tk.LEFT, fill=tk.Y)
        self.pack_propagate(False)
        
        self._build_header()
        self._build_menu()
        self._build_status()
    
    def _build_header(self):
        """Build sidebar header."""
        header = tk.Frame(self, bg=SIDEBAR_BG)
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y * 2, PAD_Y))
        
        title = tk.Label(
            header,
            text="NAVIGATION",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg=TEXT_MID,
            bg=SIDEBAR_BG,
        )
        title.pack(anchor="w")
    
    def _build_menu(self):
        """Build navigation menu buttons."""
        self.menu_frame = tk.Frame(self, bg=SIDEBAR_BG)
        self.menu_frame.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        for key, label, icon in self.MENU_ITEMS:
            btn = self._create_menu_button(key, label, icon)
            btn.pack(fill=tk.X, pady=4)  # Increased padding
            self._buttons[key] = btn
        
        self._update_selection("dashboard")
    
    def _create_menu_button(self, key, label, icon):
        """Create a single menu button."""
        btn = tk.Frame(self.menu_frame, bg=SIDEBAR_BG, cursor="hand2", padx=8, pady=6)
        
        icon_lbl = tk.Label(
            btn,
            text=icon,
            font=(FONT_FAMILY, FONT_SIZE_LG, "normal"),
            fg=TEXT_DIM,
            bg=SIDEBAR_BG,
            width=2,
        )
        icon_lbl.pack(side=tk.LEFT, padx=(0, 6))
        
        label_lbl = tk.Label(
            btn,
            text=label,
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg=TEXT,
            bg=SIDEBAR_BG,
        )
        label_lbl.pack(side=tk.LEFT, padx=(0, 8))
        
        # Bind hover to the entire frame and its children
        for widget in [btn, icon_lbl, label_lbl]:
            widget.bind("<Enter>", lambda e, b=btn, i=icon_lbl, l=label_lbl: self._on_hover(b, i, l, True))
            widget.bind("<Leave>", lambda e, b=btn, i=icon_lbl, l=label_lbl: self._on_hover(b, i, l, False))
            widget.bind("<Button-1>", lambda e, k=key: self._on_select(k))
        
        return btn
    
    def _on_hover(self, btn, icon_lbl, label_lbl, entering):
        """Handle menu button hover with reduced flicker."""
        key = None
        for k, b in self._buttons.items():
            if b == btn:
                key = k
                break
        
        if key == self._selected:
            return
        
        # Get current bg to avoid unnecessary updates
        current_bg = btn.cget("bg")
        
        if entering:
            if current_bg != SURFACE_HOVER:
                btn.config(bg=SURFACE_HOVER)
                icon_lbl.config(bg=SURFACE_HOVER, fg=TEXT)
                label_lbl.config(bg=SURFACE_HOVER, fg=TEXT_BRIGHT)
        else:
            if current_bg != SIDEBAR_BG:
                btn.config(bg=SIDEBAR_BG)
                icon_lbl.config(bg=SIDEBAR_BG, fg=TEXT_DIM)
                label_lbl.config(bg=SIDEBAR_BG, fg=TEXT)
    
    def _on_select(self, key):
        """Handle menu selection."""
        self._selected = key
        self._update_selection(key)
        self.app.show_view(key)
    
    def _update_selection(self, key):
        """Update visual selection state."""
        for k, btn in self._buttons.items():
            # Find child widgets
            icon_lbl = btn.winfo_children()[0]
            label_lbl = btn.winfo_children()[1]
            
            if k == key:
                btn.config(bg=ACCENT_DIM, highlightbackground=BORDER_ACCENT, highlightthickness=1)
                icon_lbl.config(bg=ACCENT_DIM, fg=ACCENT)
                label_lbl.config(bg=ACCENT_DIM, fg=TEXT_BRIGHT)
            else:
                btn.config(bg=SIDEBAR_BG, highlightbackground=SIDEBAR_BG, highlightthickness=0)
                icon_lbl.config(bg=SIDEBAR_BG, fg=TEXT_DIM)
                label_lbl.config(bg=SIDEBAR_BG, fg=TEXT)
    
    def _build_status(self):
        """Build bot status section at bottom of sidebar."""
        self.status_frame = tk.Frame(self, bg=SURFACE, highlightbackground=BORDER, highlightthickness=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        status_title = tk.Label(
            self.status_frame,
            text="BOT STATUS",
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
            fg=TEXT_MID,
            bg=SURFACE,
        )
        status_title.pack(anchor="w", padx=10, pady=(8, 4))
        
        self.status_value = tk.Label(
            self.status_frame,
            text="STOPPED",
            font=(FONT_FAMILY, FONT_SIZE_LG, "bold"),
            fg=TEXT_DIM,
            bg=SURFACE,
        )
        self.status_value.pack(anchor="w", padx=10, pady=(0, 2))
        
        self.mode_value = tk.Label(
            self.status_frame,
            text="Mode: —",
            font=(FONT_FAMILY, FONT_SIZE_SM, "normal"),
            fg=TEXT_MID,
            bg=SURFACE,
        )
        self.mode_value.pack(anchor="w", padx=10, pady=(0, 8))
    
    def set_status(self, running, mode="PAPER"):
        """Update bot status display."""
        if running:
            self.status_value.config(text="RUNNING", fg=ACCENT)
        else:
            self.status_value.config(text="STOPPED", fg=TEXT_DIM)
        
        self.mode_value.config(text=f"Mode: {mode}")
    
    def select_view(self, key):
        """Programmatically select a view."""
        self._on_select(key)
