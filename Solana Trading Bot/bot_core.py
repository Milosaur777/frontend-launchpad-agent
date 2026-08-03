"""
Main trading bot orchestrator.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from config.settings import Config

# Simple file-based debug logger (same as app.py)
_base = Path(__file__).parent
_dbg_file = _base / "logs" / "debug_startup.log"


def _dbg(msg):
    try:
        _dbg_file.parent.mkdir(parents=True, exist_ok=True)
        with open(_dbg_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {msg}\n")
            f.flush()
    except Exception:
        pass


_dbg("bot_core.py imported OK")

from data.dexscreener import DexScreenerClient
from data.jupiter import JupiterClient
from data.price_feed import PriceFeed
from data.solana_rpc import SolanaRPCClient
from data.historical_loader import load_to_feed
from data.auto_fetch import fetch_all_watchlist
from execution.wallet import SolanaWallet
from execution.solana_trader import SolanaTrader
from execution.position_manager import PositionManager
from ml.features import FeatureEngineer
from ml.trainer import ModelTrainer
from ml.inference import InferenceEngine
from ml.token_scorer import TokenScorer
from ml.regime import RegimeDetector
from strategy.orchestrator import SignalOrchestrator
from risk.risk_manager import RiskManager, RiskCheck
from monitoring.alerts import AlertManager
from monitoring.logger import log
import traceback as _tb

_dbg("bot_core.py all imports done")


class TradingBot:
    """Memecoin trading bot main orchestrator."""

    def __init__(self):
        log.info("Initializing PolyCryptoAlpha Trading Bot...")

        # Data clients
        self.dexscreener = DexScreenerClient()
        self.jupiter = JupiterClient()
        self.rpc = SolanaRPCClient()

        # Wallet & execution
        self.wallet = SolanaWallet()

        # Price feed & ML
        self.price_feed = PriceFeed(dexscreener=self.dexscreener, jupiter=self.jupiter)
        self.trader = SolanaTrader(wallet=self.wallet, jupiter=self.jupiter, price_feed=self.price_feed)
        self.engineer = FeatureEngineer()
        self.trainer = ModelTrainer(engineer=self.engineer)
        self.token_scorer = TokenScorer()
        self.regime_detector = RegimeDetector()

        # Inference engine (lazy load)
        self.inference = InferenceEngine(model_dir=Config.MODELS_DIR, use_onnx=False)
        self.orchestrator = SignalOrchestrator(
            inference_engine=self.inference,
            feature_engineer=self.engineer,
            token_scorer=self.token_scorer,
        )

        # Risk & positions
        self.risk_manager = RiskManager()
        state_file = Config.DATA_DIR / "positions.json"
        self.position_manager = PositionManager(state_file=state_file)

        # Alerts
        self.alerts = AlertManager()

        # Bot state
        self.is_running = False
        self.cycle_count = 0
        self.last_retrain = datetime.min
        self._ui_queue = None  # Set by app.py to send trade notifications

        # Cooldown: don't re-buy tokens sold recently (token_address -> cycle when sold)
        self._sell_cooldown: Dict[str, int] = {}
        self._COOLDOWN_CYCLES = 30  # ~5 minutes at 10s cycles

        # Minimum hold: don't process sell signals or stop loss for N cycles after open
        self._MIN_HOLD_CYCLES = 10  # ~1.5 minutes at 10s cycles

        # In paper mode, clear stale positions and trade history from previous runs
        if not Config.LIVE_MODE:
            self.position_manager.positions.clear()
            self.position_manager.trade_history.clear()
            if self.position_manager.state_file:
                self.position_manager.save_state()

        log.info(f"Bot initialized. Mode: {'LIVE' if Config.LIVE_MODE else 'PAPER'}")
        log.info(f"Wallet: {self.wallet.public_key}")

    def _warm_from_csvs(self):
        """Load historical CSVs into price_feed for warm-start."""
        csv_dir = Config.HISTORICAL_DATA_DIR
        csvs_found = False

        if csv_dir.exists():
            csv_files = list(csv_dir.glob("*.csv"))
            if csv_files:
                csvs_found = True
                # Map CSV filenames to token addresses
                symbol_map = {s.lower(): a for s, a in Config.FIXED_WATCHLIST.items()}

                loaded = 0
                for csv_file in csv_files:
                    stem = csv_file.stem.lower()
                    # Try to match CSV to a known token
                    for symbol, address in symbol_map.items():
                        if symbol in stem:
                            try:
                                load_to_feed(address, symbol.upper(), csv_file, feed=self.price_feed)
                                count = len(self.price_feed.history.get(address, []))
                                log.info(f"  Loaded {symbol.upper()}: {count} bars from {csv_file.name}")
                                loaded += 1
                            except Exception as e:
                                log.warning(f"  Failed to load {csv_file.name}: {e}")
                            break

                if loaded > 0:
                    log.info(f"Warm-started with {loaded} CSV files")
                    return

        # No CSVs found - try auto-fetch if API key is configured
        dexploit_key = getattr(Config, "DEEXPLOIT_API_KEY", "")
        if dexploit_key:
            log.info("No CSVs found, attempting auto-fetch from Dexploit...")
            try:
                feed = fetch_all_watchlist(
                    resolution="5m",
                    hours=72,
                    api_key=dexploit_key,
                    feed=self.price_feed,
                )
                log.info(f"Auto-fetched data for {len(feed.history)} tokens")
            except Exception as e:
                log.warning(f"Auto-fetch failed: {e}")
        else:
            log.info("No CSVs found. Set DEEXPLOIT_API_KEY in .env to enable auto-fetch.")
            log.info("Get a free key at https://dexploit.dev/dashboard")

    async def run(self):
        """Main trading loop."""
        self.is_running = True
        log.info("Bot run() started — attempting ML model load...")

        # Load historical CSVs for warm-start
        self._warm_from_csvs()

        # Try to load existing ML model on startup
        try:
            loaded = self.inference.load()
            log.info(f"inference.load() returned: {loaded}, is_ready: {self.inference.is_ready}")
            if loaded:
                self.orchestrator.inference = self.inference
                log.info("Loaded existing ML model from disk")
            else:
                log.info("No ML model found on disk — will train when enough data accumulates")
        except Exception as e:
            import traceback
            log.error(f"ML model load FAILED with exception: {e}")
            log.error(f"Traceback:\n{traceback.format_exc()}")

        await self.alerts.send_alert(
            "Bot Started",
            f"Mode: {'LIVE' if Config.LIVE_MODE else 'PAPER'}\nWallet: {self.wallet.public_key}",
            level="INFO",
        )

        try:
            while self.is_running:
                cycle_start = datetime.now()
                self.cycle_count += 1

                try:
                    await self._trading_cycle()
                except Exception as e:
                    log.error(f"Error in trading cycle: {e}", exc_info=True)
                    await self.alerts.send_alert("Trading Cycle Error", str(e), level="ERROR")

                # Sleep until next cycle
                elapsed = (datetime.now() - cycle_start).total_seconds()
                sleep_time = max(0, 60 - elapsed)  # 1-minute cycles
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

        except asyncio.CancelledError:
            log.info("Bot cancelled")
        finally:
            await self.shutdown()

    async def _trading_cycle(self):
        """Execute one trading cycle."""
        _dbg(f"CYCLE {self.cycle_count} BEGIN")
        log.info(f"Starting trading cycle {self.cycle_count}")

        # 1. Update watchlist with trending tokens (every 10 cycles)
        if self.cycle_count % 10 == 1:
            await self._update_watchlist()

        # 2. Always update prices — even if risk check blocks trading
        updated = await self.price_feed.update_all()
        log.info(f"Updated prices for {len(updated)} tokens")

        # 3. Check risk limits
        risk_check = self.risk_manager.can_trade()
        if not risk_check.allowed:
            log.warning(f"Risk check blocked trading: {risk_check.reason}")
            return

        # 4. Check history depth
        for addr in list(self.price_feed._watchlist):
            history = self.price_feed.get_history(addr)
            _dbg(f"CYCLE {self.cycle_count} | {addr[:10]} | {len(history)} snapshots")

        # 5. Update positions (stop loss / take profit) — skip first cycle to avoid
        #    stale positions from disk being stopped out against current prices
        if self.cycle_count > 1:
            await self._update_positions()

        # 6. Periodic ML retraining
        await self._maybe_retrain()

        # 7. Generate signals
        signals = self.orchestrator.generate_signals(self.price_feed)

        # 7b. Scout mode: fill empty position slots with opportunistic buys
        has_buy_signals = any(s.action == "buy" for s in signals)
        n_positions = len(self.position_manager.positions)
        if not has_buy_signals and n_positions < 5:
            scout_signals = self.orchestrator.scout_buy(
                self.price_feed, n_positions=n_positions, max_positions=5,
                cooldowns=self._sell_cooldown, current_cycle=self.cycle_count,
                cooldown_cycles=self._COOLDOWN_CYCLES,
            )
            signals.extend(scout_signals)

        if signals:
            log.info(f"Generated {len(signals)} signals!")
            _dbg(f"CYCLE {self.cycle_count} | GENERATED {len(signals)} SIGNALS!")
            for sig in signals:
                msg = f"  {sig.action.upper()} {sig.symbol} | conf={sig.confidence:.2f} | reasons={sig.reasons}"
                log.info(msg)
                _dbg(f"CYCLE {self.cycle_count} | {msg}")
        else:
            _dbg(f"CYCLE {self.cycle_count} | NO SIGNALS")
            return

        # 8. Filter and execute signals
        for signal in signals:
            await self._process_signal(signal)

    async def _update_watchlist(self):
        """Update token watchlist based on configured mode."""
        try:
            if Config.WATCHLIST_MODE.lower() == "fixed":
                # Add Solana tokens
                for symbol, address in Config.FIXED_WATCHLIST.items():
                    self.price_feed.add_to_watchlist(address, chain="solana")

                # Robinhood Chain tokens - DexScreener does not support this chain yet
                # Adding them would crash the batch API call, so skip for now
                # TODO: Re-enable when DexScreener adds Robinhood chain support

                total = len(Config.FIXED_WATCHLIST)
                log.info(
                    f"Using fixed watchlist with {total} Solana tokens: "
                    f"{list(Config.FIXED_WATCHLIST.keys())}"
                )
                return

            # Discovery mode
            trending = await self.dexscreener.get_trending_tokens(
                chain="solana",
                min_liquidity=Config.MIN_LIQUIDITY_USD,
                min_volume_24h=Config.MIN_VOLUME_24H_USD,
                min_token_age_hours=Config.MIN_TOKEN_AGE_HOURS,
                max_token_age_hours=Config.MAX_TOKEN_AGE_HOURS,
                min_txns_24h=Config.MIN_TXNS_24H,
                min_buy_ratio=Config.MIN_BUY_RATIO,
                max_buy_ratio=Config.MAX_BUY_RATIO,
                top_n=20,
            )
            for pair in trending:
                self.price_feed.add_to_watchlist(pair.base_token_address)
            symbols = [p.base_token_symbol for p in trending]
            log.info(f"Updated watchlist with {len(trending)} established viral tokens: {symbols}")
        except Exception as e:
            log.warning(f"Failed to update watchlist: {e}")

    async def _update_positions(self):
        """Check stop loss / take profit for open positions."""
        for token_address in list(self.position_manager.positions.keys()):
            position = self.position_manager.positions.get(token_address)
            if not position:
                continue

            # Skip stop loss check for recently opened positions (minimum hold)
            cycles_held = self.cycle_count - getattr(position, '_open_cycle', 0)
            if cycles_held < self._MIN_HOLD_CYCLES:
                continue

            snapshots = self.price_feed.get_history(token_address)
            if not snapshots:
                continue

            current_price = snapshots[-1].price_usd
            closed_trade = self.position_manager.update_position_price(token_address, current_price)

            if closed_trade:
                self._sell_cooldown[token_address] = self.cycle_count
                self.risk_manager.record_trade_result(closed_trade.pnl_usd)
                self._notify_trade("sell", closed_trade.symbol, "sell",
                                   entry=closed_trade.entry_price,
                                   exit_price=closed_trade.exit_price,
                                   pnl=closed_trade.pnl_usd,
                                   reason=closed_trade.reason)
                log.info(
                    f"Position closed: {closed_trade.symbol} via {closed_trade.reason} "
                    f"PnL: ${closed_trade.pnl_usd:.2f} ({closed_trade.pnl_pct:+.2f}%)"
                )
                await self.alerts.send_alert(
                    f"Position Closed: {closed_trade.symbol}",
                    f"Reason: {closed_trade.reason}\n"
                    f"PnL: ${closed_trade.pnl_usd:.2f} ({closed_trade.pnl_pct:+.2f}%)",
                    level="INFO",
                )

    async def _maybe_retrain(self):
        """Retrain ML model periodically."""
        hours_since_retrain = (datetime.now() - self.last_retrain).total_seconds() / 3600
        if hours_since_retrain < Config.ML_RETRAIN_HOURS:
            return

        try:
            log.info(f"Retraining ML model... (last train {hours_since_retrain:.1f}h ago)")

            # Check how many snapshots we have per token
            token_counts = {t: len(s) for t, s in self.price_feed.history.items()}
            log.info(f"Token snapshot counts: {token_counts}")

            df = self.trainer.generate_training_data(
                self.price_feed.history,
                forward_bars=3,
            )

            if df is None:
                log.warning("ML training data generation returned None — "
                            "insufficient snapshots per token (need ~23+ rows per token after resampling)")
                return

            if len(df) < 100:
                log.warning(f"ML training dataset too small: {len(df)} rows (need 100+). "
                            f"Will retry after more data accumulates.")
                return

            self.trainer.train_final_model(df, model_dir=Config.MODELS_DIR)
            new_inference = InferenceEngine(model_dir=Config.MODELS_DIR, use_onnx=False)
            load_ok = new_inference.load()
            log.info(f"ML_RETRAIN: new InferenceEngine.load()={load_ok}, is_ready={new_inference.is_ready}")
            self.inference = new_inference
            self.orchestrator.inference = self.inference
            self.last_retrain = datetime.now()
            log.info(f"ML model retrained successfully — {len(df)} training rows")
        except Exception as e:
            import traceback
            log.error(f"ML retraining failed: {e}")
            log.error(f"Traceback:\n{traceback.format_exc()}")

    def _notify_trade(self, trade_type, symbol, action, entry=0, exit_price=0, pnl=0, reason=""):
        """Send trade notification to UI queue."""
        if self._ui_queue:
            try:
                self._ui_queue.put({
                    "type": "trade",
                    "trade": {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "symbol": symbol,
                        "action": action,
                        "entry": entry,
                        "exit": exit_price,
                        "pnl": pnl,
                        "reason": reason,
                    },
                })
            except Exception:
                pass

    async def _process_signal(self, signal):
        """Process a trading signal through risk management and execute."""
        _dbg(f"PROCESS: {signal.action.upper()} {signal.symbol} | conf={signal.confidence:.2f} | {signal.reasons}")

        # Skip if already in position
        if signal.action == "buy" and signal.token_address in self.position_manager.positions:
            _dbg(f"SKIP {signal.symbol}: already in position")
            return

        # Skip sell signals if no position
        if signal.action == "sell" and signal.token_address not in self.position_manager.positions:
            _dbg(f"SKIP {signal.symbol}: no position to sell")
            return

        # Get SOL price
        sol_price = await self.wallet.get_sol_price_usd()
        _dbg(f"SOL price: ${sol_price:.2f}")

        if signal.action == "buy":
            risk_check = self.risk_manager.calculate_position_size(
                confidence=signal.confidence,
                token_price=0.0,  # Not used for SOL sizing
                sol_price=sol_price,
                n_open_positions=len(self.position_manager.positions),
            )

            if not risk_check.allowed or risk_check.suggested_size is None:
                _dbg(f"RISK BLOCKED {signal.symbol}: {risk_check.reason}")
                return

            sol_amount = risk_check.suggested_size
            _dbg(f"EXECUTING BUY: {signal.symbol} | {sol_amount:.4f} SOL")

            result = await self.trader.buy_token(signal.token_address, sol_amount)

            if result.success:
                token_amount = sol_amount / max(result.price, 1e-9)
                pos = self.position_manager.open_position(
                    token_address=signal.token_address,
                    symbol=signal.symbol,
                    entry_price=result.price,
                    token_amount=token_amount,
                    sol_invested=sol_amount,
                    stop_loss_pct=Config.STOP_LOSS_PCT,
                    take_profit_pct=Config.TAKE_PROFIT_PCT,
                    trailing_stop_pct=Config.TRAILING_STOP_PCT,
                    trailing_stop_activation_pct=Config.TRAILING_STOP_ACTIVATION_PCT,
                )
                pos._open_cycle = self.cycle_count
                self._notify_trade("buy", signal.symbol, "buy",
                                   entry=result.price,
                                   reason=signal.reasons[0] if signal.reasons else "signal")
                await self.alerts.send_alert(
                    f"BUY Executed: {signal.symbol}",
                    f"Amount: {sol_amount:.4f} SOL\nPrice: ${result.price:.6f}",
                    level="INFO",
                )
            else:
                log.error(f"Buy failed for {signal.symbol}: {result.error}")

        elif signal.action == "sell":
            position = self.position_manager.get_position(signal.token_address)
            if not position:
                return

            # Skip sell signals during minimum hold period
            cycles_held = self.cycle_count - getattr(position, '_open_cycle', 0)
            if cycles_held < self._MIN_HOLD_CYCLES:
                _dbg(f"SKIP SELL {signal.symbol}: only held {cycles_held} cycles (min={self._MIN_HOLD_CYCLES})")
                return

            log.info(f"SELL signal: {signal.symbol} | conf={signal.confidence:.2f}")
            result = await self.trader.sell_token(signal.token_address, position.token_amount)

            if result.success:
                closed_trade = self.position_manager.close_position(
                    signal.token_address,
                    result.price,
                    reason="signal",
                )
                if closed_trade:
                    self._sell_cooldown[signal.token_address] = self.cycle_count
                    self.risk_manager.record_trade_result(closed_trade.pnl_usd)
                    self._notify_trade("sell", signal.symbol, "sell",
                                       entry=closed_trade.entry_price,
                                       exit_price=result.price,
                                       pnl=closed_trade.pnl_usd,
                                       reason="signal")
                    await self.alerts.send_alert(
                        f"SELL Executed: {signal.symbol}",
                        f"PnL: ${closed_trade.pnl_usd:.2f} ({closed_trade.pnl_pct:+.2f}%)",
                        level="INFO",
                    )
            else:
                log.error(f"Sell failed for {signal.symbol}: {result.error}")

    async def shutdown(self):
        """Graceful shutdown."""
        log.info("Shutting down bot...")
        self.is_running = False
        self.price_feed.save_cache()
        await self.alerts.send_alert("Bot Stopped", "Trading bot shutdown complete", level="INFO")
        await self.alerts.close()
        await self.jupiter.close()
        await self.dexscreener.close()
        await self.rpc.close()
        await self.wallet.close()
