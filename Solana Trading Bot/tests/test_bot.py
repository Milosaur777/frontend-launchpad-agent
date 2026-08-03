"""
End-to-end bot test: runs one trading cycle in paper mode.
"""

import os
import sys
import asyncio
import base58
from pathlib import Path
from datetime import datetime, timedelta

# Generate a test keypair BEFORE importing config
sys.path.insert(0, str(Path(__file__).parent.parent))

from solders.keypair import Keypair

test_keypair = Keypair()
test_private_key = base58.b58encode(bytes(test_keypair)).decode("utf-8")

os.environ["SOLANA_PRIVATE_KEY"] = test_private_key
os.environ["LIVE_MODE"] = "false"
os.environ["INITIAL_CAPITAL"] = "100"
os.environ["MAX_RISK_PER_TRADE"] = "0.20"
os.environ["MAX_DAILY_LOSS"] = "0.10"
os.environ["MAX_DRAWDOWN"] = "0.30"
os.environ["STOP_LOSS_PCT"] = "0.05"
os.environ["TAKE_PROFIT_PCT"] = "0.10"
os.environ["MIN_CONFIDENCE"] = "0.60"

from bot_core import TradingBot
from data.price_feed import PriceSnapshot


def generate_snapshots_for_token(
    token_address: str,
    symbol: str,
    n: int = 100,
    base_price: float = 0.001,
) -> list:
    """Generate synthetic snapshots with momentum."""
    import random

    snapshots = []
    price = base_price
    base_time = datetime.now() - timedelta(minutes=n * 5)

    for i in range(n):
        change = random.gauss(0.002, 0.015)
        price = price * (1 + change)
        price = max(price, 0.0001)

        snapshots.append(
            PriceSnapshot(
                token_address=token_address,
                symbol=symbol,
                price_usd=price,
                liquidity_usd=100_000 + i * 100,
                volume_24h_usd=50_000 + random.gauss(0, 10_000),
                volume_1h_usd=5_000 + random.gauss(0, 1_000),
                price_change_1h_pct=random.gauss(0, 5),
                price_change_24h_pct=random.gauss(0, 20),
                txns_24h_buy=random.randint(100, 300),
                txns_24h_sell=random.randint(100, 300),
                fdv=price * 1_000_000_000,
                market_cap=price * 500_000_000,
                timestamp=base_time + timedelta(minutes=i * 5),
                source="test",
                pair_created_at=base_time,
            )
        )

    return snapshots


async def test_bot_cycle():
    print("\n[End-to-End] Testing one trading cycle in paper mode...")

    bot = TradingBot()

    # Pre-populate watchlist and price history
    for i in range(2):
        token = f"TOKEN{i}TEST"
        bot.price_feed.add_to_watchlist(token)
        snapshots = generate_snapshots_for_token(token, f"TEST{i}")
        bot.price_feed.history[token] = snapshots

    # Run one trading cycle
    await bot._trading_cycle()

    print(f"  [OK] Trading cycle completed")
    print(f"  - Open positions: {len(bot.position_manager.positions)}")
    print(f"  - Risk status: {bot.risk_manager.get_status()}")

    await bot.shutdown()


def main():
    print("=" * 60)
    print("PolyCryptoAlpha End-to-End Test")
    print("=" * 60)
    asyncio.run(test_bot_cycle())
    print("=" * 60)
    print("End-to-end test complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
