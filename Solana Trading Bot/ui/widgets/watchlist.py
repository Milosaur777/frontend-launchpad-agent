"""Watchlist view showing live token prices and signals."""

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


class WatchlistView(tk.Frame):
    """Live token watchlist with prices, liquidity, volume, and scores."""
    
    COLUMNS = [
        ("symbol", "SYMBOL"),
        ("chain", "CHAIN"),
        ("price", "PRICE"),
        ("change", "24H %"),
        ("liquidity", "LIQUIDITY"),
        ("volume", "VOLUME 24H"),
        ("score", "SAFETY"),
        ("signal", "SIGNAL"),
    ]
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE_CARD)
        self.app = app
        self._tree_items = {}
        self._build_ui()
    
    def _build_ui(self):
        """Build watchlist UI."""
        # Header
        header = section_header(self, "Token Watchlist", "Live prices and safety scores")
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y, PAD_Y // 2))
        
        # Stats bar
        stats_frame = tk.Frame(self, bg=SURFACE_CARD)
        stats_frame.pack(fill=tk.X, padx=PAD_X, pady=(0, PAD_Y))
        
        self.token_count = styled_label(stats_frame, "Watching: 0 tokens", size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
        self.token_count.pack(side=tk.LEFT)
        
        self.last_update = styled_label(stats_frame, "Last update: —", size=FONT_SIZE_SM, color=TEXT_DIM, bg=SURFACE_CARD)
        self.last_update.pack(side=tk.RIGHT)
        
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
        
        # Configure column widths
        widths = {
            "symbol": 100,
            "chain": 80,
            "price": 100,
            "change": 80,
            "liquidity": 110,
            "volume": 110,
            "score": 80,
            "signal": 100,
        }
        for col, width in widths.items():
            self.tree.column(col, width=width, minwidth=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=CARD_PAD)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=CARD_PAD)
        
        # Selection binding
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
    
    def _on_select(self, event):
        """Handle token selection."""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            if values:
                symbol = values[0]
                self.app.log_message(f"Selected token: {symbol}", "info")
    
    def update_watchlist(self, tokens):
        """
        Update watchlist display.
        
        tokens: list of dicts with keys:
            symbol, chain, price, change_24h, liquidity, volume, score, is_safe, signal
        """
        self.token_count.config(text=f"Watching: {len(tokens)} tokens")
        
        # Remove items not in tokens
        current_symbols = {t["symbol"] for t in tokens}
        for symbol, item_id in list(self._tree_items.items()):
            if symbol not in current_symbols:
                self.tree.delete(item_id)
                del self._tree_items[symbol]
        
        # Update / insert
        for token in tokens:
            symbol = token["symbol"]
            
            score = token.get("score", 0)
            is_safe = token.get("is_safe", False)
            
            if score >= 80:
                score_text = f"{score:.0f} ⚠"
                score_tag = "risky"
            elif score >= 50:
                score_text = f"{score:.0f}"
                score_tag = "medium"
            else:
                score_text = f"{score:.0f}"
                score_tag = "safe"
            
            signal = token.get("signal", "—")
            signal_tag = {
                "BUY": "buy",
                "SELL": "sell",
                "HOLD": "hold",
            }.get(signal, "neutral")
            
            values = (
                symbol,
                token.get("chain", "SOL").upper(),
                f"${token.get('price', 0):,.6f}",
                f"{token.get('change_24h', 0):+.1f}%",
                f"${token.get('liquidity', 0):,.0f}",
                f"${token.get('volume', 0):,.0f}",
                score_text,
                signal,
            )
            
            tags = (score_tag, signal_tag)
            
            if symbol in self._tree_items:
                self.tree.item(self._tree_items[symbol], values=values, tags=tags)
            else:
                item_id = self.tree.insert("", tk.END, values=values, tags=tags)
                self._tree_items[symbol] = item_id
        
        # Configure tag colors
        self.tree.tag_configure("safe", foreground=SUCCESS)
        self.tree.tag_configure("medium", foreground=WARNING)
        self.tree.tag_configure("risky", foreground=ERROR)
        self.tree.tag_configure("buy", foreground=SUCCESS)
        self.tree.tag_configure("sell", foreground=ERROR)
        self.tree.tag_configure("hold", foreground=TEXT_MID)
        self.tree.tag_configure("neutral", foreground=TEXT_DIM)
        
        self.last_update.config(text=f"Last update: now")
