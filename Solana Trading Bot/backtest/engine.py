"""
Backtest engine for PolyCryptoAlpha.

Replays historical (or synthetic) price snapshots through the signal
orchestrator and position manager to estimate strategy performance.
"""

import random
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

# Suppress noisy sklearn feature-name warnings during backtest
warnings.filterwarnings("ignore", category=UserWarning)

# Add project root to path when running backtest standalone
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import Config
from data.price_feed import PriceFeed, PriceSnapshot
from data.historical_loader import load_tradingview_csv, load_to_feed, load_multiple_csvs
from execution.position_manager import PositionManager, ClosedTrade
from execution.solana_trader import TradeResult
from ml.features import FeatureEngineer
from ml.inference import InferenceEngine
from ml.token_scorer import TokenScorer
from strategy.orchestrator import SignalOrchestrator


@dataclass
class BacktestResult:
    """Results of a backtest run."""

    initial_capital: float
    final_capital: float
    total_return_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win_pct: float
    avg_loss_pct: float
    profit_factor: float
    max_drawdown_pct: float
    sharpe_ratio: float
    trades: List[ClosedTrade]
    equity_curve: List[float]


class SyntheticDataGenerator:
    """Generate realistic synthetic price histories for backtesting."""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        np.random.seed(seed)

    def generate_token_history(
        self,
        token_address: str,
        symbol: str,
        n_bars: int = 500,
        timeframe_minutes: int = 5,
        start_price: float = 0.001,
        trend: float = 0.0,
        volatility: float = 0.03,
        liquidity_usd: float = 200_000.0,
        volume_24h_usd: float = 300_000.0,
        pair_created_at: Optional[datetime] = None,
    ) -> List[PriceSnapshot]:
        """
        Generate a synthetic snapshot history for one token.

        Args:
            token_address: Token mint address.
            symbol: Token symbol.
            n_bars: Number of 5m bars to generate.
            timeframe_minutes: Bar length in minutes.
            start_price: Initial price.
            trend: Drift per bar (e.g. 0.0005 = slow uptrend).
            volatility: Std dev of log returns.
            liquidity_usd: Constant liquidity for simplicity.
            volume_24h_usd: Constant 24h volume for simplicity.
            pair_created_at: Pair creation time.

        Returns:
            List of PriceSnapshot from oldest to newest.
        """
        snapshots = []
        price = start_price
        base_time = datetime.now() - timedelta(minutes=n_bars * timeframe_minutes)
        if pair_created_at is None:
            pair_created_at = base_time - timedelta(days=7)

        # Regime switching: random periods of momentum and reversal
        regime_changes = sorted(random.sample(range(n_bars // 10, n_bars - n_bars // 10), k=4))
        current_regime = "neutral"

        for i in range(n_bars):
            if regime_changes and i >= regime_changes[0]:
                regime_changes.pop(0)
                current_regime = random.choice(["momentum", "reversal", "neutral"])

            if current_regime == "momentum":
                # Autocorrelated returns
                drift = trend + random.gauss(0, volatility) * 0.5
                drift += 0.3 * (snapshots[-1].price_change_1h_pct / 100 if snapshots else 0)
            elif current_regime == "reversal":
                # Mean-reverting returns
                drift = -0.002 * (price / start_price - 1) + random.gauss(0, volatility)
            else:
                drift = trend + random.gauss(0, volatility)

            price = max(price * (1 + drift), 1e-9)

            # Derive 1h and 24h changes from recent history
            price_1h_ago = snapshots[-12].price_usd if len(snapshots) >= 12 else price
            price_24h_ago = snapshots[-288].price_usd if len(snapshots) >= 288 else price
            change_1h = (price / price_1h_ago - 1) * 100
            change_24h = (price / price_24h_ago - 1) * 100

            # Synthetic txns with some buy/sell imbalance
            txns_buy = int(random.gauss(800, 200))
            txns_sell = int(random.gauss(750, 200))
            txns_buy = max(txns_buy, 100)
            txns_sell = max(txns_sell, 100)

            snapshots.append(
                PriceSnapshot(
                    token_address=token_address,
                    symbol=symbol,
                    price_usd=price,
                    liquidity_usd=liquidity_usd + random.gauss(0, 5_000),
                    volume_24h_usd=volume_24h_usd + random.gauss(0, 20_000),
                    volume_1h_usd=volume_24h_usd / 24 + random.gauss(0, 2_000),
                    price_change_1h_pct=change_1h,
                    price_change_24h_pct=change_24h,
                    txns_24h_buy=txns_buy,
                    txns_24h_sell=txns_sell,
                    fdv=price * 1_000_000_000,
                    market_cap=price * 500_000_000,
                    timestamp=base_time + timedelta(minutes=i * timeframe_minutes),
                    source="backtest",
                    pair_created_at=pair_created_at,
                )
            )

        return snapshots


class BacktestEngine:
    """Replay price history through the trading pipeline."""

    def __init__(
        self,
        initial_capital: float = 100.0,
        fee_pct: float = 0.002,
        timeframe_minutes: Optional[int] = None,
    ):
        self.initial_capital = initial_capital
        self.fee_pct = fee_pct
        self.timeframe_minutes = timeframe_minutes or Config.TIMEFRAME_MINUTES.get(Config.TIMEFRAME, 5)
        self.engineer = FeatureEngineer(timeframe_minutes=timeframe_minutes)
        self.scorer = TokenScorer()
        self.inference = InferenceEngine(use_onnx=False)
        self.orchestrator = SignalOrchestrator(
            inference_engine=self.inference,
            feature_engineer=self.engineer,
            token_scorer=self.scorer,
        )
        self.position_manager = PositionManager()
        self.capital = initial_capital
        self.equity_curve: List[float] = []

    def load_synthetic_history(
        self,
        tokens: Dict[str, str],
        n_bars: int = 500,
    ) -> PriceFeed:
        """
        Generate and load synthetic price histories into a PriceFeed.

        Args:
            tokens: dict of {symbol: token_address}.
            n_bars: bars per token.

        Returns:
            PriceFeed populated with history.
        """
        generator = SyntheticDataGenerator()
        feed = PriceFeed()

        for symbol, address in tokens.items():
            history = generator.generate_token_history(
                token_address=address,
                symbol=symbol,
                n_bars=n_bars,
                timeframe_minutes=self.timeframe_minutes,
                start_price=random.uniform(0.0001, 0.01),
                trend=random.uniform(-0.0002, 0.0005),
                volatility=random.uniform(0.01, 0.05),
            )
            feed.history[address] = history
            feed.add_to_watchlist(address)

        return feed

    def load_from_csvs(
        self,
        token_map: dict,
        data_dir: str | Path,
    ) -> PriceFeed:
        """
        Load historical data from TradingView CSVs.

        Args:
            token_map: {symbol: (token_address, filename)} mapping.
            data_dir: Directory containing CSV files.

        Returns:
            PriceFeed populated with CSV history.
        """
        data_dir = Path(data_dir)
        feed = PriceFeed()

        for symbol, (address, filename) in token_map.items():
            csv_path = data_dir / filename
            if csv_path.exists():
                load_to_feed(address, symbol, csv_path, feed=feed)
                count = len(feed.history.get(address, []))
                print(f"  Loaded {symbol}: {count} bars from {filename}")
            else:
                print(f"  Skipped {symbol}: {csv_path} not found")

        return feed

    def _prepare_inference(self, feed: PriceFeed):
        """Train the ML ensemble on the synthetic history."""
        from ml.trainer import ModelTrainer

        trainer = ModelTrainer(engineer=self.engineer)
        df = trainer.generate_training_data(feed.history, forward_bars=3)
        if df is not None and len(df) > 100:
            # Train on temp dir so we don't overwrite production models
            temp_model_dir = Config.PROJECT_ROOT / "models" / "backtest_model"
            temp_model_dir.mkdir(parents=True, exist_ok=True)
            trainer.train_final_model(df, model_dir=temp_model_dir)
            self.inference = InferenceEngine(model_dir=temp_model_dir, use_onnx=False)
            self.inference.load()
            self.orchestrator.inference = self.inference

    def run(self, feed: PriceFeed) -> BacktestResult:
        """
        Run the backtest.

        The feed must already contain full histories per token. The engine
        walks forward one bar at a time, only revealing data up to that point
        to the signal generator.
        """
        # Prepare ML model on full history (fair for offline backtest)
        self._prepare_inference(feed)

        # Determine common bar indices
        min_bars = min(len(h) for h in feed.history.values())
        if min_bars < 100:
            raise ValueError("Need at least 100 bars per token for backtest")

        # Walk forward
        for bar_idx in range(100, min_bars):
            # Build a restricted feed: only history up to current bar
            restricted_feed = PriceFeed()
            for addr in feed._watchlist:
                restricted_feed.history[addr] = feed.history[addr][: bar_idx + 1]
                restricted_feed.add_to_watchlist(addr)

            # Update positions (stop loss / take profit / trailing stop)
            for addr in list(self.position_manager.positions.keys()):
                current_price = restricted_feed.get_latest(addr).price_usd
                closed = self.position_manager.update_position_price(addr, current_price)
                if closed:
                    self._record_trade(closed)

            # Generate signals
            signals = self.orchestrator.generate_signals(restricted_feed)

            for signal in signals:
                latest = restricted_feed.get_latest(signal.token_address)
                if not latest:
                    continue

                if signal.action == "buy":
                    self._execute_buy(signal, latest)
                elif signal.action == "sell":
                    self._execute_sell(signal, latest)

            # Record equity
            self._update_equity(restricted_feed)

        # Close any open positions at the final price
        for addr in list(self.position_manager.positions.keys()):
            final_price = feed.get_latest(addr).price_usd
            closed = self.position_manager.close_position(addr, final_price, reason="backtest_end")
            if closed:
                self._record_trade(closed)

        return self._build_result()

    def _execute_buy(self, signal, latest: PriceSnapshot):
        """Execute a simulated buy."""
        if signal.token_address in self.position_manager.positions:
            return

        # Simple fixed position sizing: 20% of current capital per trade
        position_size_usd = self.capital * Config.MAX_RISK_PER_TRADE
        token_amount = position_size_usd / max(latest.price_usd, 1e-9)
        fee = position_size_usd * self.fee_pct

        if self.capital < position_size_usd + fee:
            return

        self.capital -= fee
        self.position_manager.open_position(
            token_address=signal.token_address,
            symbol=signal.symbol,
            entry_price=latest.price_usd,
            token_amount=token_amount,
            sol_invested=position_size_usd / 150.0,  # Approx SOL price
            stop_loss_pct=Config.STOP_LOSS_PCT,
            take_profit_pct=Config.TAKE_PROFIT_PCT,
            trailing_stop_pct=Config.TRAILING_STOP_PCT,
            trailing_stop_activation_pct=Config.TRAILING_STOP_ACTIVATION_PCT,
        )

    def _execute_sell(self, signal, latest: PriceSnapshot):
        """Execute a simulated sell."""
        position = self.position_manager.get_position(signal.token_address)
        if not position:
            return

        closed = self.position_manager.close_position(
            signal.token_address,
            latest.price_usd,
            reason="signal",
        )
        if closed:
            self._record_trade(closed)

    def _record_trade(self, trade: ClosedTrade):
        """Record a closed trade and update capital."""
        self.capital += trade.pnl_usd

    def _update_equity(self, feed: PriceFeed):
        """Update equity curve with realized + unrealized PnL."""
        unrealized = 0.0
        for addr, position in self.position_manager.positions.items():
            latest = feed.get_latest(addr)
            if latest:
                unrealized += (latest.price_usd - position.entry_price_usd) * position.token_amount
        self.equity_curve.append(self.capital + unrealized)

    def _build_result(self) -> BacktestResult:
        """Compile backtest statistics."""
        trades = self.position_manager.trade_history
        wins = [t for t in trades if t.pnl_usd > 0]
        losses = [t for t in trades if t.pnl_usd <= 0]

        win_rate = len(wins) / len(trades) if trades else 0.0
        avg_win = sum(t.pnl_pct for t in wins) / len(wins) if wins else 0.0
        avg_loss = sum(t.pnl_pct for t in losses) / len(losses) if losses else 0.0

        gross_profit = sum(t.pnl_usd for t in wins)
        gross_loss = abs(sum(t.pnl_usd for t in losses))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")

        # Max drawdown
        peak = self.initial_capital
        max_dd = 0.0
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd

        # Sharpe-ish: mean daily return / std dev (assuming ~288 5m bars/day)
        daily_returns = []
        bars_per_day = 288
        for i in range(bars_per_day, len(self.equity_curve), bars_per_day):
            ret = (self.equity_curve[i] - self.equity_curve[i - bars_per_day]) / self.equity_curve[i - bars_per_day]
            daily_returns.append(ret)
        sharpe = 0.0
        if len(daily_returns) > 1 and np.std(daily_returns) > 0:
            sharpe = (np.mean(daily_returns) / np.std(daily_returns)) * np.sqrt(365)

        return BacktestResult(
            initial_capital=self.initial_capital,
            final_capital=self.capital,
            total_return_pct=(self.capital / self.initial_capital - 1) * 100,
            total_trades=len(trades),
            winning_trades=len(wins),
            losing_trades=len(losses),
            win_rate=win_rate,
            avg_win_pct=avg_win,
            avg_loss_pct=avg_loss,
            profit_factor=profit_factor,
            max_drawdown_pct=max_dd * 100,
            sharpe_ratio=sharpe,
            trades=trades,
            equity_curve=self.equity_curve,
        )

    def print_report(self, result: BacktestResult):
        """Print a human-readable backtest report."""
        print("\n" + "=" * 60)
        print("BACKTEST REPORT")
        print("=" * 60)
        print(f"Initial Capital:    ${result.initial_capital:,.2f}")
        print(f"Final Capital:      ${result.final_capital:,.2f}")
        print(f"Total Return:       {result.total_return_pct:+.2f}%")
        print(f"Total Trades:       {result.total_trades}")
        print(f"Winning Trades:     {result.winning_trades}")
        print(f"Losing Trades:      {result.losing_trades}")
        print(f"Win Rate:           {result.win_rate:.1%}")
        print(f"Avg Win:            {result.avg_win_pct:+.2f}%")
        print(f"Avg Loss:           {result.avg_loss_pct:+.2f}%")
        print(f"Profit Factor:      {result.profit_factor:.2f}")
        print(f"Max Drawdown:       {result.max_drawdown_pct:.2f}%")
        print(f"Sharpe Ratio:       {result.sharpe_ratio:.2f}")
        print("=" * 60)

        if result.trades:
            print("\nRecent trades:")
            for t in result.trades[-5:]:
                print(
                    f"  {t.symbol:8} {t.reason:12} PnL: ${t.pnl_usd:+7.2f} ({t.pnl_pct:+6.2f}%)"
                )
            print("=" * 60)


def run_default_backtest():
    """Run a default backtest with curated tokens."""
    engine = BacktestEngine(
        initial_capital=Config.BACKTEST_INITIAL_CAPITAL,
        fee_pct=Config.BACKTEST_FEE_PCT,
    )

    feed = engine.load_synthetic_history(
        tokens={
            "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
            "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
            "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
        },
        n_bars=300,
    )

    result = engine.run(feed)
    engine.print_report(result)
    return result


if __name__ == "__main__":
    run_default_backtest()
