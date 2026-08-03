"""Main application window for the PolyCryptoAlpha trading bot UI."""

import os
import sys
import json
import queue
import threading
import datetime
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Simple file-based debug logger (bypasses loguru enqueue issues in PyInstaller)
_DEBUG_LOG = BASE_DIR / "logs" / "debug_startup.log"

def _dbg(msg):
    try:
        _DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} | {msg}\n")
            f.flush()
    except Exception:
        pass

_dbg("app.py module loading...")

from config.settings import Config
from ui.config import (
    BG,
    SURFACE,
    SURFACE_CARD,
    TEXT,
    TEXT_BRIGHT,
    ACCENT,
    ERROR,
    FONT_FAMILY,
    FONT_SIZE,
    DEFAULT_WIDTH,
    DEFAULT_HEIGHT,
    MIN_WIDTH,
    MIN_HEIGHT,
)
from ui.widgets.titlebar import Titlebar
from ui.widgets.sidebar import Sidebar
from ui.widgets.status_bar import StatusBar
from ui.widgets.dashboard import DashboardView
from ui.widgets.watchlist import WatchlistView
from ui.widgets.positions import PositionsView
from ui.widgets.trade_history import TradeHistoryView
from ui.widgets.ml_status import MLStatusView
from ui.widgets.journal import JournalView
from ui.widgets.sniper import SniperView
from ui.widgets.settings import SettingsView
from ui.widgets.log_panel import LogPanel
from ui.components import scrollbar_style
from ml.learning_journal import get_journal


