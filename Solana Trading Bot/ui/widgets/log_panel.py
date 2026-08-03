"""Log panel for bot activity messages."""

import tkinter as tk

from ui.config import (
    LOG_BG,
    SURFACE,
    TEXT,
    TEXT_DIM,
    TEXT_MID,
    ACCENT,
    WARNING,
    ERROR,
    SUCCESS,
    FONT_FAMILY,
    FONT_MONO,
    FONT_SIZE,
    FONT_SIZE_SM,
    PAD_X,
    PAD_Y,
)


class LogPanel(tk.Frame):
    """Scrolling log console with color-coded messages."""
    
    def __init__(self, parent, app, height=180):
        super().__init__(parent, bg=LOG_BG)
        self.app = app
        self.height = height
        self._build_ui()
    
    def _build_ui(self):
        """Build log panel UI."""
        # Header
        header = tk.Frame(self, bg=LOG_BG)
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y // 2, 0))
        
        title = tk.Label(
            header,
            text="BOT ACTIVITY LOG",
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
            fg=TEXT_MID,
            bg=LOG_BG,
        )
        title.pack(side=tk.LEFT)
        
        self.clear_btn = tk.Label(
            header,
            text="Clear",
            font=(FONT_FAMILY, FONT_SIZE_SM, "underline"),
            fg=TEXT_DIM,
            bg=LOG_BG,
            cursor="hand2",
        )
        self.clear_btn.pack(side=tk.RIGHT)
        self.clear_btn.bind("<Button-1>", lambda e: self.clear())
        self.clear_btn.bind("<Enter>", lambda e: self.clear_btn.config(fg=TEXT))
        self.clear_btn.bind("<Leave>", lambda e: self.clear_btn.config(fg=TEXT_DIM))
        
        # Log text
        self.text = tk.Text(
            self,
            font=(FONT_MONO, FONT_SIZE),
            fg=TEXT,
            bg=LOG_BG,
            insertbackground=TEXT,
            highlightthickness=0,
            bd=0,
            wrap=tk.WORD,
            padx=8,
            pady=8,
            height=self.height // 20,
            state=tk.DISABLED,
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=PAD_X, pady=(4, PAD_Y))
        
        # Tags
        self.text.tag_configure("info", foreground=TEXT)
        self.text.tag_configure("success", foreground=SUCCESS)
        self.text.tag_configure("warning", foreground=WARNING)
        self.text.tag_configure("error", foreground=ERROR)
        self.text.tag_configure("accent", foreground=ACCENT)
        self.text.tag_configure("timestamp", foreground=TEXT_DIM)
    
    def log(self, message, level="info"):
        """Add a log message."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.text.insert(tk.END, f"{message}\n", level)
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)
    
    def clear(self):
        """Clear log."""
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.config(state=tk.DISABLED)
