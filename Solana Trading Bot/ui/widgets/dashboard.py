"""Dashboard view showing portfolio overview and key metrics."""

import tkinter as tk

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
    FONT_SIZE_XL,
    PAD_X,
    PAD_Y,
    CARD_PAD,
)
from ui.components import styled_frame, styled_label, metric_card, section_header, status_badge
from ui.widgets.chart import PriceChart, ChartSeries


class DashboardView(tk.Frame):
    """Main dashboard view with portfolio metrics, price chart, and recent activity."""
    
    def __init__(self, parent, app):
        super().__init__(parent, bg=SURFACE_CARD)
        self.app = app
        
        self.metric_vars = {}
        self.price_history = {}  # symbol -> list of (timestamp, price)
        self._last_overlay_symbols = set()  # Track symbols for overlay menu
        self._build_ui()
    
    def _build_ui(self):
        """Build dashboard UI."""
        # Header
        header = section_header(self, "Dashboard", "Portfolio overview, live chart, and bot performance")
        header.pack(fill=tk.X, padx=PAD_X, pady=(PAD_Y, PAD_Y // 2))
        
        # Metrics grid
        metrics_frame = tk.Frame(self, bg=SURFACE_CARD)
        metrics_frame.pack(fill=tk.X, padx=PAD_X, pady=PAD_Y)
        
        self.metrics = {
            "balance": metric_card(metrics_frame, "TOTAL BALANCE", "$0.00", "Starting capital + PnL", ACCENT),
            "pnl": metric_card(metrics_frame, "TOTAL PnL", "$0.00", "Realized + unrealized", SUCCESS),
            "win_rate": metric_card(metrics_frame, "WIN RATE", "0%", "From closed trades", ACCENT),
            "open_positions": metric_card(metrics_frame, "OPEN POSITIONS", "0", "Active trades", TEXT_BRIGHT),
        }
        
        for i, (key, (card, lbl)) in enumerate(self.metrics.items()):
            card.grid(row=0, column=i, padx=(0 if i == 0 else 8, 0), sticky="nsew")
        
        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)
        
        # Chart + side panels split
        split = tk.Frame(self, bg=SURFACE_CARD)
        split.pack(fill=tk.BOTH, expand=True, padx=PAD_X, pady=PAD_Y)
        split.grid_columnconfigure(0, weight=3)
        split.grid_columnconfigure(1, weight=1)
        split.grid_rowconfigure(0, weight=1)
        
        # Left: chart panel
        chart_panel = self._build_chart_panel(split)
        chart_panel.grid(row=0, column=0, sticky="nsew", padx=(0, PAD_X // 2))
        
        # Right: portfolio + activity
        right_panel = tk.Frame(split, bg=SURFACE_CARD)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(PAD_X // 2, 0))
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)
        
        portfolio = self._build_portfolio_panel(right_panel)
        portfolio.grid(row=0, column=0, sticky="nsew", pady=(0, PAD_Y // 2))
        
        activity = self._build_activity_panel(right_panel)
        activity.grid(row=1, column=0, sticky="nsew", pady=(PAD_Y // 2, 0))
    
    def _build_chart_panel(self, parent):
        """Build live price chart panel with controls."""
        panel = styled_frame(parent)
        panel.pack_propagate(False)
        panel.config(height=400)
        
        # Header with controls
        header_frame = tk.Frame(panel, bg=SURFACE_CARD)
        header_frame.pack(fill=tk.X, padx=CARD_PAD, pady=(CARD_PAD, PAD_Y // 2))
        
        header = styled_label(header_frame, "LIVE PRICE CHART", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        header.pack(side=tk.LEFT)
        
        controls = tk.Frame(header_frame, bg=SURFACE_CARD)
        controls.pack(side=tk.RIGHT)
        
        # Mode toggle — default to Candlestick
        self.chart_mode_var = tk.StringVar(value="candlestick")
        mode_btn = tk.Menubutton(
            controls,
            text="Candlestick",
            font=(FONT_FAMILY, FONT_SIZE),
            fg=TEXT,
            bg=SURFACE,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT_BRIGHT,
            highlightbackground=BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        mode_menu = tk.Menu(mode_btn, tearoff=0, bg=SURFACE, fg=TEXT, activebackground=ACCENT_DIM, activeforeground=ACCENT, bd=0)
        mode_menu.add_radiobutton(label="Line", variable=self.chart_mode_var, value="line", command=self._on_mode_change)
        mode_menu.add_radiobutton(label="Candlestick", variable=self.chart_mode_var, value="candlestick", command=self._on_mode_change)
        mode_btn.config(menu=mode_menu)
        mode_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.chart_mode_btn = mode_btn
        
        # Time range
        self.chart_range_var = tk.StringVar(value="ALL")
        range_btn = tk.Menubutton(
            controls,
            text="ALL",
            font=(FONT_FAMILY, FONT_SIZE),
            fg=TEXT,
            bg=SURFACE,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT_BRIGHT,
            highlightbackground=BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        range_menu = tk.Menu(range_btn, tearoff=0, bg=SURFACE, fg=TEXT, activebackground=ACCENT_DIM, activeforeground=ACCENT, bd=0)
        for r in ["1h", "4h", "24h", "ALL"]:
            range_menu.add_radiobutton(label=r, variable=self.chart_range_var, value=r, command=self._on_range_change)
        range_btn.config(menu=range_menu)
        range_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.chart_range_btn = range_btn
        
        # Overlay selector
        self.overlay_var = tk.StringVar(value="Overlay")
        overlay_btn = tk.Menubutton(
            controls,
            text="Overlay",
            font=(FONT_FAMILY, FONT_SIZE),
            fg=TEXT,
            bg=SURFACE,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT_BRIGHT,
            highlightbackground=BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        self.overlay_menu = tk.Menu(overlay_btn, tearoff=0, bg=SURFACE, fg=TEXT, activebackground=ACCENT_DIM, activeforeground=ACCENT, bd=0)
        overlay_btn.config(menu=self.overlay_menu)
        overlay_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.overlay_btn = overlay_btn
        
        # Indicators — EMA 26, RSI 14, MACD on by default
        self.indicator_var = tk.StringVar(value="Indicators")
        indicator_btn = tk.Menubutton(
            controls,
            text="Indicators",
            font=(FONT_FAMILY, FONT_SIZE),
            fg=TEXT,
            bg=SURFACE,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT_BRIGHT,
            highlightbackground=BORDER_LIGHT,
            highlightthickness=1,
            bd=0,
        )
        self.indicator_menu = tk.Menu(indicator_btn, tearoff=0, bg=SURFACE, fg=TEXT, activebackground=ACCENT_DIM, activeforeground=ACCENT, bd=0)
        indicator_defaults = {"ema_12": False, "ema_26": True, "rsi_14": True, "macd": True}
        for key, label in PriceChart.INDICATORS.items():
            var = tk.BooleanVar(value=indicator_defaults.get(key, False))
            self.indicator_menu.add_checkbutton(
                label=label,
                variable=var,
                command=lambda k=key, v=var: self._on_indicator_toggle(k, v.get()),
            )
        indicator_btn.config(menu=self.indicator_menu)
        indicator_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.indicator_btn = indicator_btn
        
        # Screenshot button
        screenshot_btn = tk.Label(
            controls,
            text="📷",
            font=(FONT_FAMILY, FONT_SIZE_LG),
            fg=TEXT_MID,
            bg=SURFACE_CARD,
            cursor="hand2",
        )
        screenshot_btn.pack(side=tk.LEFT)
        screenshot_btn.bind("<Enter>", lambda e: screenshot_btn.config(fg=TEXT_BRIGHT))
        screenshot_btn.bind("<Leave>", lambda e: screenshot_btn.config(fg=TEXT_MID))
        screenshot_btn.bind("<Button-1>", lambda e: self.price_chart.save_screenshot())
        self.screenshot_btn = screenshot_btn
        
        # Chart
        self.price_chart = PriceChart(panel, height=340)
        self.price_chart.pack(fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=(0, CARD_PAD))
        
        return panel
    
    def _on_mode_change(self):
        """Handle chart mode change."""
        mode = self.chart_mode_var.get()
        self.price_chart.set_mode(mode)
        self.chart_mode_btn.config(text=mode.capitalize())
    
    def _on_range_change(self):
        """Handle time range change."""
        range_key = self.chart_range_var.get()
        self.price_chart.set_time_range(range_key)
        self.chart_range_btn.config(text=range_key)
    
    def _on_indicator_toggle(self, key, enabled):
        """Handle indicator toggle."""
        self.price_chart.set_indicator(key, enabled)
    
    def _on_overlay_toggle(self, symbol):
        """Toggle overlay for a symbol."""
        if symbol in self.price_chart.series:
            current = self.price_chart.series[symbol].visible
            self.price_chart.set_series_visibility(symbol, not current)
        else:
            self._update_chart(symbol)
            self.price_chart.set_series_visibility(symbol, True)
        
        self._refresh_overlay_menu()
    
    def _refresh_overlay_menu(self):
        """Refresh overlay menu checkmarks only when symbols change."""
        current_symbols = set(self.price_history.keys())
        
        # Only rebuild if symbols actually changed
        if current_symbols == self._last_overlay_symbols:
            # Just update checkmarks without rebuilding
            for i, symbol in enumerate(sorted(current_symbols)):
                if i < self.overlay_menu.index(tk.END) + 1:
                    visible = self.price_chart.series.get(symbol, ChartSeries(symbol)).visible
                    if symbol in self.price_chart.series:
                        visible = self.price_chart.series[symbol].visible
                    self.overlay_menu.entryconfigure(i, variable=tk.BooleanVar(value=visible))
            return
        
        # Symbols changed - rebuild menu
        self._last_overlay_symbols = current_symbols.copy()
        self.overlay_menu.delete(0, "end")
        for symbol in sorted(current_symbols):
            visible = self.price_chart.series.get(symbol, ChartSeries(symbol)).visible
            if symbol in self.price_chart.series:
                visible = self.price_chart.series[symbol].visible
            var = tk.BooleanVar(value=visible)
            self.overlay_menu.add_checkbutton(
                label=symbol,
                variable=var,
                command=lambda s=symbol: self._on_overlay_toggle(s),
            )
    
    def _update_chart(self, symbol):
        """Update chart for selected symbol."""
        history = self.price_history.get(symbol, [])
        if history:
            timestamps = [t for t, _ in history]
            prices = [p for _, p in history]
            self.price_chart.set_line_data(symbol, timestamps, prices)
    
    def _build_portfolio_panel(self, parent):
        """Build portfolio breakdown panel."""
        panel = styled_frame(parent)
        panel.pack_propagate(False)
        panel.config(height=195)

        header = styled_label(panel, "PORTFOLIO BREAKDOWN", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, CARD_PAD // 2))
        
        # Asset allocation frame
        alloc_frame = tk.Frame(panel, bg=SURFACE_CARD)
        alloc_frame.pack(fill=tk.X, padx=CARD_PAD, pady=PAD_Y)
        
        # Simple bar chart
        self.allocation_bar = tk.Canvas(alloc_frame, bg=SURFACE_CARD, height=24, highlightthickness=0)
        self.allocation_bar.pack(fill=tk.X)
        
        # Allocation labels
        self.allocation_labels = tk.Frame(panel, bg=SURFACE_CARD)
        self.allocation_labels.pack(fill=tk.X, padx=CARD_PAD, pady=(0, PAD_Y))
        
        # Asset list
        self.asset_list = tk.Frame(panel, bg=SURFACE_CARD)
        self.asset_list.pack(fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=PAD_Y)
        
        self._build_asset_headers()
        
        return panel
    
    def _build_asset_headers(self):
        """Build asset list headers."""
        header = tk.Frame(self.asset_list, bg=SURFACE_CARD)
        header.pack(fill=tk.X)
        
        headers = [("ASSET", 14), ("ALLOC", 12), ("VALUE", 12), ("PnL", 10)]
        for text, width in headers:
            lbl = styled_label(header, text, size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
            lbl.pack(side=tk.LEFT, padx=(0, 8))
            lbl.config(width=width)
    
    def _build_activity_panel(self, parent):
        """Build recent activity panel."""
        panel = styled_frame(parent)
        panel.pack_propagate(False)
        panel.config(height=195)

        header = styled_label(panel, "RECENT ACTIVITY", size=FONT_SIZE_SM, color=TEXT_MID, bold=True, bg=SURFACE_CARD)
        header.pack(anchor="w", padx=CARD_PAD, pady=(CARD_PAD, CARD_PAD // 2))
        
        self.activity_container = tk.Frame(panel, bg=SURFACE_CARD)
        self.activity_container.pack(fill=tk.BOTH, expand=True, padx=CARD_PAD, pady=PAD_Y)
        
        self._add_activity_item("Bot initialized", "Paper trading mode active", "info")
        self._add_activity_item("Watching 15 tokens", "Solana + Robinhood Chain", "neutral")
        
        return panel
    
    def _add_activity_item(self, title, subtitle, status):
        """Add an activity item."""
        item = tk.Frame(self.activity_container, bg=SURFACE_CARD)
        item.pack(fill=tk.X, pady=3)
        
        colors = {
            "success": SUCCESS,
            "error": ERROR,
            "warning": WARNING,
            "info": "#3b82f6",
            "neutral": TEXT_DIM,
        }
        color = colors.get(status, TEXT_DIM)
        
        dot = tk.Label(item, text="●", font=(FONT_FAMILY, FONT_SIZE_SM), fg=color, bg=SURFACE_CARD)
        dot.pack(side=tk.LEFT)
        
        text_frame = tk.Frame(item, bg=SURFACE_CARD)
        text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        
        title_lbl = styled_label(text_frame, title, size=FONT_SIZE, color=TEXT, bg=SURFACE_CARD)
        title_lbl.pack(anchor="w")
        
        sub_lbl = styled_label(text_frame, subtitle, size=FONT_SIZE_SM, color=TEXT_DIM, bg=SURFACE_CARD)
        sub_lbl.pack(anchor="w")
    
    def update_metrics(self, balance=0.0, pnl=0.0, win_rate=0.0, open_positions=0):
        """Update dashboard metrics."""
        pnl_color = SUCCESS if pnl >= 0 else ERROR
        
        self.metrics["balance"][1].config(text=f"${balance:,.2f}")
        self.metrics["pnl"][1].config(text=f"${pnl:,.2f}", fg=pnl_color)
        self.metrics["win_rate"][1].config(text=f"{win_rate:.1f}%")
        self.metrics["open_positions"][1].config(text=str(open_positions))
    
    def add_activity(self, title, subtitle, status="neutral"):
        """Add a new activity item."""
        self._add_activity_item(title, subtitle, status)
    
    def update_allocation(self, allocations):
        """Update allocation bar chart."""
        # allocations: list of (symbol, value, color)
        total = sum(v for _, v, _ in allocations) or 1
        
        self.allocation_bar.delete("all")
        x = 0
        width = self.allocation_bar.winfo_width() or 300
        
        for symbol, value, color in allocations:
            w = (value / total) * width
            self.allocation_bar.create_rectangle(x, 0, x + w, 24, fill=color, outline="")
            x += w
        
        # Clear and rebuild labels
        for widget in self.allocation_labels.winfo_children():
            widget.destroy()
        
        for symbol, value, color in allocations:
            pct = (value / total) * 100
            lbl = styled_label(self.allocation_labels, f"● {symbol} {pct:.1f}%", size=FONT_SIZE_SM, color=color, bg=SURFACE_CARD)
            lbl.pack(side=tk.LEFT, padx=(0, 12))
    
    def update_asset_list(self, assets):
        """Update asset list."""
        # assets: list of (symbol, allocation_pct, value, pnl)
        for widget in self.asset_list.winfo_children()[1:]:  # Keep header
            widget.destroy()
        
        for symbol, alloc, value, pnl in assets:
            row = tk.Frame(self.asset_list, bg=SURFACE_CARD)
            row.pack(fill=tk.X, pady=2)
            
            pnl_color = SUCCESS if pnl >= 0 else ERROR
            
            data = [
                (symbol, 14, TEXT),
                (f"{alloc:.1f}%", 12, TEXT_MID),
                (f"${value:,.2f}", 12, TEXT),
                (f"${pnl:,.2f}", 10, pnl_color),
            ]
            
            for text, width, color in data:
                lbl = styled_label(row, text, size=FONT_SIZE, color=color, bg=SURFACE_CARD)
                lbl.pack(side=tk.LEFT, padx=(0, 8))
                lbl.config(width=width)
    
    def update_chart_symbols(self, symbols):
        """Update chart overlay menu with available symbols."""
        for symbol in symbols:
            if symbol not in self.price_history:
                self.price_history[symbol] = []
        
        # Ensure at least one series is visible
        if not any(self.price_chart.series.get(s, ChartSeries(s)).visible for s in symbols):
            if symbols:
                self.price_chart.add_series(symbols[0])
        
        self._refresh_overlay_menu()
        self.price_chart.draw()
    
    def add_price_point(self, symbol, timestamp, price):
        """Add a price point to chart history."""
        from datetime import datetime
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.strptime(timestamp, "%H:%M:%S")
            except Exception:
                timestamp = datetime.now()
        
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append((timestamp, price))
        
        # Keep last 100 points
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
        
        # Add to chart
        self.price_chart.add_line_point(symbol, timestamp, price)
        self._refresh_overlay_menu()
    
    def set_chart_data(self, symbol, prices, timestamps=None):
        """Set full chart data for a symbol."""
        from datetime import datetime
        if timestamps is None:
            timestamps = [datetime.now() for _ in prices]
        elif isinstance(timestamps[0], str):
            # Parse string timestamps
            parsed = []
            for t in timestamps:
                try:
                    parsed.append(datetime.strptime(t, "%H:%M:%S"))
                except Exception:
                    parsed.append(datetime.now())
            timestamps = parsed
        
        self.price_history[symbol] = list(zip(timestamps, prices))
        self.price_chart.set_line_data(symbol, timestamps, prices)
        self._refresh_overlay_menu()
