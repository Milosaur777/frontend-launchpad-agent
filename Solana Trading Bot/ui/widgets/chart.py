"""Advanced Tkinter Canvas chart widget with candlesticks, indicators, markers, and screenshot."""

import tkinter as tk
from tkinter import filedialog
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

from ui.config import (
    SURFACE,
    SURFACE_CARD,
    SURFACE_HOVER,
    BORDER,
    BORDER_LIGHT,
    BORDER_ACCENT,
    ACCENT,
    ACCENT_DIM,
    ACCENT_BRIGHT,
    TEXT,
    TEXT_DIM,
    TEXT_MID,
    TEXT_BRIGHT,
    SUCCESS,
    ERROR,
    FONT_FAMILY,
    FONT_SIZE,
    FONT_SIZE_SM,
)


@dataclass
class OHLCV:
    """A single OHLCV candle."""

    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class TradeMarker:
    """A trade entry/exit marker."""

    timestamp: datetime
    price: float
    action: str  # "buy" or "sell"
    symbol: str
    pnl: Optional[float] = None


class ChartSeries:
    """A chart data series for one token."""

    def __init__(self, symbol: str, chain: str = "", color: str = ACCENT):
        self.symbol = symbol
        self.chain = chain
        self.color = color
        self.candles: List[OHLCV] = []
        self.line_values: List[float] = []
        self.line_timestamps: List[datetime] = []
        self.visible = True

    def add_candle(self, candle: OHLCV):
        """Add a candle."""
        self.candles.append(candle)

    def add_line_point(self, timestamp: datetime, price: float):
        """Add a line chart point."""
        self.line_timestamps.append(timestamp)
        self.line_values.append(price)

    def get_recent_candles(self, minutes: Optional[int] = None) -> List[OHLCV]:
        """Get candles, optionally filtered to recent minutes."""
        if minutes is None:
            return self.candles
        cutoff = datetime.now() - timedelta(minutes=minutes)
        return [c for c in self.candles if c.timestamp >= cutoff]

    def get_recent_line_points(self, minutes: Optional[int] = None) -> Tuple[List[datetime], List[float]]:
        """Get line points, optionally filtered to recent minutes."""
        if minutes is None:
            return self.line_timestamps, self.line_values
        cutoff = datetime.now() - timedelta(minutes=minutes)
        filtered_times = []
        filtered_values = []
        for t, v in zip(self.line_timestamps, self.line_values):
            if t >= cutoff:
                filtered_times.append(t)
                filtered_values.append(v)
        return filtered_times, filtered_values


