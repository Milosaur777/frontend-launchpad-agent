"""Trade history view showing closed trades."""

import tkinter as tk
from tkinter import ttk

from ui.config import SURFACE_CARD, TEXT, TEXT_DIM, TEXT_MID, SUCCESS, ERROR, FONT_SIZE, FONT_SIZE_SM, PAD_X, PAD_Y, CARD_PAD
from ui.components import styled_frame, styled_label, section_header, style_treeview


class TradeHistoryView(tk.Frame):
    """Trade history panel."""
    
    COLUMNS = [
        ("time", "TIME"),
        ("symbol", "SYMBOL"),
        ("action", "ACTION"),
        ("entry", "ENTRY"),
        ("exit", "EXIT"),
        ("pnl", "PnL"),
        ("reason", "REASON"),
    ]
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE_CARD)
        self.app = app
        self._build_ui()
    
    def _build_ui(self):
        header = section_header(self, "Trade History", "Closed trades and performance")
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y, PAD_Y // 2))
        
        table_frame = styled_frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=PAD_X, pady=PAD_Y)
        
        columns = [col for col, _ in self.COLUMNS]
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        style_treeview(self.tree, self.COLUMNS)
        
        widths = {"time": 140, "symbol": 80, "action": 60, "entry": 100, "exit": 100, "pnl": 100, "reason": 200}
        for col, width in widths.items():
            self.tree.column(col, width=width, minwidth=width)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=CARD_PAD)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=CARD_PAD)
    
    def add_trade(self, trade):
        """Add a trade to history."""
        pnl = trade.get("pnl", 0)
        tag = "profit" if pnl >= 0 else "loss"
        
        values = (
            trade.get("time", "—"),
            trade.get("symbol", "—"),
            trade.get("action", "—"),
            f"${trade.get('entry', 0):,.6f}",
            f"${trade.get('exit', 0):,.6f}",
            f"${pnl:,.2f}",
            trade.get("reason", "—"),
        )
        
        self.tree.insert("", 0, values=values, tags=(tag,))
        self.tree.tag_configure("profit", foreground=SUCCESS)
        self.tree.tag_configure("loss", foreground=ERROR)
