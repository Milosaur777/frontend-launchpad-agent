"""
Signal orchestrator: combines momentum, volume, and ML signals.
"""

from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

import pandas as pd

_base_o = Path(__file__).parent
_dbg_file_o = _base_o / "logs" / "debug_startup.log"


def _dbg(msg):
    try:
        _dbg_file_o.parent.mkdir(parents=True, exist_ok=True)
        with open(_dbg_file_o, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {msg}\n")
            f.flush()
    except Exception:
        pass


from config.settings import Config
from data.price_feed import PriceSnapshot, PriceFeed
from ml.features import FeatureEngineer
from ml.inference import InferenceEngine
from ml.token_scorer import TokenScorer
from strategy.momentum import MomentumStrategy, Signal
from strategy.volume_breakout import VolumeBreakoutStrategy

log = logging.getLogger(__name__)


@dataclass
class TradingSignal:
    """Final consolidated trading signal."""

    token_address: str
    symbol: str
    action: str
    confidence: float
    sol_amount: float
    reasons: List[str]
    ml_probability: Optional[float] = None


class SignalOrchestrator:
    """Combines multiple signal sources into actionable trading signals."""

    def __init__(
        self,
        inference_engine: Optional[InferenceEngine] = None,
        feature_engineer: Optional[FeatureEngineer] = None,
        token_scorer: Optional[TokenScorer] = None,
    ):
        self.inference = inference_engine
        self.engineer = feature_engineer or FeatureEngineer()
        self.scorer = token_scorer or TokenScorer()
        self.momentum = MomentumStrategy(engineer=self.engineer)
        self.volume = VolumeBreakoutStrategy(engineer=self.engineer)

    def generate_signals(
        self,
        price_feed: PriceFeed,
    ) -> List[TradingSignal]:
        """
        Generate consolidated trading signals from all sources.

        Args:
            price_feed: PriceFeed with snapshot history.

        Returns:
            List of final trading signals.
        """
        signals: Dict[str, List[Signal]] = {}

        # Generate raw signals for each watched token
        for token_address in price_feed._watchlist:
            snapshots = price_feed.get_history(token_address, max_age_minutes=120)
            if len(snapshots) < 10:
                _dbg(f"SKIP {token_address[:12]}: only {len(snapshots)} snapshots (need 10)")
                continue

            # Risk filter: skip unsafe tokens
            latest = snapshots[-1]
            risk = self.scorer.score(latest)
            if not risk.is_safe:
                _dbg(f"SKIP {latest.symbol}: risk_score={risk.total_score}, reasons={risk.reasons}")
                continue

            token_signals = []
            token_signals.extend(self.momentum.generate_signals(snapshots))
            token_signals.extend(self.volume.generate_signals(snapshots))

            # Add ML signal if inference engine is ready
            if self.inference and self.inference.is_ready:
                features = self.engineer.get_latest_feature_vector(snapshots)
                if features is not None:
                    pred = self.inference.predict(features)
                    if pred:
                        _dbg(f"  {latest.symbol} ML pred: direction={pred.direction}, "
                             f"conf={pred.confidence:.3f}, prob_up={pred.probability_up:.3f}")
                        if pred.confidence >= Config.MIN_CONFIDENCE:
                            action = "buy" if pred.direction == 1 else "sell"
                            token_signals.append(
                                Signal(
                                    token_address=token_address,
                                    symbol=latest.symbol,
                                    action=action,
                                    confidence=pred.confidence,
                                    reason=f"ML ensemble (LGBM:{pred.model_votes.get('lightgbm', 0):.2f}, XGB:{pred.model_votes.get('xgboost', 0):.2f})",
                                )
                            )
                    else:
                        _dbg(f"  {latest.symbol} ML pred returned None")

            if token_signals:
                _dbg(f"  {latest.symbol}: {len(token_signals)} raw signals "
                     f"({[s.action for s in token_signals]})")
                signals[token_address] = token_signals

        # Consolidate signals per token
        consolidated = []
        for token_address, token_signals in signals.items():
            buy_signals = [s for s in token_signals if s.action == "buy"]
            sell_signals = [s for s in token_signals if s.action == "sell"]

            if buy_signals and not sell_signals:
                signal = self._consolidate(token_address, "buy", buy_signals, price_feed)
                if signal:
                    consolidated.append(signal)
            elif sell_signals and not buy_signals:
                signal = self._consolidate(token_address, "sell", sell_signals, price_feed)
                if signal:
                    consolidated.append(signal)
            elif buy_signals and sell_signals:
                if len(buy_signals) > len(sell_signals):
                    signal = self._consolidate(token_address, "buy", buy_signals, price_feed)
                    if signal:
                        consolidated.append(signal)
                elif len(sell_signals) > len(buy_signals):
                    signal = self._consolidate(token_address, "sell", sell_signals, price_feed)
                    if signal:
                        consolidated.append(signal)

        return consolidated

    def scout_buy(
        self,
        price_feed: PriceFeed,
        n_positions: int = 0,
        max_positions: int = 5,
        cooldowns: Optional[Dict[str, int]] = None,
        current_cycle: int = 0,
        cooldown_cycles: int = 30,
    ) -> List[TradingSignal]:
        """
        Scout mode: when positions are sparse, find multiple tokens to buy
        based on simple positive price momentum.
        """
        if n_positions >= max_positions:
            return []

        candidates = []
        if cooldowns is None:
            cooldowns = {}

        for token_address in price_feed._watchlist:
            # Skip tokens in cooldown (recently sold)
            last_sold = cooldowns.get(token_address, -999)
            if current_cycle - last_sold < cooldown_cycles:
                continue

            snapshots = price_feed.get_history(token_address, max_age_minutes=120)
            if len(snapshots) < 3:
                continue

            latest = snapshots[-1]
            risk = self.scorer.score(latest)
            if not risk.is_safe:
                continue

            # Use only the most recent snapshots (max 10)
            recent = snapshots[-10:]
            prices = [s.price_usd for s in recent]
            if prices[-1] <= 0 or prices[0] <= 0:
                continue

            pct_change = (prices[-1] - prices[0]) / prices[0]
            volumes = [s.volume_1h_usd for s in recent[-5:]]
            avg_vol = sum(volumes) / len(volumes) if volumes else 0

            score = 0
            if pct_change > 0:
                score += min(pct_change * 10, 3.0)
            else:
                # Penalize negative momentum — scout should only buy uptrending
                score -= min(abs(pct_change) * 5, 2.0)
            if latest.liquidity_usd > 10_000:
                score += 1.0
            if avg_vol > 5_000:
                score += 0.5
            # Scout mode: lenient risk — allow up to 50 (normal threshold is 35)
            if risk.total_score < 50:
                score += 1.0

            # Bonus for positive recent momentum
            if len(prices) >= 3:
                last_3_change = (prices[-1] - prices[-3]) / prices[-3] if prices[-3] > 0 else 0
                if last_3_change > 0:
                    score += 0.5

            # Require minimum score of 2.5 to avoid buying flat tokens
            if score > 2.5:
                candidates.append((token_address, latest, pct_change, score))

        # Sort by score descending, take best N
        candidates.sort(key=lambda x: x[3], reverse=True)
        slots = max_positions - n_positions
        signals = []

        for token_address, latest, pct_change, score in candidates[:slots]:
            signals.append(TradingSignal(
                token_address=token_address,
                symbol=latest.symbol,
                action="buy",
                confidence=min(0.40 + score * 0.05, 0.70),
                sol_amount=0.0,
                reasons=[f"Scout: +{pct_change:.1%} momentum, score={score:.1f}"],
                ml_probability=None,
            ))

        if signals:
            _dbg(f"SCOUT: {len(signals)} buys from {len(candidates)} candidates")

        return signals

    def _consolidate(
        self,
        token_address: str,
        action: str,
        signals: List[Signal],
        price_feed: PriceFeed,
    ) -> Optional[TradingSignal]:
        """Consolidate multiple signals for one token into one action."""
        latest = price_feed.get_latest(token_address)
        if not latest:
            return None

        avg_confidence = sum(s.confidence for s in signals) / len(signals)
        reasons = [s.reason for s in signals]

        # Find ML probability if present
        ml_prob = None
        for s in signals:
            if "ML ensemble" in s.reason:
                ml_prob = s.confidence
                break

        return TradingSignal(
            token_address=token_address,
            symbol=latest.symbol,
            action=action,
            confidence=min(avg_confidence, 0.99),
            sol_amount=0.0,  # To be filled by risk manager
            reasons=reasons,
            ml_probability=ml_prob,
        )
