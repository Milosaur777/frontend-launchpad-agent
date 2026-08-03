"""Settings view for configuring the trading bot."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from ui.config import (
    SURFACE,
    SURFACE_CARD,
    SURFACE_HOVER,
    SURFACE_ACTIVE,
    TEXT,
    TEXT_DIM,
    TEXT_MID,
    TEXT_BRIGHT,
    ACCENT,
    ACCENT_DIM,
    ACCENT_BRIGHT,
    BORDER,
    BORDER_LIGHT,
    BORDER_ACCENT,
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
from ui.components import styled_frame, styled_label, section_header, styled_button, status_badge


class SettingsView(tk.Frame):
    """Settings panel with paper/live toggle and configuration."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE_CARD)
        self.app = app
        self._build_ui()
    
    def _build_ui(self):
        """Build settings UI."""
        # Header
        header = section_header(self, "Settings", "Configure bot behavior and risk parameters")
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y, PAD_Y // 2))
        
        # Mode toggle section (PAPER / LIVE)
        mode_card = styled_frame(self, highlight=True)
        mode_card.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        mode_header = styled_label(mode_card, "TRADING MODE", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        mode_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))
        
        mode_row = tk.Frame(mode_card, bg=SURFACE_CARD)
        mode_row.pack(fill=tk.X, padx=CARD_PAD, pady=(0, CARD_PAD))
        
        self.mode_var = tk.StringVar(value="PAPER")
        
        self.paper_btn = self._create_mode_button(mode_row, "PAPER", "Practice with fake money", "paper")
        self.paper_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.live_btn = self._create_mode_button(mode_row, "LIVE", "Trade real money", "live")
        self.live_btn.pack(side=tk.LEFT)
        
        self.mode_badge = status_badge(mode_row, "PAPER MODE", status="success")
        self.mode_badge.pack(side=tk.RIGHT)
        
        self.warning_frame = tk.Frame(mode_card, bg="#1a1010", highlightbackground=ERROR, highlightthickness=1)
        self.warning_lbl = tk.Label(
            self.warning_frame,
            text="⚠ LIVE MODE: Real capital will be used. Ensure you understand the risks.",
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            fg=ERROR,
            bg="#1a1010",
            wraplength=600,
            justify=tk.LEFT,
        )
        self.warning_lbl.pack(padx=CARD_PAD, pady=CARD_PAD)
        # Hidden by default
        self.warning_frame.pack_forget()
        
        # Risk parameters
        risk_card = styled_frame(self)
        risk_card.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        risk_header = styled_label(risk_card, "RISK PARAMETERS", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        risk_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))
        
        risk_grid = tk.Frame(risk_card, bg=SURFACE_CARD)
        risk_grid.pack(fill=tk.X, padx=CARD_PAD, pady=(0, CARD_PAD))
        
        self.risk_fields = {}
        fields = [
            ("capital", "Starting Capital ($)", "100"),
            ("max_positions", "Max Risk Per Trade (%)", "20"),
            ("stop_loss", "Stop Loss %", "5"),
            ("take_profit", "Take Profit %", "15"),
            ("trailing_stop", "Trailing Stop %", "3"),
        ]
        
        for i, (key, label, default) in enumerate(fields):
            row = i // 3
            col = i % 3
            
            field_frame = tk.Frame(risk_grid, bg=SURFACE_CARD)
            field_frame.grid(row=row, column=col, sticky="w", padx=(0, 24), pady=8)
            
            lbl = styled_label(field_frame, label, size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
            lbl.pack(anchor="w")
            
            entry = tk.Entry(
                field_frame,
                font=(FONT_FAMILY, FONT_SIZE),
                fg=TEXT,
                bg=SURFACE,
                insertbackground=TEXT,
                highlightbackground=BORDER_LIGHT,
                highlightthickness=1,
                bd=0,
                width=20,
            )
            entry.insert(0, default)
            entry.pack(anchor="w", pady=(4, 0))
            
            self.risk_fields[key] = entry
        
        # API keys
        api_card = styled_frame(self)
        api_card.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        api_header = styled_label(api_card, "API KEYS", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        api_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))
        
        api_grid = tk.Frame(api_card, bg=SURFACE_CARD)
        api_grid.pack(fill=tk.X, padx=CARD_PAD, pady=(0, CARD_PAD))
        
        self.api_fields = {}
        api_fields = [
            ("solana_rpc", "Solana RPC URL", "https://api.mainnet-beta.solana.com"),
            ("wallet_key", "Wallet Private Key", ""),
            ("dexploit_key", "Dexploit API Key", ""),
            ("alpaca_key", "Alpaca API Key", ""),
            ("alpaca_secret", "Alpaca Secret", ""),
        ]
        
        for i, (key, label, default) in enumerate(api_fields):
            field_frame = tk.Frame(api_grid, bg=SURFACE_CARD)
            field_frame.pack(fill=tk.X, pady=6)
            
            lbl = styled_label(field_frame, label, size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
            lbl.pack(anchor="w")
            
            entry = tk.Entry(
                field_frame,
                font=(FONT_FAMILY, FONT_SIZE),
                fg=TEXT,
                bg=SURFACE,
                insertbackground=TEXT,
                highlightbackground=BORDER_LIGHT,
                highlightthickness=1,
                bd=0,
                width=80,
                show="●" if "key" in key or "secret" in key else "",
            )
            entry.insert(0, default)
            entry.pack(fill=tk.X, pady=(4, 0))
            
            self.api_fields[key] = entry
        
        # Action buttons
        buttons_frame = tk.Frame(self, bg=SURFACE_CARD)
        buttons_frame.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        self.save_btn = styled_button(buttons_frame, "Save Settings", self._save_settings, variant="primary", width=16)
        self.save_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        self.reset_btn = styled_button(buttons_frame, "Reset Defaults", self._reset_defaults, variant="secondary", width=16)
        self.reset_btn.pack(side=tk.LEFT)
        
        self.status_lbl = styled_label(buttons_frame, "", size=FONT_SIZE_SM, color=SUCCESS, bg=SURFACE_CARD)
        self.status_lbl.pack(side=tk.RIGHT)

        # Robinhood Chain Sniper section
        sniper_card = styled_frame(self, highlight=True)
        sniper_card.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)

        sniper_header = styled_label(sniper_card, "ROBINHOOD CHAIN SNIPER", size=FONT_SIZE_SM, color=ACCENT, bold=True, bg=SURFACE_CARD)
        sniper_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))

        sniper_desc = styled_label(
            sniper_card,
            "Auto-buy $1 of every new token launched on Robinhood Chain. Paper mode by default.",
            size=FONT_SIZE_SM, color=TEXT_DIM, bg=SURFACE_CARD,
        )
        sniper_desc.pack(anchor="w", padx=CARD_PAD, pady=(0, PAD_Y // 2))

        sniper_grid = tk.Frame(sniper_card, bg=SURFACE_CARD)
        sniper_grid.pack(fill=tk.X, padx=CARD_PAD, pady=(0, CARD_PAD))

        self.sniper_fields = {}
        sniper_fields = [
            ("buy_amount", "Buy Amount (WETH)", "0.0005"),
            ("max_concurrent", "Max Concurrent Buys", "3"),
            ("buy_delay", "Buy Delay (sec)", "0.5"),
            ("auto_sell_pnl", "Auto Sell at PnL %", "100"),
            ("auto_stop_loss", "Auto Stop Loss %", "-50"),
        ]

        for i, (key, label, default) in enumerate(sniper_fields):
            row = i // 3
            col = i % 3
            field_frame = tk.Frame(sniper_grid, bg=SURFACE_CARD)
            field_frame.grid(row=row, column=col, sticky="w", padx=(0, 24), pady=8)
            lbl = styled_label(field_frame, label, size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
            lbl.pack(anchor="w")
            entry = tk.Entry(
                field_frame, font=(FONT_FAMILY, FONT_SIZE), fg=TEXT, bg=SURFACE,
                insertbackground=TEXT, highlightbackground=BORDER_LIGHT, highlightthickness=1, bd=0, width=20,
            )
            entry.insert(0, default)
            entry.pack(anchor="w", pady=(4, 0))
            self.sniper_fields[key] = entry

        sniper_status = styled_label(sniper_card, "Status: IDLE", size=FONT_SIZE_SM, color=TEXT_MID, bg=SURFACE_CARD)
        sniper_status.pack(anchor="w", padx=CARD_PAD, pady=(0, CARD_PAD))
        self.sniper_status_lbl = sniper_status

        # ML Operations section
        ml_card = styled_frame(self)
        ml_card.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)

        ml_header = styled_label(ml_card, "ML OPERATIONS", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        ml_header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))

        ml_info = styled_label(ml_card, "Manage ML model training and data", size=FONT_SIZE_SM, color=TEXT_DIM, bg=SURFACE_CARD)
        ml_info.pack(anchor="w", padx=CARD_PAD, pady=(0, PAD_Y // 2))

        ml_buttons_row = tk.Frame(ml_card, bg=SURFACE_CARD)
        ml_buttons_row.pack(fill=tk.X, padx=CARD_PAD, pady=(0, CARD_PAD))

        self.retrain_btn = styled_button(ml_buttons_row, "Force Retrain Now", self._force_retrain, variant="warning", width=18)
        self.retrain_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.snapshot_btn = styled_button(ml_buttons_row, "Show Snapshots", self._show_snapshots, variant="secondary", width=18)
        self.snapshot_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.ml_status_lbl = styled_label(ml_buttons_row, "", size=FONT_SIZE_SM, color=SUCCESS, bg=SURFACE_CARD)
        self.ml_status_lbl.pack(side=tk.LEFT, padx=(8, 0))
    
    def _create_mode_button(self, parent, text, subtitle, mode):
        """Create a mode selection button."""
        btn = tk.Frame(parent, bg=SURFACE, highlightbackground=BORDER_LIGHT, highlightthickness=1, cursor="hand2")
        btn.config(width=200, height=60)
        btn.pack_propagate(False)
        
        title = tk.Label(btn, text=text, font=(FONT_FAMILY, FONT_SIZE_LG, "bold"), fg=TEXT, bg=SURFACE)
        title.pack(anchor="w", padx=12, pady=(8, 0))
        
        sub = tk.Label(btn, text=subtitle, font=(FONT_FAMILY, FONT_SIZE_SM), fg=TEXT_DIM, bg=SURFACE)
        sub.pack(anchor="w", padx=12, pady=(0, 8))
        
        def on_enter(e):
            if self.mode_var.get() != mode:
                btn.config(bg=SURFACE_HOVER)
                title.config(bg=SURFACE_HOVER)
                sub.config(bg=SURFACE_HOVER)
        
        def on_leave(e):
            if self.mode_var.get() != mode:
                btn.config(bg=SURFACE)
                title.config(bg=SURFACE)
                sub.config(bg=SURFACE)
        
        def on_click(e):
            self._set_mode(mode)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn.bind("<Button-1>", on_click)
        title.bind("<Button-1>", on_click)
        sub.bind("<Button-1>", on_click)
        
        return btn
    
    def _set_mode(self, mode):
        """Set trading mode."""
        self.mode_var.set(mode.upper())
        
        active_bg = ACCENT_DIM
        active_border = BORDER_ACCENT
        inactive_bg = SURFACE
        inactive_border = BORDER_LIGHT
        
        if mode == "paper":
            self.paper_btn.config(bg=active_bg, highlightbackground=active_border)
            for child in self.paper_btn.winfo_children():
                child.config(bg=active_bg, fg=TEXT_BRIGHT)
            
            self.live_btn.config(bg=inactive_bg, highlightbackground=inactive_border)
            for child in self.live_btn.winfo_children():
                child.config(bg=inactive_bg, fg=TEXT)
            
            self.mode_badge = status_badge(self.live_btn.master, "PAPER MODE", status="success")
            self.warning_frame.pack_forget()
        else:
            self.live_btn.config(bg=active_bg, highlightbackground=active_border)
            for child in self.live_btn.winfo_children():
                child.config(bg=active_bg, fg=TEXT_BRIGHT)
            
            self.paper_btn.config(bg=inactive_bg, highlightbackground=inactive_border)
            for child in self.paper_btn.winfo_children():
                child.config(bg=inactive_bg, fg=TEXT)
            
            self.mode_badge = status_badge(self.live_btn.master, "LIVE MODE", status="error")
            self.warning_frame.pack(fill=tk.X, padx=CARD_PAD, pady=(PAD_Y, 0))
        
        # Update badge placement
        self.mode_badge.pack_forget()
        self.mode_badge.pack(side=tk.RIGHT)
        
        self.app.set_live_mode(mode == "live")
    
    def _save_settings(self):
        """Save settings to config."""
        try:
            settings = {
                "mode": self.mode_var.get(),
                "risk": {k: v.get() for k, v in self.risk_fields.items()},
                "api": {k: v.get() for k, v in self.api_fields.items()},
            }
            
            self.app.apply_settings(settings)
            self.status_lbl.config(text="Settings saved", fg=SUCCESS)
            self.after(3000, lambda: self.status_lbl.config(text=""))
        except Exception as e:
            self.status_lbl.config(text=f"Error: {e}", fg=ERROR)
    
    def _reset_defaults(self):
        """Reset to default settings."""
        defaults = {
            "capital": "100",
            "max_positions": "20",
            "stop_loss": "5",
            "take_profit": "15",
            "trailing_stop": "3",
        }
        for key, val in defaults.items():
            self.risk_fields[key].delete(0, tk.END)
            self.risk_fields[key].insert(0, val)
        
        self._set_mode("paper")
        self.status_lbl.config(text="Defaults restored", fg=SUCCESS)
    
    def set_mode(self, mode):
        """Set mode programmatically."""
        self._set_mode(mode.lower())

    def _force_retrain(self):
        """Trigger immediate ML retraining."""
        if not hasattr(self.app, 'bot') or self.app.bot is None:
            self.ml_status_lbl.config(text="Bot not running", fg=ERROR)
            return
        self.ml_status_lbl.config(text="Retraining...", fg=ACCENT)
        self.retrain_btn.config(state=tk.DISABLED)

        def run_retrain():
            import asyncio
            from config.settings import Config
            from monitoring.logger import log
            try:
                self.app.bot.last_retrain = datetime.min  # Force retrain
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self.app.bot._maybe_retrain())
                loop.close()
                self.after(0, lambda: self.ml_status_lbl.config(text="Retrain triggered - check logs", fg=SUCCESS))
            except Exception as e:
                self.after(0, lambda: self.ml_status_lbl.config(text=f"Error: {e}", fg=ERROR))
            finally:
                self.after(0, lambda: self.retrain_btn.config(state=tk.NORMAL))

        import threading
        threading.Thread(target=run_retrain, daemon=True).start()

    def _show_snapshots(self):
        """Show snapshot counts per token."""
        if not hasattr(self.app, 'bot') or self.app.bot is None:
            self.ml_status_lbl.config(text="Bot not running", fg=ERROR)
            return
        history = self.app.bot.price_feed.history
        if not history:
            self.ml_status_lbl.config(text="No snapshot data", fg=WARNING)
            return
        counts = {t: len(s) for t, s in history.items()}
        total = sum(counts.values())
        top3 = sorted(counts.items(), key=lambda x: -x[1])[:3]
        top3_str = ", ".join(f"{s}:{c}" for s, c in top3)
        self.ml_status_lbl.config(text=f"{total} snapshots | Top: {top3_str}", fg=TEXT)
        self.after(10000, lambda: self.ml_status_lbl.config(text=""))
