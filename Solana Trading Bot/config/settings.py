"""
PolyCryptoAlpha v2.0 Configuration
Centralized configuration for Solana memecoin trading bot.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# Load .env from project root, not from config/ directory
PROJECT_ROOT = Path(__file__).parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Config:
    """Centralized configuration loaded from environment variables."""

    # ═══════════════════════════════════════════════════════════════════════════
    # PROJECT PATHS
    # ═══════════════════════════════════════════════════════════════════════════
    PROJECT_ROOT = PROJECT_ROOT
    DATA_DIR = PROJECT_ROOT / "data"
    LOGS_DIR = PROJECT_ROOT / "logs"
    MODELS_DIR = PROJECT_ROOT / "models"
    CACHE_DIR = DATA_DIR / "cache"
    HISTORICAL_DATA_DIR = DATA_DIR / "historical"

    # ═══════════════════════════════════════════════════════════════════════════
    # SOLANA WALLET & RPC
    # ═══════════════════════════════════════════════════════════════════════════
    SOLANA_PRIVATE_KEY: str = os.getenv("SOLANA_PRIVATE_KEY", "")
    SOLANA_RPC_URL: str = os.getenv(
        "SOLANA_RPC_URL",
        "https://api.mainnet-beta.solana.com",
    )
    HELIUS_RPC_URL: str = os.getenv("HELIUS_RPC_URL", "")
    HELIUS_API_KEY: str = os.getenv("HELIUS_API_KEY", "")
    DEEXPLOIT_API_KEY: str = os.getenv("DEEXPLOIT_API_KEY", "")

    # Primary RPC URL (prefer Helius if configured)
    PRIMARY_RPC_URL: str = HELIUS_RPC_URL or SOLANA_RPC_URL
    RPC_HEADERS: dict = {"Content-Type": "application/json"}

    # Convenience access methods for non-instantiated use
    @classmethod
    def primary_rpc_url(cls) -> str:
        """Prefer Helius if configured, fallback to public RPC."""
        return cls.HELIUS_RPC_URL or cls.SOLANA_RPC_URL

    # ═══════════════════════════════════════════════════════════════════════════
    # TRADING MODE & CAPITAL
    # ═══════════════════════════════════════════════════════════════════════════
    LIVE_MODE: bool = os.getenv("LIVE_MODE", "false").lower() == "true"
    INITIAL_CAPITAL: float = float(os.getenv("INITIAL_CAPITAL", "100"))

    # ═══════════════════════════════════════════════════════════════════════════
    # RISK MANAGEMENT
    # ═══════════════════════════════════════════════════════════════════════════
    MAX_RISK_PER_TRADE: float = float(os.getenv("MAX_RISK_PER_TRADE", "0.20"))
    MAX_DAILY_LOSS: float = float(os.getenv("MAX_DAILY_LOSS", "0.10"))
    MAX_DRAWDOWN: float = float(os.getenv("MAX_DRAWDOWN", "0.30"))
    STOP_LOSS_PCT: float = float(os.getenv("STOP_LOSS_PCT", "0.15"))
    TAKE_PROFIT_PCT: float = float(os.getenv("TAKE_PROFIT_PCT", "0.20"))

    # Trailing stop-loss (optional enhancement to fixed stop-loss)
    TRAILING_STOP_PCT: float = float(os.getenv("TRAILING_STOP_PCT", "0.08"))
    TRAILING_STOP_ACTIVATION_PCT: float = float(os.getenv("TRAILING_STOP_ACTIVATION_PCT", "0.10"))

    MAX_SLIPPAGE_BPS: int = int(os.getenv("MAX_SLIPPAGE_BPS", "500"))

    # Circuit breakers
    CB_MAX_CONSECUTIVE_LOSSES: int = 3
    CB_COOLDOWN_MINUTES: int = 60

    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTION
    # ═══════════════════════════════════════════════════════════════════════════
    JITO_TIP_LAMPORTS: int = int(os.getenv("JITO_TIP_LAMPORTS", "10000"))
    JITO_BLOCK_ENGINE_URL: str = "https://mainnet.block-engine.jito.wtf/api/v1"

    # ═══════════════════════════════════════════════════════════════════════════
    # ML CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════
    MIN_CONFIDENCE: float = float(os.getenv("MIN_CONFIDENCE", "0.50"))
    ML_RETRAIN_HOURS: int = int(os.getenv("ML_RETRAIN_HOURS", "4"))
    LOOKBACK_CANDLES: int = int(os.getenv("LOOKBACK_CANDLES", "100"))
    TIMEFRAME: str = os.getenv("TIMEFRAME", "5m")

    ML_ENSEMBLE_MODELS: List[str] = ["lightgbm", "xgboost"]

    # Timeframe mapping to minutes
    TIMEFRAME_MINUTES: dict = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "4h": 240,
        "1d": 1440,
    }

    @property
    def timeframe_minutes(self) -> int:
        return self.TIMEFRAME_MINUTES.get(self.TIMEFRAME, 5)

    # ═══════════════════════════════════════════════════════════════════════════
    # ASSET FILTERS — ESTABLISHED VIRAL MEMECOINS ONLY
    # We ignore brand-new launches / PumpFun snipes and trade tokens that already
    # have proven liquidity, volume, and on-chain activity.
    # ═══════════════════════════════════════════════════════════════════════════
    MIN_LIQUIDITY_USD: float = 50_000.0  # Minimum pool liquidity
    MIN_VOLUME_24H_USD: float = 100_000.0  # Minimum 24h volume
    MIN_TOKEN_AGE_HOURS: float = 24.0  # Must be at least 24h old
    MAX_TOKEN_AGE_HOURS: float = 720.0  # Ignore stale / dead tokens older than 30d
    MIN_TXNS_24H: int = 500  # Minimum 24h transactions (buy+sell)
    MIN_BUY_RATIO: float = 0.35  # Min healthy buy ratio
    MAX_BUY_RATIO: float = 0.75  # Max healthy buy ratio
    MIN_HOLDERS: int = 200  # Minimum unique holders

    # ═══════════════════════════════════════════════════════════════════════════
    # WATCHLIST MODE
    # "discovery" = scan DexScreener for trending tokens
    # "fixed"     = trade only the curated FIXED_WATCHLIST below
    # ═══════════════════════════════════════════════════════════════════════════
    WATCHLIST_MODE: str = os.getenv("WATCHLIST_MODE", "discovery")

    # Curated list of established Solana memecoins (symbol -> mint address)
    FIXED_WATCHLIST: dict = {
        "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
        "TRUMP": "6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN",
        "WEN": "WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk",
        "PONKE": "5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC",
        "BONK2": "6yiDKPDbqWLGAEBkDvVg6UNrKsLsPVkLbA1TJo4KCdzP",
        "MOG": "36TTDWEvZNpKA7CQHMXZxnwGk74UAHwEDdCpLeFbtTCy",
        "GIGA": "4HH28JezeYFYGJNHz8PBivGbBPSDtvQVKqHyMPPyhT6v",
        "PNUT": "Dn3DFUNDKEyMJGrEsuzTiYrfEwtPo86iH5qTKzbbtiag",
    }

    # Robinhood Chain memecoins (EVM addresses)
    # No OHLCV data available yet - live prices only via DexScreener
    ROBINHOOD_CHAIN_WATCHLIST: dict = {
        "CASHCAT": "0x3bA24aE811cA41964791a6828C578fd9D9195c72",
        "HOODRAT": "0x8e62F281f282686fCa6dCB39288069a93fC23F1c",
        "TENDIES": "0x45242320DBB855EeA8Fd36804C6487E10E97FCF9",
        "WENLAMBO": "0xA80eb66b3E0CF66ccB46f8b8C9e7ff5803eEb820",
        "DIH": "0x1E9e4dD08C116DF16DF478f82c6a3823B78F0eea",
    }

    # ═══════════════════════════════════════════════════════════════════════════
    # ROBINHOOD CHAIN SNIPER BOT
    # ═══════════════════════════════════════════════════════════════════════════
    ROBINHOOD_RPC_URL: str = "https://rpc.mainnet.chain.robinhood.com"
    ROBINHOOD_CHAIN_ID: int = 4663
    SNIPER_BUY_AMOUNT_WETH: float = float(os.getenv("SNIPER_BUY_AMOUNT_WETH", "0.0005"))
    SNIPER_MAX_CONCURRENT: int = int(os.getenv("SNIPER_MAX_CONCURRENT", "3"))
    SNIPER_BUY_DELAY: float = float(os.getenv("SNIPER_BUY_DELAY", "0.5"))
    SNIPER_AUTO_SELL_PNL_PCT: float = float(os.getenv("SNIPER_AUTO_SELL_PNL_PCT", "100"))
    SNIPER_AUTO_STOP_LOSS_PCT: float = float(os.getenv("SNIPER_AUTO_STOP_LOSS_PCT", "-50"))
    SNIPER_ENABLED: bool = os.getenv("SNIPER_ENABLED", "false").lower() == "true"

    # ═══════════════════════════════════════════════════════════════════════════
    # BACKTEST CONFIG
    # ═══════════════════════════════════════════════════════════════════════════
    BACKTEST_INITIAL_CAPITAL: float = float(os.getenv("BACKTEST_INITIAL_CAPITAL", "100"))
    BACKTEST_FEE_PCT: float = float(os.getenv("BACKTEST_FEE_PCT", "0.002"))  # 0.2% per trade

    # ═══════════════════════════════════════════════════════════════════════════
    # NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    # ═══════════════════════════════════════════════════════════════════════════
    # LOGGING
    # ═══════════════════════════════════════════════════════════════════════════
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_RETENTION_DAYS: int = 7

    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDATION
    # ═══════════════════════════════════════════════════════════════════════════
    @classmethod
    def validate(cls) -> None:
        """Validate critical configuration. Raises ValueError on failure."""
        errors = []

        if not cls.SOLANA_PRIVATE_KEY:
            errors.append("SOLANA_PRIVATE_KEY is not set in .env")
        elif len(cls.SOLANA_PRIVATE_KEY) < 32:
            errors.append("SOLANA_PRIVATE_KEY looks invalid (too short)")

        if cls.INITIAL_CAPITAL <= 0:
            errors.append("INITIAL_CAPITAL must be positive")

        if cls.MAX_RISK_PER_TRADE <= 0 or cls.MAX_RISK_PER_TRADE > 1:
            errors.append("MAX_RISK_PER_TRADE must be between 0 and 1")

        if cls.MAX_DRAWDOWN <= 0 or cls.MAX_DRAWDOWN > 1:
            errors.append("MAX_DRAWDOWN must be between 0 and 1")

        if cls.MAX_SLIPPAGE_BPS < 0 or cls.MAX_SLIPPAGE_BPS > 10000:
            errors.append("MAX_SLIPPAGE_BPS must be between 0 and 10000")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(errors))


# Auto-validate on import when run directly
if __name__ == "__main__":
    Config.validate()
    print("Configuration validated successfully.")
