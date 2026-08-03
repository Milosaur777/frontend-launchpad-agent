"""
Backtest from TradingView CSVs.

Place your CSV files in data/historical/ and run this script.

CSV format:
    Time,Open,High,Low,Close,Volume

    Where Time is ISO format (e.g., "2024-01-15 00:00")
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Config
from backtest.engine import BacktestEngine


# Map your CSVs here: {symbol: (token_address, filename)}
TOKEN_MAP = {
    "BONK": ("DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263", "bonk_5m.csv"),
    "WIF": ("EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm", "wif_5m.csv"),
    "POPCAT": ("7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr", "popcat_5m.csv"),
}


def main():
    print("=" * 60)
    print("Backtest from TradingView CSVs")
    print("=" * 60)

    engine = BacktestEngine(
        initial_capital=Config.BACKTEST_INITIAL_CAPITAL,
        fee_pct=Config.BACKTEST_FEE_PCT,
    )

    data_dir = Config.DATA_DIR / "historical"

    # Try to load CSVs, fall back to synthetic if not found
    tokens_found = any((data_dir / f).exists() for _, (_, f) in TOKEN_MAP.items())

    if tokens_found:
        print(f"\nLoading CSVs from {data_dir}...")
        feed = engine.load_from_csvs(TOKEN_MAP, data_dir)
    else:
        print(f"\nNo CSVs found in {data_dir}/")
        print("Using synthetic data instead.\n")
        print("To use real data, export from TradingView and place in:")
        print(f"  {data_dir}/")
        print("\nExpected files:")
        for symbol, (_, filename) in TOKEN_MAP.items():
            print(f"  - {filename} ({symbol})")
        print()

        feed = engine.load_synthetic_history(
            tokens={s: a for s, (a, _) in TOKEN_MAP.items()},
            n_bars=300,
        )

    result = engine.run(feed)
    engine.print_report(result)


if __name__ == "__main__":
    main()
