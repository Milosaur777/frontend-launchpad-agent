"""Robinhood Chain Sniper Bot panel — monitor new token launches and auto-buys."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from ui.config import (
    SURFACE,
    SURFACE_CARD,
    SURFACE_HOVER,
    BORDER_LIGHT,
    TEXT,
    TEXT_DIM,
    TEXT_MID,
    TEXT_BRIGHT,
    ACCENT,
    ACCENT_DIM,
    WARNING,
    ERROR,
    SUCCESS,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_SM,
    FONT_SIZE_LG,
    PAD_X,
    PAD_Y,
    CARD_PAD,
)
from ui.components import styled_frame, styled_label, styled_button, section_header, status_badge


class SniperView(tk.Frame):
    """Robinhood Chain sniper bot monitoring view."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE_CARD)
        self.app = app
        self._tree_items = {}
        self._build_ui()

    def _build_ui(self):
        """Build sniper UI."""
        # Header
        header = section_header(
            self,
            "Robinhood Chain Sniper",
            "Auto-detect new token launches and buy $1 each",
        )
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y, PAD_Y // 2))

        # Status bar
        stats_frame = tk.Frame(self, bg=SURFACE_CARD)
        stats_frame.pack(fill=tk.X, padx=PAD_X, pady=(0, PAD_Y))

        self.status_badge = status_badge(stats_frame, "IDLE", status="neutral")
        self.status_badge.pack(side=tk.LEFT)

        self.sniped_count = styled_label(
            stats_frame, "Sniped: 0", size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD
        )
        self.sniped_count.pack(side=tk.LEFT, padx=(12, 0))

        self.weth_spent = styled_label(
            stats_frame, "WETH Spent: 0.0000", size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD
        )
        self.weth_spent.pack(side=tk.LEFT, padx=(12, 0))

        self.success_rate = styled_label(
            stats_frame, "Success: —", size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD
        )
        self.success_rate.pack(side=tk.LEFT, padx=(12, 0))

        # Control buttons
        controls = tk.Frame(stats_frame, bg=SURFACE_CARD)
        controls.pack(side=tk.RIGHT)

        self.start_btn = styled_button(
            controls, "Start Sniper", self._on_start, variant="primary", width=14
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = styled_button(
            controls, "Stop Sniper", self._on_stop, variant="danger", width=14
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Sniped tokens table
        table_frame = styled_frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=PAD_X, pady=PAD_Y)

        columns = [
            "time", "symbol", "address", "pair", "weth_spent",
            "tokens", "status",
        ]
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )

        # Column config
        col_config = {
            "time": ("TIME", 130),
            "symbol": ("SYMBOL", 80),
            "address": ("ADDRESS", 180),
            "pair": ("PAIR", 180),
            "weth_spent": ("WETH SPENT", 100),
            "tokens": ("TOKENS", 120),
            "status": ("STATUS", 90),
        }
        for col, (heading, width) in col_config.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, minwidth=width)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=CARD_PAD)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=CARD_PAD)

        # Tag colors
        self.tree.tag_configure("holding", foreground=ACCENT)
        self.tree.tag_configure("sold", foreground=SUCCESS)
        self.tree.tag_configure("rugged", foreground=ERROR)
        self.tree.tag_configure("failed", foreground=TEXT_DIM)

        # Activity log
        log_frame = styled_frame(self)
        log_frame.pack(fill=tk.X, padx=PAD_X, pady=(0, PAD_Y))

        log_header = styled_label(
            log_frame, "ACTIVITY LOG", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD
        )
        log_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))

        self.log_text = tk.Text(
            log_frame,
            font=(FONT_FAMILY, FONT_SIZE_SM),
            fg=TEXT_MID,
            bg=SURFACE,
            insertbackground=TEXT,
            highlightbackground=BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
            height=8,
            wrap=tk.WORD,
            state=tk.DISABLED,
        )
        self.log_text.pack(fill=tk.X, padx=CARD_PAD, pady=(0, CARD_PAD))

    def _on_start(self):
        """Start the sniper bot."""
        if hasattr(self.app, "start_sniper"):
            self.app.start_sniper()

    def _on_stop(self):
        """Stop the sniper bot."""
        if hasattr(self.app, "stop_sniper"):
            self.app.stop_sniper()

    def update_status(self, running: bool):
        """Update status badge."""
        if running:
            self.status_badge = status_badge(self.status_badge.master, "RUNNING", status="success")
        else:
            self.status_badge = status_badge(self.status_badge.master, "IDLE", status="neutral")
        self.status_badge.pack(side=tk.LEFT)

    def update_stats(self, total_sniped: int, weth_spent: float, success_rate: float):
        """Update stats display."""
        self.sniped_count.config(text=f"Sniped: {total_sniped}")
        self.weth_spent.config(text=f"WETH Spent: {weth_spent:.6f}")
        if total_sniped > 0:
            self.success_rate.config(text=f"Success: {success_rate:.0f}%")

    def add_sniped_token(self, token_data: dict):
        """Add a sniped token to the table."""
        symbol = token_data.get("symbol", "???")
        address = token_data.get("address", "")[:16] + "..."
        pair = token_data.get("pair_address", "")[:16] + "..."
        weth = token_data.get("weth_spent", 0)
        tokens = token_data.get("tokens_received", 0)
        status = token_data.get("status", "holding")
        time_str = token_data.get("time", datetime.now().strftime("%H:%M:%S"))

        values = (time_str, symbol, address, pair, f"{weth:.6f}", f"{tokens:,.0f}", status)

        if symbol in self._tree_items:
            self.tree.item(self._tree_items[symbol], values=values, tags=(status,))
        else:
            item_id = self.tree.insert("", 0, values=values, tags=(status,))
            self._tree_items[symbol] = item_id

    def log(self, message: str, level: str = "info"):
        """Add a message to the activity log."""
        colors = {
            "info": TEXT_MID,
            "success": SUCCESS,
            "warning": WARNING,
            "error": ERROR,
            "accent": ACCENT,
        }
        color = colors.get(level, TEXT_MID)
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", level)
        self.log_text.tag_configure(level, foreground=color)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
