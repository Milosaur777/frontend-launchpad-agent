"""
Feature engineering pipeline for memecoin trading ML.
Converts price snapshots into model-ready features.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings

import numpy as np
import pandas as pd

from data.price_feed import PriceSnapshot
from config.settings import Config


@dataclass
class FeatureVector:
    """A single feature vector for one token at one point in time."""

    token_address: str
    symbol: str
    timestamp: datetime
    features: pd.Series
    target: Optional[float] = None


class FeatureEngineer:
    """Build ML features from price snapshot history."""

    def __init__(self, timeframe_minutes: Optional[int] = None):
        self.timeframe_minutes = timeframe_minutes or Config.TIMEFRAME_MINUTES.get(
            Config.TIMEFRAME, 5
        )

    def snapshots_to_ohlcv(
        self,
        snapshots: List[PriceSnapshot],
    ) -> Optional[pd.DataFrame]:
        """
        Convert raw price snapshots into OHLCV bars.

        Since free APIs don't provide historical OHLCV, we aggregate
        our own snapshots into time bars.
        """
        if len(snapshots) < 10:
            return None

        df = pd.DataFrame([
            {
                "timestamp": s.timestamp,
                "open": s.price_usd,
                "high": s.price_usd,
                "low": s.price_usd,
                "close": s.price_usd,
                "volume": s.volume_1h_usd / max(s.price_usd, 1e-9),
                "liquidity": s.liquidity_usd,
                "txns_buy": s.txns_24h_buy,
                "txns_sell": s.txns_24h_sell,
                "fdv": s.fdv,
                "market_cap": s.market_cap,
            }
            for s in snapshots
        ])

        df.set_index("timestamp", inplace=True)
        # Ensure index is a proper DatetimeIndex (may be plain Index if timestamps are strings)
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index, utc=True)
        # Normalize all timestamps to naive (strip timezone info) to avoid
        # mixing offset-aware and offset-naive datetimes
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        df.sort_index(inplace=True)

        # Resample to timeframe
        agg_dict = {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "liquidity": "last",
            "txns_buy": "last",
            "txns_sell": "last",
            "fdv": "last",
            "market_cap": "last",
        }

        ohlcv = df.resample(f"{self.timeframe_minutes}min").agg(agg_dict)
        ohlcv.dropna(subset=["close"], inplace=True)

        return ohlcv

    def compute_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute technical indicator features."""
        df = df.copy()

        # Returns
        df["returns"] = df["close"].pct_change()
        df["log_returns"] = np.log(df["close"] / df["close"].shift(1))

        # Moving averages and ratios
        for window in [5, 10, 20]:
            df[f"ma_{window}"] = df["close"].rolling(window).mean()
            df[f"ma_ratio_{window}"] = df["close"] / df[f"ma_{window}"]
            df[f"ema_{window}"] = df["close"].ewm(span=window, adjust=False).mean()
            df[f"ema_ratio_{window}"] = df["close"] / df[f"ema_{window}"]

        # Volatility
        df["volatility_5"] = df["returns"].rolling(5).std()
        df["volatility_20"] = df["returns"].rolling(20).std()

        # RSI
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss.replace(0, np.nan)
        df["rsi_14"] = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = df["close"].ewm(span=12, adjust=False).mean()
        ema_26 = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = ema_12 - ema_26
        df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["macd_signal"]

        # Bollinger Bands
        df["bb_middle"] = df["close"].rolling(20).mean()
        df["bb_std"] = df["close"].rolling(20).std()
        df["bb_upper"] = df["bb_middle"] + 2 * df["bb_std"]
        df["bb_lower"] = df["bb_middle"] - 2 * df["bb_std"]
        df["bb_position"] = (df["close"] - df["bb_lower"]) / (
            df["bb_upper"] - df["bb_lower"]
        ).replace(0, np.nan)

        # ATR (Average True Range)
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift(1))
        low_close = np.abs(df["low"] - df["close"].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df["atr_14"] = tr.rolling(14).mean()
        df["atr_pct"] = df["atr_14"] / df["close"]

        return df

    def compute_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute volume-based features."""
        df = df.copy()

        df["volume_ma_5"] = df["volume"].rolling(5).mean()
        df["volume_ratio_5"] = df["volume"] / df["volume_ma_5"].replace(0, np.nan)
        df["volume_ma_20"] = df["volume"].rolling(20).mean()
        df["volume_ratio_20"] = df["volume"] / df["volume_ma_20"].replace(0, np.nan)

        # Volume trend
        df["volume_change"] = df["volume"].pct_change()

        # VWAP deviation
        typical_price = (df["high"] + df["low"] + df["close"]) / 3
        vwap = (typical_price * df["volume"]).cumsum() / df["volume"].cumsum()
        df["vwap_deviation"] = (df["close"] - vwap) / vwap.replace(0, np.nan)

        # Buy/sell pressure
        df["buy_sell_ratio"] = df["txns_buy"] / (
            df["txns_sell"].replace(0, np.nan)
        )

        return df

    def compute_liquidity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute liquidity and market structure features."""
        df = df.copy()

        df["liquidity_change"] = df["liquidity"].pct_change()
        df["liquidity_ratio"] = df["liquidity"] / df["market_cap"].replace(0, np.nan)

        # Market cap changes
        df["mc_change"] = df["market_cap"].pct_change()
        df["fdv_mc_ratio"] = df["fdv"] / df["market_cap"].replace(0, np.nan)

        # Price ranges
        df["high_low_range"] = (df["high"] - df["low"]) / df["close"]

        return df

    def build_features(
        self,
        snapshots: List[PriceSnapshot],
    ) -> Optional[pd.DataFrame]:
        """
        Build complete feature dataframe from snapshots.

        Returns:
            DataFrame with features, or None if insufficient data.
        """
        ohlcv = self.snapshots_to_ohlcv(snapshots)
        if ohlcv is None or len(ohlcv) < 10:
            return None

        df = self.compute_technical_features(ohlcv)
        df = self.compute_volume_features(df)
        df = self.compute_liquidity_features(df)

        # Drop rows with too many NaNs
        feature_cols = [c for c in df.columns if c not in ["open", "high", "low", "close", "volume"]]
        df = df.dropna(subset=feature_cols, how="all")

        return df

    def get_latest_feature_vector(
        self,
        snapshots: List[PriceSnapshot],
    ) -> Optional[pd.Series]:
        """Get the latest feature vector for live inference."""
        df = self.build_features(snapshots)
        if df is None or len(df) == 0:
            return None
        return df.iloc[-1]

    def create_training_dataset(
        self,
        snapshot_history: Dict[str, List[PriceSnapshot]],
        forward_bars: int = 3,
    ) -> Optional[pd.DataFrame]:
        """
        Create a training dataset across multiple tokens.

        Args:
            snapshot_history: Dict mapping token_address -> list of snapshots.
            forward_bars: Number of bars ahead to predict return direction.

        Returns:
            DataFrame with features and binary target (1 = up, 0 = down/flat).
        """
        all_rows = []

        for token_address, snapshots in snapshot_history.items():
            df = self.build_features(snapshots)
            if df is None or len(df) < forward_bars + 10:
                continue

            if not snapshots:
                continue

            symbol = snapshots[0].symbol

            # Future return direction
            future_return = df["close"].shift(-forward_bars) / df["close"] - 1
            df["target"] = (future_return > 0).astype(int)

            # Add metadata
            df["token_address"] = token_address
            df["symbol"] = symbol

            all_rows.append(df)

        if not all_rows:
            return None

        combined = pd.concat(all_rows, ignore_index=True)
        return combined
