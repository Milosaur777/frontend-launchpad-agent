"""
Backtest engine test.
Run with: python tests/test_backtest.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest.engine import BacktestEngine


def test_backtest():
    print("\n[Backtest] Running quick backtest...")
    engine = BacktestEngine(initial_capital=100.0, fee_pct=0.002, timeframe_minutes=5)

    feed = engine.load_synthetic_history(
        tokens={
            "TEST1": "TestToken1111111111111111111111111111111111",
            "TEST2": "TestToken2222222222222222222222222222222222",
        },
        n_bars=200,
    )

    result = engine.run(feed)

    print(f"  [OK] Backtest completed")
    print(f"  - Total Return: {result.total_return_pct:+.2f}%")
    print(f"  - Total Trades: {result.total_trades}")
    print(f"  - Win Rate:     {result.win_rate:.1%}")
    print(f"  - Max Drawdown: {result.max_drawdown_pct:.2f}%")

    assert result.total_trades >= 0
    assert result.max_drawdown_pct >= 0
    print("  [OK] Backtest assertions passed")


if __name__ == "__main__":
    print("=" * 60)
    print("PolyCryptoAlpha Backtest Test")
    print("=" * 60)
    test_backtest()
    print("\n" + "=" * 60)
    print("Backtest test complete")
    print("=" * 60)
