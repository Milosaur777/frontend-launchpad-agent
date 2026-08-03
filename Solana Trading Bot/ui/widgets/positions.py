"""Positions view showing open trades with PnL and trailing stops."""

import tkinter as tk
from tkinter import ttk

from ui.config import (
    SURFACE_CARD,
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
    PAD_X,
    PAD_Y,
    CARD_PAD,
)
from ui.components import styled_frame, styled_label, section_header, style_treeview


class PositionsView(tk.Frame):
    """Open positions panel with PnL and trailing stop visualization."""
    
    COLUMNS = [
        ("symbol", "SYMBOL"),
        ("entry", "ENTRY"),
        ("current", "CURRENT"),
        ("pnl", "PnL"),
        ("pnl_pct", "PnL %"),
        ("stop", "TRAIL STOP"),
        ("status", "STATUS"),
    ]
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE_CARD)
        self.app = app
        self._tree_items = {}
        self._build_ui()
    
    def _build_ui(self):
        """Build positions UI."""
        # Header
        header = section_header(self, "Open Positions", "Active trades and trailing stops")
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y, PAD_Y // 2))
        
        # Summary bar
        summary = tk.Frame(self, bg=SURFACE_CARD)
        summary.pack(fill=tk.X, padx=PAD_X, pady=(0, PAD_Y))
        
        self.position_count = styled_label(summary, "0 positions", size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
        self.position_count.pack(side=tk.LEFT)
        
        self.unrealized_pnl = styled_label(summary, "Unrealized PnL: $0.00", size=FONT_SIZE_SM, color=TEXT_DIM, bg=SURFACE_CARD)
        self.unrealized_pnl.pack(side=tk.RIGHT)
        
        # Treeview
        table_frame = styled_frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=PAD_X, pady=PAD_Y)
        
        columns = [col for col, _ in self.COLUMNS]
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        style_treeview(self.tree, self.COLUMNS)
        
        widths = {
            "symbol": 100,
            "entry": 100,
            "current": 100,
            "pnl": 100,
            "pnl_pct": 80,
            "stop": 100,
            "status": 100,
        }
        for col, width in widths.items():
            self.tree.column(col, width=width, minwidth=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=CARD_PAD)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=CARD_PAD)
    
    def update_positions(self, positions):
        """
        Update positions display.
        
        positions: list of dicts with keys:
            symbol, entry_price, current_price, pnl, pnl_pct, stop_price, status
        """
        self.position_count.config(text=f"{len(positions)} positions")
        
        total_pnl = sum(p.get("pnl", 0) for p in positions)
        pnl_color = SUCCESS if total_pnl >= 0 else ERROR
        self.unrealized_pnl.config(text=f"Unrealized PnL: ${total_pnl:,.2f}", fg=pnl_color)
        
        # Remove old items
        current_symbols = {p["symbol"] for p in positions}
        for symbol, item_id in list(self._tree_items.items()):
            if symbol not in current_symbols:
                self.tree.delete(item_id)
                del self._tree_items[symbol]
        
        # Update / insert
        for pos in positions:
            symbol = pos["symbol"]
            pnl = pos.get("pnl", 0)
            pnl_pct = pos.get("pnl_pct", 0)
            
            pnl_color = SUCCESS if pnl >= 0 else ERROR
            status = pos.get("status", "OPEN")
            
            values = (
                symbol,
                f"${pos.get('entry_price', 0):,.6f}",
                f"${pos.get('current_price', 0):,.6f}",
                f"${pnl:,.2f}",
                f"{pnl_pct:+.2f}%",
                f"${pos.get('stop_price', 0):,.6f}",
                status,
            )
            
            tag = "profit" if pnl >= 0 else "loss"
            
            if symbol in self._tree_items:
                self.tree.item(self._tree_items[symbol], values=values, tags=(tag,))
            else:
                item_id = self.tree.insert("", tk.END, values=values, tags=(tag,))
                self._tree_items[symbol] = item_id
        
        self.tree.tag_configure("profit", foreground=SUCCESS)
        self.tree.tag_configure("loss", foreground=ERROR)
