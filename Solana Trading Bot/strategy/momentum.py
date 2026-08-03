"""
Momentum-based trading signal strategy.
"""

from typing import Dict, List
from dataclasses import dataclass

import numpy as np
import pandas as pd

from data.price_feed import PriceSnapshot
from ml.features import FeatureEngineer


@dataclass
class Signal:
    """Trading signal."""

    token_address: str
    symbol: str
    action: str  # "buy" or "sell"
    confidence: float
    reason: str


def _safe(row: pd.Series, key: str, default: float = 0.0) -> float:
    """Get a value from a Series, returning default if NaN or missing."""
    val = row.get(key, default)
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return default
    return val


class MomentumStrategy:
    """Generates momentum signals based on EMA crossovers and RSI."""

    def __init__(self, engineer: FeatureEngineer = None):
        self.engineer = engineer or FeatureEngineer()

    def generate_signals(
        self,
        snapshots: List[PriceSnapshot],
    ) -> List[Signal]:
        """Generate momentum signals for a list of snapshots."""
        if len(snapshots) < 10:
            return []

        df = self.engineer.build_features(snapshots)
        if df is None or len(df) < 3:
            return []

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        token_address = snapshots[-1].token_address
        symbol = snapshots[-1].symbol

        signals = []

        ema_ratio_now = _safe(latest, "ema_ratio_5", 1.0)
        ema_ratio_prev = _safe(prev, "ema_ratio_5", 1.0)
        rsi_now = _safe(latest, "rsi_14", 50.0)
        rsi_prev = _safe(prev, "rsi_14", 50.0)
        macd_now = _safe(latest, "macd_hist", 0.0)
        macd_prev = _safe(prev, "macd_hist", 0.0)

        # Buy: EMA9 crosses above EMA21, RSI not overbought
        ema9_cross = ema_ratio_now > 1.0 and ema_ratio_prev <= 1.0
        rsi_ok = rsi_now < 70
        macd_bullish = macd_now > 0

        if ema9_cross and rsi_ok and macd_bullish:
            signals.append(
                Signal(
                    token_address=token_address,
                    symbol=symbol,
                    action="buy",
                    confidence=0.65,
                    reason="EMA crossover + MACD bullish + RSI not overbought",
                )
            )

        # Standalone buy: Strong price momentum (up 5%+ over recent candles)
        recent_returns = [_safe(df.iloc[i], "returns", 0.0) for i in range(max(-5, -len(df)), 0)]
        cum_return = sum(recent_returns) if recent_returns else 0
        if cum_return > 0.05 and rsi_ok:
            signals.append(
                Signal(
                    token_address=token_address,
                    symbol=symbol,
                    action="buy",
                    confidence=min(0.50 + cum_return * 2, 0.80),
                    reason=f"Strong momentum: +{cum_return:.1%} over last {len(recent_returns)} candles",
                )
            )

        # Standalone buy: RSI oversold bounce (RSI recovering from below 35)
        if rsi_prev < 35 and rsi_now > rsi_prev and macd_bullish:
            signals.append(
                Signal(
                    token_address=token_address,
                    symbol=symbol,
                    action="buy",
                    confidence=0.55,
                    reason=f"RSI oversold bounce: {rsi_prev:.0f} -> {rsi_now:.0f}",
                )
            )

        # Standalone buy: MACD histogram increasing and positive
        if macd_now > 0 and macd_now > macd_prev and rsi_now < 65:
            signals.append(
                Signal(
                    token_address=token_address,
                    symbol=symbol,
                    action="buy",
                    confidence=0.50,
                    reason=f"MACD acceleration: {macd_prev:.4f} -> {macd_now:.4f}",
                )
            )

        # Sell: EMA9 crosses below EMA21 or RSI overbought
        ema9_cross_down = ema_ratio_now < 1.0 and ema_ratio_prev >= 1.0
        rsi_overbought = rsi_now > 75

        if ema9_cross_down or rsi_overbought:
            signals.append(
                Signal(
                    token_address=token_address,
                    symbol=symbol,
                    action="sell",
                    confidence=0.6,
                    reason="EMA cross down or RSI overbought",
                )
            )

        # Standalone sell: Strong downward momentum
        if cum_return < -0.05:
            signals.append(
                Signal(
                    token_address=token_address,
                    symbol=symbol,
                    action="sell",
                    confidence=0.55,
                    reason=f"Strong bearish momentum: {cum_return:.1%} over last {len(recent_returns)} candles",
                )
            )

        return signals