class TradingBotApp(tk.Tk):
    """Main trading bot dashboard application."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("PolyCryptoAlpha Trading Bot")
        self.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.configure(bg=BG)
        
        # DPI awareness for multi-monitor support
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
        
        # Use withdraw/overrideredirect trick for custom titlebar on Windows
        # This preserves DPI scaling unlike raw overrideredirect
        self.withdraw()
        self.overrideredirect(True)
        
        # Show window after setup
        self.after(50, self.deiconify)
        
        # State
        self._is_maximized = False
        self._normal_geometry = None
        self._running = False
        self._live_mode = False
        self._bot_thread = None
        self._stop_event = threading.Event()
        self._ui_queue = queue.Queue()
        self._update_interval = 1000  # ms
        
        # Bot instance (lazy init)
        self.bot = None
        
        # Sniper bot (lazy init)
        self.sniper = None
        self._sniper_running = False

        # Learning journal
        self.journal = get_journal()

        # Chart marker tracking
        self._charted_markers: set = set()
        self._last_ml_loaded = None

        # Views
        self.views = {}
        self._current_view = None
        
        # Build UI
        scrollbar_style()
        self._build_ui()
        
        # Window position
        self._center_window()
        
        # Start UI update loop
        self._process_ui_queue()
        
        # Load settings
        self._load_settings()
    
    def _build_ui(self):
        """Build main application UI."""
        # Main container
        self.container = tk.Frame(self, bg=BG, highlightbackground=SURFACE, highlightthickness=1)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Titlebar
        self.titlebar = Titlebar(self.container, self)
        
        # Status bar
        self.status_bar = StatusBar(self.container, self)
        
        # Body
        self.body = tk.Frame(self.container, bg=BG)
        self.body.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = Sidebar(self.body, self)
        
        # Main content area
        self.content = tk.Frame(self.body, bg=BG)
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Views
        self.views["dashboard"] = DashboardView(self.content, self)
        self.views["watchlist"] = WatchlistView(self.content, self)
        self.views["sniper"] = SniperView(self.content, self)
        self.views["positions"] = PositionsView(self.content, self)
        self.views["trades"] = TradeHistoryView(self.content, self)
        self.views["ml"] = MLStatusView(self.content, self)
        self.views["journal"] = JournalView(self.content, self)
        self.views["settings"] = SettingsView(self.content, self)
        
        for view in self.views.values():
            view.place(relwidth=1, relheight=1)
            view.lower()
        
        # Log panel at bottom
        self.log_panel = LogPanel(self.content, self, height=180)
        self.log_panel.place(rely=0.72, relwidth=1, relheight=0.28)
        
        # Show dashboard
        self.show_view("dashboard")
        
        # Load existing journal notes
        for note in self.journal.get_recent_notes(20):
            self.views["journal"].add_trade_note(
                note.timestamp[:16].replace("T", " "),
                note.symbol,
                note.action,
                note.pnl,
                note.note,
            )
        self.views["journal"].update_insights(self.journal.get_insights())
        
        # Log startup
        self.log_message("PolyCryptoAlpha UI initialized", "accent")
        self.log_message(f"Mode: {'LIVE' if Config.LIVE_MODE else 'PAPER'}", "info")
    
    def _center_window(self):
        """Center window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def show_view(self, key):
        """Switch to a view."""
        if key not in self.views:
            return
        
        for view in self.views.values():
            view.lower()
        
        self.views[key].lift()
        self._current_view = key
        self.sidebar._update_selection(key)
    
    # ── Window Controls ─────────────────────────────────────
    
    def minimize_window(self):
        """Minimize window (requires temp overrideredirect toggle on Windows)."""
        self.overrideredirect(False)
        self.iconify()
        # Re-enable overrideredirect when window is restored
        self.bind("<Map>", self._on_restore_override)
    
    def _on_restore_override(self, event=None):
        """Re-enable custom titlebar after minimize restore."""
        self.after(10, lambda: self.overrideredirect(True))
        self.unbind("<Map>")
    
    def maximize_window(self):
        """Toggle maximize/restore."""
        if self._is_maximized:
            self.overrideredirect(True)
            self.geometry(self._normal_geometry)
            self._is_maximized = False
        else:
            self._normal_geometry = self.geometry()
            self.overrideredirect(False)
            self.state('zoomed')
            self._is_maximized = True
    
    def close_window(self):
        """Close application."""
        self.stop_bot()
        self.stop_sniper()
        self._save_settings()
        self.destroy()
    
    # ── Sniper Bot Control ───────────────────────────────────
    
    def start_sniper(self):
        """Start the Robinhood Chain sniper bot."""
        if self._sniper_running:
            return
        
        self._sniper_running = True
        self.views["sniper"].update_status(True)
        self.log_message("Robinhood Chain sniper bot started", "success")
        
        # Initialize sniper lazily
        if self.sniper is None:
            try:
                from sniper.sniper_bot import SniperBot
                from config.settings import Config
                self.sniper = SniperBot(
                    buy_amount_weth=Config.SNIPER_BUY_AMOUNT_WETH,
                    max_concurrent_buys=Config.SNIPER_MAX_CONCURRENT,
                    buy_delay_seconds=Config.SNIPER_BUY_DELAY,
                    auto_sell_pnl_pct=Config.SNIPER_AUTO_SELL_PNL_PCT,
                    auto_stop_loss_pct=Config.SNIPER_AUTO_STOP_LOSS_PCT,
                    paper_mode=not Config.LIVE_MODE,
                )
                
                # Wire up callbacks
                async def on_new_token(token):
                    self._ui_queue.put({
                        "type": "sniper_log",
                        "message": f"NEW: {token.address[:12]}... (pair: {token.pair_address[:12]}...)",
                        "level": "accent",
                    })
                
                async def on_buy(sniped):
                    self._ui_queue.put({
                        "type": "sniper_buy",
                        "token": {
                            "symbol": sniped.symbol,
                            "address": sniped.address,
                            "pair_address": sniped.pair_address,
                            "weth_spent": sniped.weth_spent,
                            "tokens_received": sniped.tokens_received,
                            "status": sniped.status,
                            "time": sniped.buy_time.strftime("%H:%M:%S"),
                        },
                    })
                
                async def on_error(msg):
                    self._ui_queue.put({
                        "type": "sniper_log",
                        "message": f"ERROR: {msg}",
                        "level": "error",
                    })
                
                self.sniper.on_new_token(on_new_token)
                self.sniper.on_buy(on_buy)
                self.sniper.on_error(on_error)
                
            except Exception as e:
                self.log_message(f"Failed to initialize sniper: {e}", "error")
                self._sniper_running = False
                self.views["sniper"].update_status(False)
                return
        
        # Run sniper in background thread
        def run_sniper():
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.sniper.start())
            except Exception as e:
                self._ui_queue.put({"type": "sniper_log", "message": f"Sniper error: {e}", "level": "error"})
            finally:
                loop.close()
                self._ui_queue.put({"type": "sniper_stopped"})
        
        t = threading.Thread(target=run_sniper, daemon=True)
        t.start()
    
    def stop_sniper(self):
        """Stop the sniper bot."""
        if not self._sniper_running:
            return
        self._sniper_running = False
        if self.sniper:
            self.sniper.stop()
        self.views["sniper"].update_status(False)
        self.log_message("Robinhood Chain sniper bot stopped", "warning")
    
    # ── Bot Control ─────────────────────────────────────────
    
    def start_bot(self):
        """Start the trading bot in a background thread."""
        if self._running:
            return
        
        if self._live_mode:
            result = messagebox.askyesno(
                "Confirm Live Trading",
                "LIVE MODE is enabled. Real money will be used.\n\nAre you sure you want to start?",
                icon="warning"
            )
            if not result:
                return
        
        self._running = True
        self._stop_event.clear()
        self.status_bar.set_running(True)
        self.sidebar.set_status(True, "LIVE" if self._live_mode else "PAPER")
        self.log_message("Bot started", "success")
        
        # Initialize bot lazily
        if self.bot is None:
            try:
                from bot_core import TradingBot
                self.bot = TradingBot()
                self.bot._ui_queue = self._ui_queue
            except Exception as e:
                self.log_message(f"Failed to initialize bot: {e}", "error")
                self._running = False
                self.status_bar.set_running(False)
                return
        
        self._bot_thread = threading.Thread(target=self._bot_loop, daemon=True)
        self._bot_thread.start()
    
    def stop_bot(self):
        """Stop the trading bot."""
        if not self._running:
            return
        
        self._running = False
        self._stop_event.set()
        self.status_bar.set_running(False)
        self.sidebar.set_status(False, "LIVE" if self._live_mode else "PAPER")
        self.log_message("Bot stopping...", "warning")
        
        if self.bot:
            try:
                import asyncio
                asyncio.run_coroutine_threadsafe(self.bot.shutdown(), self.bot_loop)
            except Exception:
                pass
    
    def _bot_loop(self):
        """Background thread running the bot."""
        import asyncio
        
        self.bot_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.bot_loop)
        
        async def run():
            try:
                # Warm start
                _dbg("BOT_THREAD: starting run()")
                self.bot._warm_from_csvs()
                _dbg("BOT_THREAD: warm_from_csvs done")
                
                # Load ML model on startup (bypasses bot.run() so we must do it here)
                _dbg(f"BOT_THREAD: model_dir={Config.MODELS_DIR}, exists={Config.MODELS_DIR.exists()}")
                try:
                    loaded = self.bot.inference.load()
                    _dbg(f"BOT_THREAD: inference.load() returned {loaded}, is_ready={self.bot.inference.is_ready}")
                    self._ui_queue.put({
                        "type": "log",
                        "message": f"ML model load: {'success' if loaded else 'no model found'} (is_ready={self.bot.inference.is_ready})",
                        "level": "info" if loaded else "warning",
                    })
                    if loaded:
                        self.bot.orchestrator.inference = self.bot.inference
                        _dbg("BOT_THREAD: assigned inference to orchestrator")
                except Exception as e:
                    import traceback
                    tb = traceback.format_exc()
                    _dbg(f"BOT_THREAD: inference.load() FAILED: {e}\n{tb}")
                    self._ui_queue.put({
                        "type": "log",
                        "message": f"ML model load FAILED: {e}\n{tb}",
                        "level": "error",
                    })
                
                # Update watchlist
                _dbg("BOT_THREAD: updating watchlist...")
                await self.bot._update_watchlist()
                _dbg("BOT_THREAD: watchlist updated")
                
                # Force initial price fetch so UI shows data immediately
                try:
                    _dbg("BOT_THREAD: initial price fetch...")
                    updated = await self.bot.price_feed.update_all()
                    _dbg(f"BOT_THREAD: initial price fetch done: {len(updated)} tokens")
                    self._ui_queue.put({
                        "type": "log",
                        "message": f"Initial price fetch: {len(updated)} tokens",
                        "level": "info",
                    })
                except Exception as e:
                    import traceback
                    _dbg(f"BOT_THREAD: initial price fetch FAILED: {e}\n{traceback.format_exc()}")
                    self._ui_queue.put({
                        "type": "log",
                        "message": f"Initial price fetch failed: {e}",
                        "level": "error",
                    })
                
                _dbg("BOT_THREAD: entering while loop")
                while not self._stop_event.is_set():
                    try:
                        self.bot.cycle_count += 1
                        await self.bot._trading_cycle()
                    except Exception as e:
                        import traceback
                        _dbg(f"BOT_THREAD: cycle error: {e}\n{traceback.format_exc()}")
                        self._ui_queue.put({"type": "log", "message": f"Cycle error: {e}", "level": "error"})
                    
                    # Wait for next cycle
                    await asyncio.sleep(60)
                
                await self.bot.shutdown()
            except Exception as e:
                import traceback
                _dbg(f"BOT_THREAD: FATAL: {e}\n{traceback.format_exc()}")
                self._ui_queue.put({"type": "log", "message": f"Bot error: {e}", "level": "error"})
        
        try:
            self.bot_loop.run_until_complete(run())
        finally:
            self.bot_loop.close()
            self._ui_queue.put({"type": "bot_stopped"})
    
    # ── UI Update Queue ─────────────────────────────────────
    
    def _process_ui_queue(self):
        """Process messages from bot thread."""
        try:
            while True:
                msg = self._ui_queue.get_nowait()
                self._handle_ui_message(msg)
        except queue.Empty:
            pass
        except Exception:
            pass  # Don't let message handling crash the UI loop
        
        # Periodic refresh of market data
        try:
            self._refresh_ui()
        except Exception:
            pass  # _refresh_ui has its own error handling
        
        self.after(self._update_interval, self._process_ui_queue)
    
    def _handle_ui_message(self, msg):
        """Handle a UI queue message."""
        mtype = msg.get("type")
        
        if mtype == "log":
            self.log_message(msg["message"], msg.get("level", "info"))
        elif mtype == "bot_stopped":
            self._running = False
            self.status_bar.set_running(False)
            self.sidebar.set_status(False, "LIVE" if self._live_mode else "PAPER")
            self.log_message("Bot stopped", "warning")
        elif mtype == "trade":
            self.views["trades"].add_trade(msg["trade"])
            note_text = msg["trade"].get("note", "")
            self.views["journal"].add_trade_note(
                msg["trade"].get("time", ""),
                msg["trade"].get("symbol", ""),
                msg["trade"].get("action", ""),
                msg["trade"].get("pnl", 0),
                note_text,
            )
            # Persist to learning journal
            self.journal.add_trade_note(
                msg["trade"].get("symbol", ""),
                msg["trade"].get("action", ""),
                msg["trade"].get("pnl", 0),
                note_text,
                tags=[msg["trade"].get("reason", "")],
            )
            # Refresh insights periodically
            if len(self.journal.notes) % 5 == 0:
                insights = self.journal.analyze_patterns()
                self.views["journal"].update_insights(insights)
        elif mtype == "insight":
            self.views["journal"].update_insights(msg["text"])
        elif mtype == "sniper_log":
            self.views["sniper"].log(msg["message"], msg.get("level", "info"))
        elif mtype == "sniper_buy":
            token = msg["token"]
            self.views["sniper"].add_sniped_token(token)
            self.views["sniper"].log(
                f"BOUGHT {token['symbol']}: {token['tokens_received']:,.0f} tokens for {token['weth_spent']:.6f} WETH",
                "success",
            )
        elif mtype == "sniper_stopped":
            self._sniper_running = False
            self.views["sniper"].update_status(False)
            self.log_message("Sniper bot stopped", "warning")
    
    def _sync_trade_markers(self):
        """Sync trade entry/exit markers with the chart."""
        from ui.widgets.chart import TradeMarker

        # Markers for open positions (entry)
        for addr, pos in self.bot.position_manager.positions.items():
            marker_id = f"open_{addr}_{pos.entry_time.isoformat()}"
            if marker_id in self._charted_markers:
                continue

            self.views["dashboard"].price_chart.add_marker(TradeMarker(
                timestamp=pos.entry_time,
                price=pos.entry_price_usd,
                action="buy",
                symbol=pos.symbol,
            ))
            self._charted_markers.add(marker_id)

        # Markers for closed trades (exit)
        for trade in self.bot.position_manager.trade_history:
            marker_id = f"close_{trade.token_address}_{trade.exit_time.isoformat()}"
            if marker_id in self._charted_markers:
                continue

            self.views["dashboard"].price_chart.add_marker(TradeMarker(
                timestamp=trade.exit_time,
                price=trade.exit_price,
                action="sell",
                symbol=trade.symbol,
                pnl=trade.pnl_usd,
            ))
            self._charted_markers.add(marker_id)

    def _update_candles(self, symbol: str, token_address: str):
        """Build 1-minute OHLC candles from snapshot history for chart."""
        from ui.widgets.chart import OHLCV
        from datetime import timedelta
        
        history = self.bot.price_feed.get_history(token_address)
        if len(history) < 2:
            return
        
        # Group snapshots into 1-minute buckets
        candles = {}
        for snap in history:
            bucket = snap.timestamp.replace(second=0, microsecond=0)
            if bucket not in candles:
                candles[bucket] = {
                    "open": snap.price_usd,
                    "high": snap.price_usd,
                    "low": snap.price_usd,
                    "close": snap.price_usd,
                    "volume": snap.volume_1h_usd,
                }
            else:
                c = candles[bucket]
                c["high"] = max(c["high"], snap.price_usd)
                c["low"] = min(c["low"], snap.price_usd)
                c["close"] = snap.price_usd
                c["volume"] += snap.volume_1h_usd
        
        # Sort and create OHLCV objects
        ohlcv_list = []
        for ts in sorted(candles.keys()):
            c = candles[ts]
            ohlcv_list.append(OHLCV(
                timestamp=ts,
                open=c["open"],
                high=c["high"],
                low=c["low"],
                close=c["close"],
                volume=c["volume"],
            ))
        
        self.views["dashboard"].price_chart.set_candles(symbol, ohlcv_list)
    
    def _refresh_ui(self):
        """Refresh UI with latest bot data."""
        if self.bot is None:
            return
        
        # ── ML status FIRST (isolated try/except so it always updates) ──
        try:
            inf = self.bot.inference
            ml_loaded = inf.is_ready if inf is not None else False
            self.views["ml"].update_status(ml_loaded, "Model ready" if ml_loaded else "No model loaded")
            # Log once on state change to avoid spam
            if not hasattr(self, '_last_ml_loaded') or self._last_ml_loaded != ml_loaded:
                self.log_message(f"ML Status: {'LOADED' if ml_loaded else 'NOT LOADED'}"
                                 f" (inference={type(inf).__name__ if inf else 'None'},"
                                 f" is_ready={getattr(inf, 'is_ready', 'N/A')})", "info")
                self._last_ml_loaded = ml_loaded
        except Exception as e:
            self.log_message(f"ML status refresh error: {e}", "error")
        
        try:
            # Watchlist
            watchlist_tokens = []
            chart_symbols = []
            for addr, chain in list(self.bot.price_feed._watchlist.items()):
                try:
                    snap = self.bot.price_feed.get_latest(addr)
                    if snap is None:
                        continue
                    
                    risk = self.bot.token_scorer.score(snap)
                    
                    watchlist_tokens.append({
                        "symbol": snap.symbol,
                        "chain": chain,
                        "price": snap.price_usd,
                        "change_24h": snap.price_change_24h_pct,
                        "liquidity": snap.liquidity_usd,
                        "volume": snap.volume_24h_usd,
                        "score": risk.total_score,
                        "is_safe": risk.is_safe,
                        "signal": "—",
                    })
                    
                    # Add to chart symbols
                    if snap.symbol not in chart_symbols:
                        chart_symbols.append(snap.symbol)
                    
                    # Add price point to chart history
                    self.views["dashboard"].add_price_point(snap.symbol, snap.timestamp, snap.price_usd)
                    
                    # Build candles from snapshot history for candlestick mode
                    self._update_candles(snap.symbol, addr)
                except Exception as e:
                    self.log_message(f"Error processing {addr[:12]}: {e}", "error")
            
            self.views["watchlist"].update_watchlist(watchlist_tokens)
            self.views["dashboard"].update_chart_symbols(chart_symbols)

            # Sync trade markers
            self._sync_trade_markers()
            
            # Positions
            positions = []
            for addr, pos in self.bot.position_manager.positions.items():
                snap = self.bot.price_feed.get_latest(addr)
                current_price = snap.price_usd if snap else pos.entry_price_usd
                pnl = (current_price - pos.entry_price_usd) * pos.token_amount
                pnl_pct = ((current_price / pos.entry_price_usd) - 1) * 100 if pos.entry_price_usd else 0
                
                stop_price = pos.highest_price * (1 - pos.trailing_stop_pct) if pos.trailing_stop_active else pos.stop_loss_price
                
                positions.append({
                    "symbol": pos.symbol,
                    "entry_price": pos.entry_price_usd,
                    "current_price": current_price,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "stop_price": stop_price,
                    "status": "TRAILING" if pos.trailing_stop_active else "OPEN",
                })
            
            self.views["positions"].update_positions(positions)
            
        except Exception as e:
            self.log_message(f"UI refresh error: {e}", "error")
        
        # Balance/update in its own try/except so it ALWAYS runs
        try:
            positions_for_balance = []
            for addr, pos in self.bot.position_manager.positions.items():
                snap = self.bot.price_feed.get_latest(addr)
                current_price = snap.price_usd if snap else pos.entry_price_usd
                pnl = (current_price - pos.entry_price_usd) * pos.token_amount
                positions_for_balance.append({
                    "symbol": pos.symbol,
                    "entry_price": pos.entry_price_usd,
                    "pnl": pnl,
                })
            
            realized_pnl = self.bot.position_manager.get_realized_pnl()
            unrealized_pnl = sum(p["pnl"] for p in positions_for_balance)
            total_pnl = realized_pnl + unrealized_pnl
            balance = Config.INITIAL_CAPITAL + total_pnl
            
            win_rate = 0.0
            trade_count = len(self.bot.position_manager.trade_history)
            if trade_count > 0:
                wins = sum(1 for t in self.bot.position_manager.trade_history if t.pnl_usd > 0)
                win_rate = (wins / trade_count) * 100
            
            self.views["dashboard"].update_metrics(
                balance=balance,
                pnl=total_pnl,
                win_rate=win_rate,
                open_positions=len(self.bot.position_manager.positions),
            )
            
            allocations = [(p["symbol"], p["entry_price"] * 10, ACCENT) for p in positions_for_balance]
            if not allocations:
                allocations = [("Cash", Config.INITIAL_CAPITAL, TEXT_MID)]
            self.views["dashboard"].update_allocation(allocations)
            
        except Exception as e:
            self.log_message(f"Balance refresh error: {e}", "error")
    
    def log_message(self, message, level="info"):
        """Log a message to the UI."""
        self.log_panel.log(message, level)
    
    # ── Settings ────────────────────────────────────────────
    
    def set_live_mode(self, live):
        """Set live/paper mode."""
        self._live_mode = live
        Config.LIVE_MODE = live
        mode_str = "LIVE" if live else "PAPER"
        self.status_bar.set_mode(mode_str)
        self.sidebar.set_status(self._running, mode_str)
        self.log_message(f"Mode switched to {mode_str}", "warning" if live else "info")
    
    def apply_settings(self, settings):
        """Apply settings from UI."""
        mode = settings.get("mode", "PAPER")
        self.set_live_mode(mode == "LIVE")
        
        risk = settings.get("risk", {})
        try:
            Config.INITIAL_CAPITAL = float(risk.get("capital", 100))
            Config.STOP_LOSS_PCT = float(risk.get("stop_loss", 5)) / 100
            Config.TAKE_PROFIT_PCT = float(risk.get("take_profit", 15)) / 100
            Config.TRAILING_STOP_PCT = float(risk.get("trailing_stop", 3)) / 100
            Config.MAX_RISK_PER_TRADE = float(risk.get("max_positions", 3)) / 100
        except ValueError:
            self.log_message("Invalid risk parameter value", "error")
        
        self.log_message("Settings applied", "success")
    
    def _save_settings(self):
        """Save settings to disk."""
        settings_file = BASE_DIR / "ui_settings.json"
        try:
            settings = {
                "live_mode": self._live_mode,
                "mode": "LIVE" if self._live_mode else "PAPER",
            }
            with open(settings_file, "w") as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            self.log_message(f"Failed to save settings: {e}", "error")
    
    def _load_settings(self):
        """Load settings from disk."""
        settings_file = BASE_DIR / "ui_settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, "r") as f:
                    settings = json.load(f)
                if settings.get("live_mode"):
                    self.views["settings"].set_mode("live")
            except Exception as e:
                self.log_message(f"Failed to load settings: {e}", "error")


def main():
    """Run the trading bot UI."""
    app = TradingBotApp()
    app.mainloop()


if __name__ == "__main__":
    main()
