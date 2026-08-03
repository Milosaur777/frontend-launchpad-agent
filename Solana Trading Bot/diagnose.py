"""Diagnose why ML training fails."""
import asyncio
from datetime import datetime
from bot_core import TradingBot
from config.settings import Config

async def diagnose():
    bot = TradingBot()
    bot._warm_from_csvs()
    await bot._update_watchlist()

    # Run a few cycles to get data
    for i in range(3):
        try:
            await bot._trading_cycle()
        except Exception as e:
            print(f"Cycle {i} error: {e}")
        await asyncio.sleep(1)

    print(f"\n=== DIAGNOSIS ===")
    print(f"History has {len(bot.price_feed.history)} tokens")
    for addr, snaps in bot.price_feed.history.items():
        print(f"  {addr[:12]}...: {len(snaps)} snapshots")

    # Try training data generation
    print(f"\n=== TRAINING DATA ===")
    try:
        df = bot.trainer.generate_training_data(
            bot.price_feed.history,
            forward_bars=3,
        )
        if df is None:
            print("generate_training_data returned None!")
        else:
            print(f"Generated {len(df)} rows, {len(df.columns)} columns")
            print(f"Columns: {list(df.columns[:10])}...")
            if "target" in df.columns:
                print(f"Target distribution: {df['target'].value_counts().to_dict()}")
    except Exception as e:
        print(f"generate_training_data FAILED: {e}")
        import traceback
        traceback.print_exc()

    # Check risk manager
    print(f"\n=== RISK MANAGER ===")
    check = bot.risk_manager.can_trade()
    print(f"can_trade: allowed={check.allowed}, reason={check.reason}")

    await bot.shutdown()

asyncio.run(diagnose())
