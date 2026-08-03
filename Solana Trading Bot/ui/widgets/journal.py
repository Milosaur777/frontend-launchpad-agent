"""Journal view for trade notes and learning."""

import tkinter as tk

from ui.config import (
    SURFACE_CARD, SURFACE, TEXT, TEXT_DIM, TEXT_MID, TEXT_BRIGHT,
    ACCENT, ACCENT_DIM, SUCCESS, ERROR, WARNING,
    FONT_FAMILY, FONT_SIZE, FONT_SIZE_SM,
    PAD_X, PAD_Y, CARD_PAD,
)
from ui.components import styled_frame, styled_label, section_header


class JournalView(tk.Frame):
    """Trading journal panel with AI notes and pattern learning."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE_CARD)
        self.app = app
        self._build_ui()
    
    def _build_ui(self):
        header = section_header(self, "Trading Journal", "AI-generated notes and lessons learned")
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y, PAD_Y // 2))
        
        # Insights card
        insights_card = styled_frame(self)
        insights_card.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        insights_header = styled_label(insights_card, "LEARNED INSIGHTS", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        insights_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))
        
        self.insights_text = tk.Text(
            insights_card,
            font=(FONT_FAMILY, FONT_SIZE),
            fg=TEXT,
            bg=SURFACE,
            insertbackground=TEXT,
            highlightthickness=0,
            bd=0,
            wrap=tk.WORD,
            padx=CARD_PAD,
            pady=CARD_PAD,
            height=6,
        )
        self.insights_text.pack(fill=tk.X, padx=CARD_PAD, pady=(0, CARD_PAD))
        self.insights_text.insert(tk.END, "No insights yet. The bot will analyze winning and losing trades to find patterns.")
        self.insights_text.config(state=tk.DISABLED)
        
        # Entries list
        entries_card = styled_frame(self)
        entries_card.pack(fill=tk.BOTH, expand=True, padx=PAD_X, pady=PAD_Y)
        
        entries_header = styled_label(entries_card, "TRADE NOTES", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        entries_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))
        
        self.entries_container = tk.Frame(entries_card, bg=SURFACE_CARD)
        self.entries_container.pack(fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=(0, CARD_PAD))
        
        self._add_entry("2026-07-15 09:30", "Example trade note", "This is where AI-generated trade notes will appear.")
    
    def _add_entry(self, time, title, note):
        """Add a journal entry."""
        entry = styled_frame(self.entries_container)
        entry.pack(fill=tk.X, pady=4)
        
        header = tk.Frame(entry, bg=SURFACE_CARD)
        header.pack(fill=tk.X, padx=CARD_PAD, pady=(CARD_PAD, 0))
        
        time_lbl = styled_label(header, time, size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
        time_lbl.pack(side=tk.LEFT)
        
        title_lbl = styled_label(header, title, size=FONT_SIZE, color=TEXT_BRIGHT, bold=True, bg=SURFACE_CARD)
        title_lbl.pack(side=tk.LEFT, padx=(12, 0))
        
        note_lbl = styled_label(entry, note, size=FONT_SIZE, color=TEXT_DIM, bg=SURFACE_CARD)
        note_lbl.pack(anchor="w", padx=CARD_PAD, pady=(4, CARD_PAD))
    
    def add_trade_note(self, time, symbol, action, pnl, note):
        """Add a trade note to the journal."""
        title = f"{action} {symbol} | PnL: ${pnl:,.2f}"
        self._add_entry(time, title, note)
    
    def update_insights(self, insights):
        """Update learned insights."""
        self.insights_text.config(state=tk.NORMAL)
        self.insights_text.delete(1.0, tk.END)
        self.insights_text.insert(tk.END, insights)
        self.insights_text.config(state=tk.DISABLED)
