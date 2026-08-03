"""
Paper trading demo — runs a few cycles and exits.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Config
from monitoring.logger import setup_logging, log
from bot_core import TradingBot

DEMO_CYCLES = 5


async def main():
    print("=" * 60)
    print("PolyCryptoAlpha — Paper Trading Demo")
    print("=" * 60)

    Config.validate()
    setup_logging()

    bot = TradingBot()

    try:
        for i in range(DEMO_CYCLES):
            bot.cycle_count += 1
            log.info(f"--- Demo cycle {i + 1}/{DEMO_CYCLES} ---")
            await bot._trading_cycle()
            await asyncio.sleep(2)

        log.info("Demo complete — showing trade summary")
        stats = bot.position_manager.get_trade_stats()
        print("\n" + "=" * 60)
        print("DEMO RESULTS")
        print("=" * 60)
        print(f"Total trades:   {stats['total_trades']}")
        print(f"Winning:        {stats['winning_trades']}")
        print(f"Losing:         {stats['losing_trades']}")
        print(f"Win rate:       {stats['win_rate']:.1%}")
        print(f"Realized PnL:   ${stats['total_pnl']:.2f}")
        print("=" * 60)
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