class PriceChart(tk.Canvas):
    """Advanced price chart with candlesticks, line, overlays, indicators, markers, and screenshot."""

    CHART_MODES = ["line", "candlestick"]
    TIME_RANGES = {
        "1h": 60,
        "4h": 240,
        "24h": 1440,
        "ALL": None,
    }
    INDICATORS = {
        "ema_12": "EMA 12",
        "ema_26": "EMA 26",
        "rsi_14": "RSI 14",
        "macd": "MACD",
    }

    def __init__(self, parent, height=320, **kwargs):
        self.bg_color = kwargs.pop("bg", SURFACE)
        super().__init__(parent, bg=self.bg_color, highlightthickness=0, height=height, **kwargs)

        self.series: Dict[str, ChartSeries] = {}
        self.mode = "candlestick"
        self.time_range = "ALL"
        self.hover_index: Optional[int] = None
        self.hover_series: Optional[str] = None
        self.auto_scroll = True
        self.max_candles = 100
        self.max_line_points = 100

        # Indicators — enable EMA 26, RSI 14, MACD by default
        self.indicators: Dict[str, bool] = {
            "ema_12": False,
            "ema_26": True,
            "rsi_14": True,
            "macd": True,
        }
        self.indicator_panels: Dict[str, float] = {}  # indicator -> height fraction

        # Trade markers
        self.markers: List[TradeMarker] = []

        # Y-axis zoom state
        self.y_zoom_start: Optional[float] = None
        self.y_zoom_end: Optional[float] = None
        self.y_zoom_dragging = False
        self.y_zoom_anchor_y: Optional[int] = None

        self.pad_left = 65
        self.pad_right = 20
        self.pad_top = 44
        self.pad_bottom = 52
        self.indicator_height = 60  # Height for each indicator panel

        self.colors = [ACCENT, "#f59e0b", "#3b82f6", "#a855f7", "#ec4899", "#22c55e", "#ef4444"]

        self.line_color = ACCENT
        self.volume_color = ACCENT_DIM
        self.grid_color = BORDER_LIGHT
        self.text_color = TEXT_MID
        self.crosshair_color = TEXT_DIM

        self.bind("<Configure>", self._on_resize)
        self.bind("<Motion>", self._on_mouse_move)
        self.bind("<Leave>", self._on_mouse_leave)
        
        # Y-axis zoom bindings
        self.bind("<ButtonPress-3>", self._on_y_zoom_start)  # Right-click to start zoom
        self.bind("<B3-Motion>", self._on_y_zoom_drag)
        self.bind("<ButtonRelease-3>", self._on_y_zoom_end)
        self.bind("<Double-Button-3>", self._on_y_zoom_reset)  # Double right-click to reset

    def _on_resize(self, event):
        self.draw()

    def _on_mouse_move(self, event):
        if not self.series:
            return

        width = self.winfo_width()
        plot_width = width - self.pad_left - self.pad_right

        if plot_width <= 0:
            return

        x = event.x - self.pad_left
        x = max(0, min(x, plot_width))

        best_dist = float("inf")
        best_idx = None
        best_series = None

        for symbol, series in self.series.items():
            if not series.visible:
                continue

            if self.mode == "candlestick" and series.candles:
                candles = series.get_recent_candles(self.TIME_RANGES[self.time_range])
                if len(candles) < 2:
                    continue
                idx = int((x / plot_width) * (len(candles) - 1))
                idx = max(0, min(idx, len(candles) - 1))
                cx = self.pad_left + (idx / (len(candles) - 1)) * plot_width
                dist = abs(cx - event.x)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
                    best_series = symbol

            elif self.mode == "line" and series.line_values:
                times, values = series.get_recent_line_points(self.TIME_RANGES[self.time_range])
                if len(values) < 2:
                    continue
                idx = int((x / plot_width) * (len(values) - 1))
                idx = max(0, min(idx, len(values) - 1))
                cx = self.pad_left + (idx / (len(values) - 1)) * plot_width
                dist = abs(cx - event.x)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = idx
                    best_series = symbol

        if best_idx != self.hover_index or best_series != self.hover_series:
            self.hover_index = best_idx
            self.hover_series = best_series
            self.draw()

    def _on_mouse_leave(self, event):
        if self.hover_index is not None or self.hover_series is not None:
            self.hover_index = None
            self.hover_series = None
            self.draw()

    def _on_y_zoom_start(self, event):
        """Start Y-axis zoom drag."""
        if event.x < self.pad_left:  # Only in Y-axis area
            self.y_zoom_dragging = True
            self.y_zoom_anchor_y = event.y
            self.y_zoom_start = event.y
            self.y_zoom_end = event.y

    def _on_y_zoom_drag(self, event):
        """Update Y-axis zoom selection."""
        if self.y_zoom_dragging:
            self.y_zoom_end = event.y
            self.draw()
            # Draw zoom selection rectangle
            self._draw_y_zoom_selection()

    def _on_y_zoom_end(self, event):
        """Complete Y-axis zoom."""
        if self.y_zoom_dragging and self.y_zoom_start is not None and self.y_zoom_end is not None:
            self.y_zoom_dragging = False
            
            # Convert y coordinates to price range
            height = self.winfo_height()
            price_plot_height = height - self.pad_top - self.pad_bottom
            
            if price_plot_height <= 0:
                return
            
            min_price, max_price = self._get_price_range()
            if min_price is None or max_price is None:
                return
            
            # Convert y positions to prices (inverted y-axis)
            y1 = min(self.y_zoom_start, self.y_zoom_end)
            y2 = max(self.y_zoom_start, self.y_zoom_end)
            
            price_at_y1 = max_price - ((y1 - self.pad_top) / price_plot_height) * (max_price - min_price)
            price_at_y2 = max_price - ((y2 - self.pad_top) / price_plot_height) * (max_price - min_price)
            
            # Apply zoom if selection is significant
            if abs(price_at_y1 - price_at_y2) > (max_price - min_price) * 0.1:
                self._apply_y_zoom(price_at_y2, price_at_y1)  # min, max
            
            self.y_zoom_start = None
            self.y_zoom_end = None
            self.draw()

    def _on_y_zoom_reset(self, event):
        """Reset Y-axis zoom."""
        self.y_zoom_start = None
        self.y_zoom_end = None
        self.draw()

    def _apply_y_zoom(self, min_price: float, max_price: float):
        """Apply Y-axis zoom to price range."""
        # Store zoomed range
        self._zoomed_min_price = min_price
        self._zoomed_max_price = max_price

    def _draw_y_zoom_selection(self):
        """Draw Y-axis zoom selection rectangle."""
        if self.y_zoom_start is None or self.y_zoom_end is None:
            return
        
        y1 = min(self.y_zoom_start, self.y_zoom_end)
        y2 = max(self.y_zoom_start, self.y_zoom_end)
        
        # Draw semi-transparent selection rectangle
        self.create_rectangle(
            0, y1, self.pad_left, y2,
            fill=ACCENT_DIM, outline=ACCENT, width=1,
            stipple="gray25",
            tags=("y_zoom",)
        )
        
        # Draw price range labels
        height = self.winfo_height()
        price_plot_height = height - self.pad_top - self.pad_bottom
        
        if price_plot_height > 0:
            min_price, max_price = self._get_price_range()
            if min_price is not None and max_price is not None:
                price_at_y1 = max_price - ((y1 - self.pad_top) / price_plot_height) * (max_price - min_price)
                price_at_y2 = max_price - ((y2 - self.pad_top) / price_plot_height) * (max_price - min_price)
                
                # Draw price labels
                self.create_text(
                    self.pad_left - 5, y1,
                    text=self._format_price(price_at_y1),
                    fill=ACCENT,
                    font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
                    anchor="e",
                    tags=("y_zoom",)
                )
                self.create_text(
                    self.pad_left - 5, y2,
                    text=self._format_price(price_at_y2),
                    fill=ACCENT,
                    font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
                    anchor="e",
                    tags=("y_zoom",)
                )

    def add_series(self, symbol: str, chain: str = "", color: Optional[str] = None):
        """Add a chart series."""
        if symbol not in self.series:
            idx = len(self.series) % len(self.colors)
            self.series[symbol] = ChartSeries(symbol, chain, color or self.colors[idx])
        return self.series[symbol]

    def remove_series(self, symbol: str):
        """Remove a chart series."""
        self.series.pop(symbol, None)
        self.draw()

    def set_series_visibility(self, symbol: str, visible: bool):
        """Toggle series visibility."""
        if symbol in self.series:
            self.series[symbol].visible = visible
            self.draw()

    def add_candle(self, symbol: str, candle: OHLCV):
        """Add a candle to a series."""
        series = self.add_series(symbol)
        series.add_candle(candle)
        if self.auto_scroll and len(series.candles) > self.max_candles:
            series.candles = series.candles[-self.max_candles:]
        self.draw()

    def add_line_point(self, symbol: str, timestamp: datetime, price: float):
        """Add a line point to a series."""
        series = self.add_series(symbol)
        series.add_line_point(timestamp, price)
        if self.auto_scroll and len(series.line_values) > self.max_line_points:
            series.line_values = series.line_values[-self.max_line_points:]
            series.line_timestamps = series.line_timestamps[-self.max_line_points:]
        self.draw()

    def set_candles(self, symbol: str, candles: List[OHLCV], chain: str = ""):
        """Set full candle data for a series."""
        series = self.add_series(symbol, chain)
        series.candles = list(candles)
        if self.auto_scroll and len(series.candles) > self.max_candles:
            series.candles = series.candles[-self.max_candles:]
        self.draw()

    def set_line_data(self, symbol: str, timestamps: List[datetime], prices: List[float], chain: str = ""):
        """Set full line data for a series."""
        series = self.add_series(symbol, chain)
        series.line_timestamps = list(timestamps)
        series.line_values = list(prices)
        if self.auto_scroll and len(series.line_values) > self.max_line_points:
            series.line_values = series.line_values[-self.max_line_points:]
            series.line_timestamps = series.line_timestamps[-self.max_line_points:]
        self.draw()

    def add_marker(self, marker: TradeMarker):
        """Add a trade marker."""
        self.markers.append(marker)
        self.draw()

    def clear_markers(self):
        """Clear all trade markers."""
        self.markers = []
        self.draw()

    def set_mode(self, mode: str):
        """Set chart mode: line or candlestick."""
        if mode in self.CHART_MODES:
            self.mode = mode
            self.draw()

    def set_time_range(self, range_key: str):
        """Set time range: 1h, 4h, 24h, ALL."""
        if range_key in self.TIME_RANGES:
            self.time_range = range_key
            self.draw()

    def set_indicator(self, indicator: str, enabled: bool):
        """Enable/disable an indicator."""
        if indicator in self.INDICATORS:
            self.indicators[indicator] = enabled
            self.draw()

    def set_auto_scroll(self, enabled: bool):
        """Enable/disable auto-scroll."""
        self.auto_scroll = enabled
        self.draw()

    def clear(self):
        """Clear all series and markers."""
        self.series = {}
        self.markers = []
        self.hover_index = None
        self.hover_series = None
        self.delete("all")

    def save_screenshot(self, filename: Optional[str] = None):
        """Save chart screenshot as PNG."""
        if filename is None:
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
            )
        
        if not filename:
            return

        try:
            # Try PIL first
            from PIL import Image, ImageDraw
            self._save_screenshot_pil(filename)
        except ImportError:
            # Fallback to PostScript
            self._save_screenshot_ps(filename)

    def _save_screenshot_pil(self, filename: str):
        """Save screenshot using PIL."""
        from PIL import Image, ImageDraw

        width = self.winfo_width()
        height = self.winfo_height()

        # Create image with background color
        hex_color = self.bg_color.lstrip("#")
        bg = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        img = Image.new("RGB", (width, height), bg)
        draw = ImageDraw.Draw(img)

        # This is a simplified screenshot - for full fidelity, use postscript
        # Draw title
        visible_series = [s for s in self.series.values() if s.visible]
        title = visible_series[0].symbol if len(visible_series) == 1 else "Price Chart"
        draw.text((self.pad_left, 10), title, fill=(232, 234, 237))

        # Draw simple lines for each visible series
        min_p, max_p = self._get_price_range()
        if min_p is None:
            img.save(filename)
            return

        plot_width = width - self.pad_left - self.pad_right
        plot_height = height - self.pad_top - self.pad_bottom

        for series in visible_series:
            if self.mode == "line" and series.line_values:
                _, values = series.get_recent_line_points(self.TIME_RANGES[self.time_range])
                if len(values) < 2:
                    continue
                points = []
                for i, v in enumerate(values):
                    x = self.pad_left + (i / (len(values) - 1)) * plot_width
                    y = self.pad_top + (1 - (v - min_p) / (max_p - min_p)) * plot_height
                    points.append((x, y))
                if len(points) >= 2:
                    draw.line(points, fill=self._hex_to_rgb(series.color), width=2)

        img.save(filename)
        print(f"Chart screenshot saved to {filename}")

    def _save_screenshot_ps(self, filename: str):
        """Save screenshot using PostScript."""
        ps_filename = filename.replace(".png", ".ps") if not filename.endswith(".ps") else filename
        self.postscript(file=ps_filename, colormode="color", pagewidth=self.winfo_width(), pageheight=self.winfo_height())
        print(f"Chart screenshot saved to {ps_filename}")

    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def draw(self):
        """Draw the chart."""
        self.delete("all")

        if not self.series or not any(s.visible and (s.candles or s.line_values) for s in self.series.values()):
            self._draw_empty()
            return

        width = self.winfo_width()
        height = self.winfo_height()

        # Calculate indicator panel heights
        active_indicators = [k for k, v in self.indicators.items() if v]
        indicator_total_height = len(active_indicators) * self.indicator_height
        price_plot_height = height - self.pad_top - self.pad_bottom - indicator_total_height

        plot_width = width - self.pad_left - self.pad_right

        if plot_width <= 0 or price_plot_height <= 0:
            return

        min_price, max_price = self._get_price_range()
        if min_price is None:
            self._draw_empty()
            return

        price_range = max_price - min_price
        if price_range == 0:
            price_range = max_price * 0.01 or 1.0
            min_price -= price_range / 2
            max_price += price_range / 2
            price_range = max_price - min_price

        # Only add padding if not zoomed
        if not (hasattr(self, '_zoomed_min_price') and self._zoomed_min_price is not None):
            padding = price_range * 0.05
            min_price -= padding
            max_price += padding
            price_range = max_price - min_price

        # Draw main price grid
        self._draw_grid(plot_width, price_plot_height, min_price, max_price)

        # Draw volumes
        self._draw_volumes(plot_width, price_plot_height, min_price, max_price)

        # Draw main data
        if self.mode == "candlestick":
            self._draw_candles(plot_width, price_plot_height, min_price, max_price)
        else:
            self._draw_lines(plot_width, price_plot_height, min_price, max_price)

        # Draw indicators overlay
        self._draw_indicators(plot_width, price_plot_height, min_price, max_price)

        # Draw trade markers
        self._draw_markers(plot_width, price_plot_height, min_price, max_price)

        # Hover crosshair
        self._draw_hover(plot_width, price_plot_height, min_price, max_price)

        # Draw indicator panels below price chart
        self._draw_indicator_panels(plot_width, price_plot_height)

        # X-axis time labels
        self._draw_time_axis(plot_width, price_plot_height)

        # Title and legend
        self._draw_title_and_legend(width)
        
        # Draw y-zoom selection if active
        if self.y_zoom_dragging:
            self._draw_y_zoom_selection()

    def _get_price_range(self) -> Tuple[Optional[float], Optional[float]]:
        """Get min/max price across visible series."""
        # Check if zoomed range is set
        if hasattr(self, '_zoomed_min_price') and hasattr(self, '_zoomed_max_price'):
            if self._zoomed_min_price is not None and self._zoomed_max_price is not None:
                return self._zoomed_min_price, self._zoomed_max_price

        min_price = None
        max_price = None

        for series in self.series.values():
            if not series.visible:
                continue

            if self.mode == "candlestick" and series.candles:
                candles = series.get_recent_candles(self.TIME_RANGES[self.time_range])
                for c in candles:
                    if min_price is None or c.low < min_price:
                        min_price = c.low
                    if max_price is None or c.high > max_price:
                        max_price = c.high

            elif self.mode == "line" and series.line_values:
                _, values = series.get_recent_line_points(self.TIME_RANGES[self.time_range])
                for v in values:
                    if min_price is None or v < min_price:
                        min_price = v
                    if max_price is None or v > max_price:
                        max_price = v

        return min_price, max_price

    def _draw_grid(self, plot_width: float, plot_height: float, min_price: float, max_price: float):
        """Draw grid and price labels."""
        n_lines = 5
        for i in range(n_lines + 1):
            y = self.pad_top + (i / n_lines) * plot_height
            price = max_price - (i / n_lines) * (max_price - min_price)

            self.create_line(self.pad_left, y, self.pad_left + plot_width, y, fill=self.grid_color, tags=("grid",))
            self.create_text(
                self.pad_left - 10, y,
                text=self._format_price(price),
                fill=self.text_color,
                font=(FONT_FAMILY, FONT_SIZE_SM),
                anchor="e",
                tags=("grid",)
            )

        self.create_rectangle(
            self.pad_left, self.pad_top,
            self.pad_left + plot_width, self.pad_top + plot_height,
            outline=self.grid_color,
            tags=("border",)
        )

    def _draw_time_axis(self, plot_width: float, price_plot_height: float):
        """Draw readable time labels along X-axis."""
        # Get primary series timestamps
        primary = None
        for s in self.series.values():
            if s.visible:
                primary = s
                break

        if not primary:
            return

        height = self.winfo_height()
        y = self.pad_top + price_plot_height + 22  # Below the chart area

        if self.mode == "candlestick" and primary.candles:
            candles = primary.get_recent_candles(self.TIME_RANGES[self.time_range])
            if len(candles) < 2:
                return
            timestamps = [c.timestamp for c in candles]
        elif self.mode == "line" and primary.line_timestamps:
            times, _ = primary.get_recent_line_points(self.TIME_RANGES[self.time_range])
            if len(times) < 2:
                return
            timestamps = times
        else:
            return

        # Draw 5-7 evenly spaced time labels
        n_labels = min(7, len(timestamps))
        for i in range(n_labels):
            idx = int((i / (n_labels - 1)) * (len(timestamps) - 1)) if n_labels > 1 else 0
            ts = timestamps[idx]
            x = self.pad_left + (idx / (len(timestamps) - 1)) * plot_width

            # Format: "Jul 15 14:30" or just "14:30" if same day
            from datetime import datetime as _dt
            now = _dt.now()
            if ts.date() == now.date():
                label = ts.strftime("%H:%M")
            else:
                label = ts.strftime("%b %d %H:%M")

            self.create_text(
                x, y,
                text=label,
                fill=TEXT_MID,
                font=(FONT_FAMILY, FONT_SIZE_SM),
                anchor="n",
                tags=("time_axis",)
            )

    def _draw_volumes(self, plot_width: float, plot_height: float, min_price: float, max_price: float):
        """Draw volume bars for the first visible series."""
        height = self.winfo_height()

        for series in self.series.values():
            if not series.visible or not series.candles:
                continue

            candles = series.get_recent_candles(self.TIME_RANGES[self.time_range])
            if len(candles) < 2:
                continue

            max_volume = max(c.volume for c in candles)
            if max_volume <= 0:
                continue

            volume_height = plot_height * 0.22
            y_bottom = self.pad_top + plot_height

            bar_width = max(1, plot_width / len(candles) * 0.55)

            for i, c in enumerate(candles):
                x = self.pad_left + (i / (len(candles) - 1)) * plot_width
                bar_h = (c.volume / max_volume) * volume_height
                y_top = y_bottom - bar_h
                self.create_rectangle(
                    x - bar_width / 2, y_top,
                    x + bar_width / 2, y_bottom,
                    fill=self.volume_color, outline="",
                    tags=("volume",)
                )
            break

    def _draw_candles(self, plot_width: float, plot_height: float, min_price: float, max_price: float):
        """Draw candlestick chart."""
        for series in self.series.values():
            if not series.visible:
                continue

            candles = series.get_recent_candles(self.TIME_RANGES[self.time_range])
            if len(candles) < 2:
                continue

            candle_width = max(2, plot_width / len(candles) * 0.65)

            for i, c in enumerate(candles):
                x = self.pad_left + (i / (len(candles) - 1)) * plot_width

                y_open = self.pad_top + (1 - (c.open - min_price) / (max_price - min_price)) * plot_height
                y_close = self.pad_top + (1 - (c.close - min_price) / (max_price - min_price)) * plot_height
                y_high = self.pad_top + (1 - (c.high - min_price) / (max_price - min_price)) * plot_height
                y_low = self.pad_top + (1 - (c.low - min_price) / (max_price - min_price)) * plot_height

                is_bullish = c.close >= c.open
                color = series.color if is_bullish else ERROR
                fill = series.color if is_bullish else self.bg_color

                self.create_line(x, y_high, x, y_low, fill=color, width=1, tags=("candle",))

                top = min(y_open, y_close)
                bottom = max(y_open, y_close)
                body_height = max(1, bottom - top)
                self.create_rectangle(
                    x - candle_width / 2, top,
                    x + candle_width / 2, top + body_height,
                    fill=fill, outline=color, width=1,
                    tags=("candle",)
                )

    def _draw_lines(self, plot_width: float, plot_height: float, min_price: float, max_price: float):
        """Draw line chart for all visible series."""
        for series in self.series.values():
            if not series.visible:
                continue

            times, values = series.get_recent_line_points(self.TIME_RANGES[self.time_range])
            if len(values) < 2:
                continue

            points = []
            for i, v in enumerate(values):
                x = self.pad_left + (i / (len(values) - 1)) * plot_width
                y = self.pad_top + (1 - (v - min_price) / (max_price - min_price)) * plot_height
                points.extend([x, y])

            if len(points) >= 4:
                self.create_line(points, fill=series.color, width=2, smooth=True, tags=("line",))

                last_x, last_y = points[-2], points[-1]
                self.create_oval(last_x - 4, last_y - 4, last_x + 4, last_y + 4, fill=series.color, outline=TEXT_BRIGHT, width=1, tags=("line",))

    def _draw_indicators(self, plot_width: float, plot_height: float, min_price: float, max_price: float):
        """Draw indicator overlays on price chart."""
        # Get primary visible series
        primary = None
        for series in self.series.values():
            if series.visible:
                primary = series
                break

        if not primary:
            return

        candles = primary.get_recent_candles(self.TIME_RANGES[self.time_range])
        if len(candles) < 26:
            return

        closes = [c.close for c in candles]

        if self.indicators.get("ema_12"):
            self._draw_ema_line(closes, plot_width, plot_height, min_price, max_price, 12, "#f59e0b")
        if self.indicators.get("ema_26"):
            self._draw_ema_line(closes, plot_width, plot_height, min_price, max_price, 26, "#3b82f6")

    def _draw_ema_line(self, closes: List[float], plot_width: float, plot_height: float, min_price: float, max_price: float, period: int, color: str):
        """Draw EMA line."""
        ema = self._calculate_ema(closes, period)
        if len(ema) < 2:
            return

        points = []
        for i, v in enumerate(ema):
            if v is None:
                continue
            x = self.pad_left + (i / (len(closes) - 1)) * plot_width
            y = self.pad_top + (1 - (v - min_price) / (max_price - min_price)) * plot_height
            points.extend([x, y])

        if len(points) >= 4:
            self.create_line(points, fill=color, width=1, smooth=True, tags=("indicator",))

    def _draw_indicator_panels(self, plot_width: float, price_plot_height: float):
        """Draw separate indicator panels (RSI, MACD)."""
        active = [k for k, v in self.indicators.items() if v and k in ("rsi_14", "macd")]
        if not active:
            return

        height = self.winfo_height()
        y_start = self.pad_top + price_plot_height

        for i, indicator in enumerate(active):
            panel_y = y_start + i * self.indicator_height
            panel_height = self.indicator_height - 8

            # Panel border
            self.create_rectangle(
                self.pad_left, panel_y,
                self.pad_left + plot_width, panel_y + panel_height,
                outline=self.grid_color,
                tags=("indicator_panel",)
            )

            label = self.INDICATORS[indicator]
            self.create_text(
                self.pad_left + 5, panel_y + 10,
                text=label,
                fill=TEXT_MID,
                font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
                anchor="w",
                tags=("indicator_panel",)
            )

            # Get primary series
            primary = None
            for s in self.series.values():
                if s.visible:
                    primary = s
                    break

            if not primary:
                continue

            candles = primary.get_recent_candles(self.TIME_RANGES[self.time_range])
            if len(candles) < 26:
                continue

            closes = [c.close for c in candles]

            if indicator == "rsi_14":
                self._draw_rsi_panel(closes, plot_width, panel_height, panel_y)
            elif indicator == "macd":
                self._draw_macd_panel(closes, plot_width, panel_height, panel_y)

    def _draw_rsi_panel(self, closes: List[float], plot_width: float, panel_height: float, panel_y: float):
        """Draw RSI panel."""
        rsi = self._calculate_rsi(closes, 14)
        if len(rsi) < 2:
            return

        # Overbought/oversold lines
        ob_y = panel_y + panel_height * 0.2
        os_y = panel_y + panel_height * 0.8
        self.create_line(self.pad_left, ob_y, self.pad_left + plot_width, ob_y, fill=BORDER_LIGHT, dash=(2, 2), tags=("indicator_panel",))
        self.create_line(self.pad_left, os_y, self.pad_left + plot_width, os_y, fill=BORDER_LIGHT, dash=(2, 2), tags=("indicator_panel",))

        points = []
        for i, v in enumerate(rsi):
            if v is None:
                continue
            x = self.pad_left + (i / (len(closes) - 1)) * plot_width
            y = panel_y + panel_height - (v / 100) * panel_height
            points.extend([x, y])

        if len(points) >= 4:
            self.create_line(points, fill=ACCENT, width=1, smooth=True, tags=("indicator_panel",))

    def _draw_macd_panel(self, closes: List[float], plot_width: float, panel_height: float, panel_y: float):
        """Draw MACD panel."""
        macd, signal, hist = self._calculate_macd(closes)
        if len(macd) < 2:
            return

        # Normalize to panel
        max_val = max(abs(v) for v in macd + signal + hist if v is not None) or 1

        zero_y = panel_y + panel_height / 2
        self.create_line(self.pad_left, zero_y, self.pad_left + plot_width, zero_y, fill=BORDER_LIGHT, tags=("indicator_panel",))

        for i, (m, s, h) in enumerate(zip(macd, signal, hist)):
            if m is None or s is None:
                continue
            x = self.pad_left + (i / (len(closes) - 1)) * plot_width

            my = zero_y - (m / max_val) * (panel_height / 2) * 0.8
            sy = zero_y - (s / max_val) * (panel_height / 2) * 0.8

            bar_color = SUCCESS if h and h >= 0 else ERROR
            bar_h = abs(h / max_val) * (panel_height / 2) * 0.8
            self.create_rectangle(x - 1, zero_y, x + 1, zero_y - (h / max_val) * (panel_height / 2) * 0.8, fill=bar_color, outline="", tags=("indicator_panel",))

        # Draw MACD and signal lines
        m_points = []
        s_points = []
        for i, (m, s) in enumerate(zip(macd, signal)):
            if m is None or s is None:
                continue
            x = self.pad_left + (i / (len(closes) - 1)) * plot_width
            my = zero_y - (m / max_val) * (panel_height / 2) * 0.8
            sy = zero_y - (s / max_val) * (panel_height / 2) * 0.8
            m_points.extend([x, my])
            s_points.extend([x, sy])

        if len(m_points) >= 4:
            self.create_line(m_points, fill="#f59e0b", width=1, smooth=True, tags=("indicator_panel",))
        if len(s_points) >= 4:
            self.create_line(s_points, fill="#3b82f6", width=1, smooth=True, tags=("indicator_panel",))

    def _draw_markers(self, plot_width: float, plot_height: float, min_price: float, max_price: float):
        """Draw trade entry/exit markers."""
        # Get primary series timestamps for mapping
        primary = None
        for s in self.series.values():
            if s.visible:
                primary = s
                break

        if not primary:
            return

        if self.mode == "candlestick" and primary.candles:
            candles = primary.get_recent_candles(self.TIME_RANGES[self.time_range])
            if not candles:
                return
            min_ts = candles[0].timestamp
            max_ts = candles[-1].timestamp
            ts_range = (max_ts - min_ts).total_seconds()
        elif self.mode == "line" and primary.line_values:
            times, _ = primary.get_recent_line_points(self.TIME_RANGES[self.time_range])
            if not times:
                return
            min_ts = times[0]
            max_ts = times[-1]
            ts_range = (max_ts - min_ts).total_seconds()
        else:
            return

        if ts_range <= 0:
            return

        for marker in self.markers:
            if marker.timestamp < min_ts or marker.timestamp > max_ts:
                continue

            x = self.pad_left + ((marker.timestamp - min_ts).total_seconds() / ts_range) * plot_width
            y = self.pad_top + (1 - (marker.price - min_price) / (max_price - min_price)) * plot_height

            if marker.action == "buy":
                # Green up triangle
                self.create_polygon(
                    x, y - 12, x - 6, y, x + 6, y,
                    fill=SUCCESS, outline=TEXT_BRIGHT, width=1,
                    tags=("marker",)
                )
                text = "B"
                color = SUCCESS
            else:
                # Red down triangle
                self.create_polygon(
                    x, y + 12, x - 6, y, x + 6, y,
                    fill=ERROR, outline=TEXT_BRIGHT, width=1,
                    tags=("marker",)
                )
                text = "S"
                color = ERROR

            self.create_text(
                x, y + (18 if marker.action == "buy" else -18),
                text=f"{text} ${marker.price:.4f}",
                fill=color,
                font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
                tags=("marker",)
            )

    def _draw_hover(self, plot_width: float, plot_height: float, min_price: float, max_price: float):
        """Draw hover crosshair and tooltip."""
        if self.hover_index is None or self.hover_series is None:
            return

        series = self.series.get(self.hover_series)
        if not series or not series.visible:
            return

        height = self.winfo_height()

        if self.mode == "candlestick" and series.candles:
            candles = series.get_recent_candles(self.TIME_RANGES[self.time_range])
            if self.hover_index >= len(candles):
                return
            c = candles[self.hover_index]
            x = self.pad_left + (self.hover_index / (len(candles) - 1)) * plot_width
            y = self.pad_top + (1 - (c.close - min_price) / (max_price - min_price)) * plot_height

            time_str = c.timestamp.strftime("%H:%M:%S")
            label = f"{series.symbol}  O:{c.open:.6f} H:{c.high:.6f} L:{c.low:.6f} C:{c.close:.6f}  {time_str}"

        elif self.mode == "line" and series.line_values:
            times, values = series.get_recent_line_points(self.TIME_RANGES[self.time_range])
            if self.hover_index >= len(values):
                return
            x = self.pad_left + (self.hover_index / (len(values) - 1)) * plot_width
            y = self.pad_top + (1 - (values[self.hover_index] - min_price) / (max_price - min_price)) * plot_height

            time_str = times[self.hover_index].strftime("%H:%M:%S")
            label = f"{series.symbol}  ${values[self.hover_index]:,.6f}  {time_str}"
        else:
            return

        self.create_line(x, self.pad_top, x, self.pad_top + plot_height, fill=self.crosshair_color, dash=(4, 4), tags=("crosshair",))
        self.create_oval(x - 4, y - 4, x + 4, y + 4, fill=ACCENT_BRIGHT, outline=TEXT_BRIGHT, width=2, tags=("crosshair",))

        self.create_text(
            x + 10, y - 24,
            text=label,
            fill=TEXT_BRIGHT,
            font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
            anchor="w",
            tags=("crosshair",)
        )

    def _draw_title_and_legend(self, width: float):
        """Draw title and legend with proper spacing."""
        visible_series = [s for s in self.series.values() if s.visible]

        title = "Price Chart"
        if len(visible_series) == 1:
            title = visible_series[0].symbol
            if visible_series[0].chain:
                title += f" ({visible_series[0].chain})"

        # Draw title with more vertical offset to avoid overlap
        self.create_text(
            self.pad_left, 26,
            text=title,
            fill=TEXT_BRIGHT,
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            anchor="w",
            tags=("title",)
        )

        # Draw legend symbols from right to left with proper spacing
        x = width - self.pad_right
        legend_y = 26  # Same y as title
        
        for series in reversed(visible_series):
            x -= 8
            # Draw color line
            self.create_line(x, legend_y, x - 20, legend_y, fill=series.color, width=2, tags=("legend",))
            x -= 26
            # Draw symbol text
            text_id = self.create_text(
                x, legend_y,
                text=series.symbol,
                fill=series.color,
                font=(FONT_FAMILY, FONT_SIZE_SM, "bold"),
                anchor="e",
                tags=("legend",)
            )
            bbox = self.bbox(text_id)
            if bbox:
                x = bbox[0] - 16  # More spacing between legend items

    def _draw_empty(self):
        """Draw empty state."""
        width = self.winfo_width() or 400
        height = self.winfo_height() or 300

        self.create_text(
            width / 2, height / 2,
            text="No price data available",
            fill=TEXT_DIM,
            font=(FONT_FAMILY, FONT_SIZE, "bold"),
            tags=("empty",)
        )

    def _format_price(self, price: float) -> str:
        """Format price for display."""
        if price >= 1:
            return f"${price:,.2f}"
        elif price >= 0.01:
            return f"${price:,.4f}"
        else:
            return f"${price:,.6f}"

    def _calculate_ema(self, values: List[float], period: int) -> List[Optional[float]]:
        """Calculate EMA."""
        if len(values) < period:
            return [None] * len(values)

        multiplier = 2 / (period + 1)
        ema = [None] * (period - 1)
        ema.append(sum(values[:period]) / period)

        for i in range(period, len(values)):
            ema.append(values[i] * multiplier + ema[-1] * (1 - multiplier))

        return ema

    def _calculate_rsi(self, values: List[float], period: int = 14) -> List[Optional[float]]:
        """Calculate RSI."""
        if len(values) < period + 1:
            return [None] * len(values)

        rsi = [None] * period
        gains = []
        losses = []

        for i in range(1, len(values)):
            change = values[i] - values[i - 1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        if avg_loss == 0:
            rsi.append(100 if avg_gain > 0 else 50)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))

        for i in range(period + 1, len(values)):
            gain = gains[i - 1]
            loss = losses[i - 1]
            avg_gain = (avg_gain * (period - 1) + gain) / period
            avg_loss = (avg_loss * (period - 1) + loss) / period

            if avg_loss == 0:
                rsi.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi.append(100 - (100 / (1 + rs)))

        return rsi

    def _calculate_macd(self, values: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
        """Calculate MACD, signal, and histogram."""
        if len(values) < slow + signal:
            return [None] * len(values), [None] * len(values), [None] * len(values)

        ema_fast = self._calculate_ema(values, fast)
        ema_slow = self._calculate_ema(values, slow)

        macd = []
        for f, s in zip(ema_fast, ema_slow):
            if f is None or s is None:
                macd.append(None)
            else:
                macd.append(f - s)

        # Signal line is EMA of MACD
        valid_macd = [m for m in macd if m is not None]
        signal_ema = self._calculate_ema(valid_macd, signal)

        signal_line = [None] * (len(macd) - len(valid_macd)) + signal_ema
        histogram = []
        for m, s in zip(macd, signal_line):
            if m is None or s is None:
                histogram.append(None)
            else:
                histogram.append(m - s)

        return macd, signal_line, histogram


class MiniSparkline(tk.Canvas):
    """Tiny sparkline for embedding in lists."""

    def __init__(self, parent, width=80, height=24, color=ACCENT, **kwargs):
        super().__init__(parent, width=width, height=height, bg=SURFACE_CARD, highlightthickness=0, **kwargs)
        self.color = color
        self.values: List[float] = []

    def set_values(self, values: List[float]):
        """Set sparkline values."""
        self.values = list(values)
        self.draw()

    def draw(self):
        """Draw sparkline."""
        self.delete("all")

        if len(self.values) < 2:
            return

        width = self.winfo_width()
        height = self.winfo_height()

        min_v = min(self.values)
        max_v = max(self.values)
        range_v = max_v - min_v

        if range_v == 0:
            range_v = 1

        points = []
        for i, v in enumerate(self.values):
            x = (i / (len(self.values) - 1)) * width
            y = height - ((v - min_v) / range_v) * height * 0.8 - height * 0.1
            points.extend([x, y])

        if len(points) >= 4:
            self.create_line(points, fill=self.color, width=2, smooth=True)
