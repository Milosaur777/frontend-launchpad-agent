"""
PolyCryptoAlpha v2.0 - Solana Memecoin Trading Bot
Entry point.
"""

import sys
import asyncio
import signal
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Config
from monitoring.logger import setup_logging, log
from bot_core import TradingBot


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    log.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)


def launch_ui():
    """Launch the graphical trading bot dashboard."""
    from ui.app import TradingBotApp
    app = TradingBotApp()
    app.mainloop()


def is_console_request() -> bool:
    """Check if user explicitly asked for console mode."""
    return any(arg in sys.argv for arg in ("--bot", "--console", "-c", "headless"))


async def run_bot():
    """Run the headless trading bot."""
    print("=" * 70)
    print("PolyCryptoAlpha v2.0 - Solana Memecoin Trading Bot")
    print("=" * 70)

    # Validate configuration
    try:
        Config.validate()
        log.info("Configuration validated successfully")
    except ValueError as e:
        log.error(f"Configuration error: {e}")
        print(f"\nConfiguration error:\n{e}")
        print("\nPlease copy .env.example to .env and fill in your settings.")
        sys.exit(1)

    print(f"Mode: {'LIVE' if Config.LIVE_MODE else 'PAPER TRADING'}")
    print(f"Initial Capital: ${Config.INITIAL_CAPITAL}")
    print(f"Max Risk/Trade: {Config.MAX_RISK_PER_TRADE * 100:.0f}%")
    print(f"Timeframe: {Config.TIMEFRAME}")
    print(f"RPC: {Config.PRIMARY_RPC_URL}")
    print("=" * 70)
    print()

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Setup logging
    setup_logging()

    # Start bot
    bot = TradingBot()
    try:
        await bot.run()
    except KeyboardInterrupt:
        log.info("Bot stopped by user")
    except Exception as e:
        log.error(f"Critical error: {e}", exc_info=True)
        raise
    finally:
        await bot.shutdown()


if __name__ == "__main__":
    # Default to GUI unless --bot/--console is passed
    if is_console_request():
        asyncio.run(run_bot())
    else:
        launch_ui()
