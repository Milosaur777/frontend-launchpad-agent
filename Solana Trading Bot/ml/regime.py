"""
Market regime detection using Gaussian Mixture Model.
Identifies trending, ranging, and volatile market regimes.
"""

from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from config.settings import Config


class Regime(Enum):
    """Market regime classifications."""

    TRENDING = "trending"
    RANGING = "ranging"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


@dataclass
class RegimeResult:
    """Result of regime detection."""

    regime: Regime
    probability: float
    all_probabilities: dict


class RegimeDetector:
    """
    Detects market regimes using Gaussian Mixture Model on returns/volatility.

    We use GMM instead of HMM because it has fewer dependencies and is
    sufficient for filtering trades by volatility regime.
    """

    def __init__(self, n_components: int = 3, lookback_bars: int = 50):
        self.n_components = n_components
        self.lookback_bars = lookback_bars
        self.model: Optional[GaussianMixture] = None
        self._fitted = False

    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Prepare returns and volatility features."""
        returns = df["returns"].fillna(0).values
        volatility = df["returns"].rolling(10).std().fillna(0).values

        # Add trend feature (price vs moving average)
        ma_ratio = df.get("ma_ratio_20", pd.Series(1.0, index=df.index)).fillna(1.0).values

        features = np.column_stack([returns, volatility, ma_ratio])
        return features

    def fit(self, df: pd.DataFrame) -> "RegimeDetector":
        """Fit the regime detector on historical data."""
        features = self._prepare_features(df)
        if len(features) < self.lookback_bars:
            return self

        # Use recent history
        recent = features[-self.lookback_bars:]

        self.model = GaussianMixture(
            n_components=self.n_components,
            random_state=42,
            covariance_type="full",
            max_iter=200,
        )
        self.model.fit(recent)
        self._fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> RegimeResult:
        """
        Predict current regime.

        Returns:
            RegimeResult with regime classification and probabilities.
        """
        if not self._fitted or self.model is None:
            # Fallback: simple rule-based regime detection
            return self._rule_based_regime(df)

        features = self._prepare_features(df)
        latest = features[-1:]

        probs = self.model.predict_proba(latest)[0]
        component = int(self.model.predict(latest)[0])
        probability = float(probs[component])

        # Map components to regimes based on characteristics
        regime = self._component_to_regime(component, df)

        all_probs = {
            Regime.TRENDING.value: 0.0,
            Regime.RANGING.value: 0.0,
            Regime.VOLATILE.value: 0.0,
        }

        return RegimeResult(
            regime=regime,
            probability=probability,
            all_probabilities=all_probs,
        )

    def _component_to_regime(self, component: int, df: pd.DataFrame) -> Regime:
        """Map GMM component to human-readable regime."""
        if not self._fitted or self.model is None:
            return Regime.UNKNOWN

        # Get means for each component
        means = self.model.means_

        # Sort components by volatility (second feature)
        volatilities = means[:, 1]
        sorted_idx = np.argsort(volatilities)

        # Low vol = ranging, high vol = volatile, medium vol = trending
        component_rank = list(sorted_idx).index(component)

        if component_rank == self.n_components - 1:
            return Regime.VOLATILE
        elif component_rank == 0:
            return Regime.RANGING
        else:
            # Check if trending by price vs MA
            if "ma_ratio_20" in df.columns and len(df) > 0:
                ma_ratio = df["ma_ratio_20"].iloc[-1]
                if abs(ma_ratio - 1.0) > 0.02:
                    return Regime.TRENDING
            return Regime.RANGING

    def _rule_based_regime(self, df: pd.DataFrame) -> RegimeResult:
        """Fallback rule-based regime detection."""
        if len(df) < 10:
            return RegimeResult(Regime.UNKNOWN, 0.0, {})

        returns = df["returns"].fillna(0)
        volatility = returns.rolling(10).std().iloc[-1]
        trend = abs(df["close"].iloc[-1] / df["close"].iloc[-10] - 1)

        if volatility > 0.05 or trend > 0.1:
            regime = Regime.VOLATILE
            prob = 0.6
        elif trend > 0.03:
            regime = Regime.TRENDING
            prob = 0.6
        else:
            regime = Regime.RANGING
            prob = 0.6

        return RegimeResult(
            regime=regime,
            probability=prob,
            all_probabilities={
                Regime.TRENDING.value: 0.33,
                Regime.RANGING.value: 0.33,
                Regime.VOLATILE.value: 0.34,
            },
        )

    def is_tradable(self, regime_result: RegimeResult) -> bool:
        """
        Determine if current regime is favorable for trading.

        For memecoin momentum strategy, we want to avoid extreme volatility
        and ranging markets. Trending or moderate volatile regimes are OK.
        """
        return regime_result.regime in (Regime.TRENDING, Regime.VOLATILE)
