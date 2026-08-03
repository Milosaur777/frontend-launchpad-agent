"""
Auto-fetch historical OHLCV data for Solana tokens.
Uses Dexploit free API (unlimited requests, 20 RPS) for candlestick data.
"""

import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional

import requests

from config.settings import Config
from data.price_feed import PriceFeed, PriceSnapshot


DEEXPLOIT_BASE = "https://api.dexploit.dev"


def fetch_ohlcv(
    token_address: str,
    resolution: str = "5m",
    hours: int = 72,
    api_key: str = "",
) -> List[dict]:
    """
    Fetch OHLCV candles from Dexploit API.

    Args:
        token_address: Token mint address.
        resolution: Candle size (1m, 5m, 1h, 1d).
        hours: How many hours of history to fetch.
        api_key: Dexploit API key.

    Returns:
        List of OHLCV dicts.
    """
    if not api_key:
        return []

    url = f"{DEEXPLOIT_BASE}/price/history"
    headers = {"X-API-Key": api_key}
    params = {
        "token": token_address,
        "resolution": resolution,
        "limit": 1000,
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("results", [])
        else:
            print(f"  [dexploit] {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"  [dexploit] Error fetching OHLCV: {e}")
    return []


def ohlcv_to_snapshots(
    token_address: str,
    symbol: str,
    candles: List[dict],
) -> List[PriceSnapshot]:
    """
    Convert OHLCV candles to PriceSnapshot objects.

    Args:
        token_address: Token mint address.
        symbol: Token symbol.
        candles: List of OHLCV dicts from Dexploit.

    Returns:
        List of PriceSnapshot objects.
    """
    snapshots = []
    prev_close = 0.0

    for candle in candles:
        try:
            # Parse timestamp (unix milliseconds)
            ts_ms = candle.get("ts_ms", 0)
            ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

            o = float(candle.get("open", 0))
            h = float(candle.get("high", 0))
            l = float(candle.get("low", 0))
            c = float(candle.get("close", 0))
            vol_sol = float(candle.get("volume_sol", 0)) / 1e9  # Convert lamports

            if c <= 0:
                continue

            # Compute synthetic changes
            change_1h = 0.0
            if prev_close > 0:
                change_1h = (c / prev_close - 1) * 100

            snapshots.append(
                PriceSnapshot(
                    token_address=token_address,
                    symbol=symbol,
                    price_usd=c,
                    liquidity_usd=0.0,
                    volume_24h_usd=vol_sol * c,
                    volume_1h_usd=vol_sol * c,
                    price_change_1h_pct=change_1h,
                    price_change_24h_pct=0.0,
                    txns_24h_buy=0,
                    txns_24h_sell=0,
                    fdv=c * 1_000_000_000,
                    market_cap=c * 500_000_000,
                    timestamp=ts,
                    source="dexploit",
                    pair_created_at=datetime.now(timezone.utc) - timedelta(hours=48),
                )
            )
            prev_close = c
        except (ValueError, KeyError):
            continue

    return snapshots


def fetch_token_history(
    token_address: str,
    symbol: str,
    resolution: str = "5m",
    hours: int = 72,
    api_key: str = "",
) -> List[PriceSnapshot]:
    """
    Fetch historical data for a single token.
    """
    candles = fetch_ohlcv(token_address, resolution, hours, api_key)
    if not candles:
        return []
    return ohlcv_to_snapshots(token_address, symbol, candles)


def fetch_all_watchlist(
    resolution: str = "5m",
    hours: int = 72,
    api_key: str = "",
    feed: Optional[PriceFeed] = None,
) -> PriceFeed:
    """
    Fetch historical data for all tokens in the fixed watchlist.
    """
    if feed is None:
        feed = PriceFeed()

    if not api_key:
        print("No API key provided. Get one free at https://dexploit.dev")
        return feed

    print(f"Fetching historical data from Dexploit...")
    print(f"  Resolution: {resolution}, History: {hours}h")

    for symbol, address in Config.FIXED_WATCHLIST.items():
        print(f"  Fetching {symbol}...", end=" ", flush=True)
        snapshots = fetch_token_history(address, symbol, resolution, hours, api_key)
        if snapshots:
            feed.history[address] = snapshots
            feed.add_to_watchlist(address)
            print(f"{len(snapshots)} candles")
        else:
            print("no data")
        time.sleep(0.1)  # Rate limit (20 RPS allowed)

    return feed


def save_to_csv(
    snapshots: List[PriceSnapshot],
    output_path: str | Path,
) -> None:
    """
    Save PriceSnapshot list to TradingView-compatible CSV.
    """
    import csv

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "Open", "High", "Low", "Close", "Volume"])

        for snap in snapshots:
            writer.writerow([
                snap.timestamp.strftime("%Y-%m-%d %H:%M"),
                f"{snap.price_usd:.10f}",
                f"{snap.price_usd * 1.001:.10f}",
                f"{snap.price_usd * 0.999:.10f}",
                f"{snap.price_usd:.10f}",
                int(snap.volume_1h_usd / max(snap.price_usd, 1e-9)),
            ])

    print(f"  Saved {len(snapshots)} candles to {output_path}")


if __name__ == "__main__":
    api_key = getattr(Config, "DEEXPLOIT_API_KEY", "")
    if not api_key:
        print("No DEEXPLOIT_API_KEY configured. Get one free at https://dexploit.dev/dashboard")
        exit(1)

    feed = fetch_all_watchlist(
        resolution="5m",
        hours=72,
        api_key=api_key,
    )

    csv_dir = Config.HISTORICAL_DATA_DIR
    csv_dir.mkdir(parents=True, exist_ok=True)

    for symbol, address in Config.FIXED_WATCHLIST.items():
        if address in feed.history:
            output = csv_dir / f"{symbol.lower()}_5m.csv"
            save_to_csv(feed.history[address], output)
