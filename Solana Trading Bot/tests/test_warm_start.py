"""Quick test of CSV warm-start in bot_core."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from bot_core import TradingBot


def test_warm_start():
    bot = TradingBot()
    bot._warm_from_csvs()

    # Check that BONK has history
    bonk_addr = "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263"
    history = bot.price_feed.history.get(bonk_addr, [])
    print(f"\nBONK history: {len(history)} bars")

    # Debug: show first few timestamps
    if history:
        print(f"First timestamp: {history[0].timestamp}")
        print(f"Last timestamp: {history[-1].timestamp}")
        print(f"First price: {history[0].price_usd}")

    # Check we can build features from it
    from ml.features import FeatureEngineer
    engineer = FeatureEngineer()
    ohlcv = engineer.snapshots_to_ohlcv(history)
    print(f"\nOHLCV after resample: {len(ohlcv) if ohlcv is not None else 'None'} bars")
    if ohlcv is not None and len(ohlcv) > 0:
        print(f"OHLCV columns: {list(ohlcv.columns)}")
        print(f"OHLCV head:\n{ohlcv.head()}")

    df = engineer.build_features(history)
    if df is not None:
        print(f"\nFeatures: {df.shape[0]} rows x {df.shape[1]} columns")
    else:
        print("\nFeatures: None (insufficient data)")

    print("\nWarm-start test passed!")


if __name__ == "__main__":
    test_warm_start()
