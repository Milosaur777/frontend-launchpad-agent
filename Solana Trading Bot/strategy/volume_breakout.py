"""
Volume breakout trading signal strategy.
"""

from typing import List
from dataclasses import dataclass

from data.price_feed import PriceSnapshot
from ml.features import FeatureEngineer
from strategy.momentum import Signal, _safe


class VolumeBreakoutStrategy:
    """Generates signals based on volume spikes with price confirmation."""

    def __init__(self, engineer: FeatureEngineer = None):
        self.engineer = engineer or FeatureEngineer()

    def generate_signals(
        self,
        snapshots: List[PriceSnapshot],
    ) -> List[Signal]:
        """Generate volume breakout signals."""
        if len(snapshots) < 10:
            return []

        df = self.engineer.build_features(snapshots)
        if df is None or len(df) < 3:
            return []

        latest = df.iloc[-1]
        token_address = snapshots[-1].token_address
        symbol = snapshots[-1].symbol

        signals = []

        volume_ratio = _safe(latest, "volume_ratio_5", 1.0)
        price_change = _safe(latest, "returns", 0)
        liquidity = _safe(latest, "liquidity", 0)

        # Volume spike with positive price move
        if volume_ratio > 3.0 and price_change > 0.02 and liquidity > 10_000:
            signals.append(
                Signal(
                    token_address=token_address,
                    symbol=symbol,
                    action="buy",
                    confidence=min(0.5 + (volume_ratio - 3) * 0.05, 0.85),
                    reason=f"Volume breakout {volume_ratio:.1f}x with +{price_change:.2%} price move",
                )
            )

        # Volume spike with negative price move (distribution)
        if volume_ratio > 4.0 and price_change < -0.03:
            signals.append(
                Signal(
                    token_address=token_address,
                    symbol=symbol,
                    action="sell",
                    confidence=min(0.55 + abs(volume_ratio - 4) * 0.05, 0.8),
                    reason=f"Volume distribution {volume_ratio:.1f}x with {price_change:.2%} price drop",
                )
            )

        return signals
