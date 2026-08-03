"""
Historical data loader for TradingView CSV exports.

TradingView exports OHLCV data that we convert into PriceSnapshot objects
for the backtest engine and live bot warm-up.

Usage:
    Export data from TradingView:
    1. Open chart for token (e.g., BONK/USD)
    2. Click "Export chart data" (three dots menu)
    3. Save as CSV

    Then load it:
        from data.historical_loader import load_tradingview_csv
        feed = load_tradingview_csv("BONK", "BONK", "path/to/export.csv")
"""

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from data.price_feed import PriceFeed, PriceSnapshot


def parse_number(s: str) -> float:
    """Parse a number string, handling both '.' and ',' as decimal separator."""
    s = s.strip()
    # Handle European format: 1.234,56 -> 1234.56
    # and: 0,000011 -> 0.000011
    if "," in s and "." in s:
        # Both present: assume comma is thousands separator
        s = s.replace(",", "")
    elif "," in s:
        # Only comma: treat as decimal separator (TradingView European export)
        s = s.replace(",", ".")
    return float(s)


def parse_tradingview_timestamp(ts: str) -> datetime:
    """
    Parse TradingView timestamp formats.

    Supports:
    - "2024-01-15T00:00:00Z"
    - "2024-01-15 00:00"
    - "2024-01-15"
    - Unix seconds/milliseconds (as string)
    """
    ts = ts.strip()

    # Unix timestamp
    if ts.isdigit():
        val = int(ts)
        if val > 1e12:
            val = val / 1000
        return datetime.fromtimestamp(val, tz=timezone.utc)

    # ISO formats
    for fmt in [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    raise ValueError(f"Cannot parse timestamp: {ts}")


def load_tradingview_csv(
    token_address: str,
    symbol: str,
    csv_path: str | Path,
    liquidity_usd: float = 200_000.0,
    volume_24h_usd: float = 300_000.0,
) -> List[PriceSnapshot]:
    """
    Load a TradingView CSV export and convert to PriceSnapshot list.

    Expected CSV columns (case-insensitive, flexible matching):
    - Time / Date / Timestamp
    - Open
    - High
    - Low
    - Close
    - Volume (optional, defaults to 0)

    Args:
        token_address: Token mint address.
        symbol: Token symbol.
        csv_path: Path to the CSV file.
        liquidity_usd: Default liquidity (TradingView doesn't provide this).
        volume_24h_usd: Default volume (TradingView doesn't provide this).

    Returns:
        List of PriceSnapshot from oldest to newest.
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    snapshots: List[PriceSnapshot] = []

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    if len(lines) < 2:
        return snapshots

    # Detect European decimal format by checking field counts
    header = lines[0]
    first_data = lines[1]
    header_fields = len(header.split(","))
    data_fields = len(first_data.split(","))

    if data_fields > header_fields:
        # European format: manually parse each line
        # Split by comma, then reconstruct values using the known structure:
        # Time,Open,High,Low,Close,Volume
        # where Open/High/Low/Close use comma as decimal: "0,0000116016"
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) < 3:
                continue
            try:
                # Time is first field (no commas in timestamp)
                ts_str = parts[0]
                ts = parse_tradingview_timestamp(ts_str)

                # After time, we have pairs of digits for each price field
                # Pattern: d,dddddddddd (integer part, comma, decimal part)
                # We need to extract: Open, High, Low, Close, Volume
                # Each price field is: X,YYYYYYYYYY (where X is 0-9 and Y is 10 digits)
                # Volume is just an integer at the end

                # Skip time, parse remaining
                remaining = ",".join(parts[1:])
                # Match price patterns: single digit, comma, 10 digits
                import re
                price_pattern = r'(\d),(\d{10})'
                prices = []
                last_end = 0
                for m in re.finditer(price_pattern, remaining):
                    prices.append(float(f"{m.group(1)}.{m.group(2)}"))
                    last_end = m.end()

                # Volume is the last number after all prices
                vol_str = remaining[last_end:].lstrip(",")
                vol = float(vol_str) if vol_str else 0.0

                if len(prices) >= 4:
                    o, h, l, c = prices[0], prices[1], prices[2], prices[3]
                    if c > 0:
                        change_1h = 0.0
                        if snapshots and snapshots[-1].price_usd > 0:
                            change_1h = (c / snapshots[-1].price_usd - 1) * 100

                        # Use current time minus 48h for pair_created_at so age filter works
                        from datetime import datetime, timezone, timedelta
                        now = datetime.now(timezone.utc) - timedelta(hours=48)

                        snapshots.append(
                            PriceSnapshot(
                                token_address=token_address,
                                symbol=symbol,
                                price_usd=c,
                                liquidity_usd=liquidity_usd,
                                volume_24h_usd=volume_24h_usd + vol,
                                volume_1h_usd=vol,
                                price_change_1h_pct=change_1h,
                                price_change_24h_pct=0.0,
                                txns_24h_buy=500,
                                txns_24h_sell=400,
                                fdv=c * 1_000_000_000,
                                market_cap=c * 500_000_000,
                                timestamp=ts,
                                source="tradingview",
                                pair_created_at=now,
                            )
                        )
            except (ValueError, KeyError, IndexError):
                continue
    else:
        # Standard format: use csv.DictReader
        import io
        reader = csv.DictReader(io.StringIO("\n".join(lines)))

        fieldnames = {name.lower().strip(): name for name in (reader.fieldnames or [])}

        time_col = None
        for candidate in ["time", "date", "timestamp"]:
            if candidate in fieldnames:
                time_col = fieldnames[candidate]
                break

        if not time_col:
            raise ValueError(f"CSV must have a Time/Date/Timestamp column. Found: {list(fieldnames.keys())}")

        for col in ["open", "high", "low", "close"]:
            if col not in fieldnames:
                raise ValueError(f"CSV missing required column: {col}")

        open_col = fieldnames["open"]
        high_col = fieldnames["high"]
        low_col = fieldnames["low"]
        close_col = fieldnames["close"]
        vol_col = fieldnames.get("volume", None)

        prev_close = 0.0
        for row in reader:
            try:
                ts = parse_tradingview_timestamp(row[time_col])
                o = parse_number(row[open_col])
                h = parse_number(row[high_col])
                l = parse_number(row[low_col])
                c = parse_number(row[close_col])
                vol = parse_number(row[vol_col]) if vol_col and row.get(vol_col) else 0.0

                if c <= 0:
                    continue

                change_1h = 0.0
                if prev_close > 0:
                    change_1h = (c / prev_close - 1) * 100

                # Use current time minus 48h for pair_created_at so age filter works
                from datetime import datetime, timezone, timedelta
                now = datetime.now(timezone.utc) - timedelta(hours=48)

                snapshots.append(
                    PriceSnapshot(
                        token_address=token_address,
                        symbol=symbol,
                        price_usd=c,
                        liquidity_usd=liquidity_usd,
                        volume_24h_usd=volume_24h_usd + vol,
                        volume_1h_usd=vol,
                        price_change_1h_pct=change_1h,
                        price_change_24h_pct=0.0,
                        txns_24h_buy=500,
                        txns_24h_sell=400,
                        fdv=c * 1_000_000_000,
                        market_cap=c * 500_000_000,
                        timestamp=ts,
                        source="tradingview",
                        pair_created_at=now,
                    )
                )
                prev_close = c
            except (ValueError, KeyError):
                continue

    # Backfill 24h change now that we have full history
    for i, snap in enumerate(snapshots):
        if i >= 288:
            snap.price_change_24h_pct = (
                (snap.price_usd / snapshots[i - 288].price_usd - 1) * 100
            )

    return snapshots


def load_to_feed(
    token_address: str,
    symbol: str,
    csv_path: str | Path,
    feed: Optional[PriceFeed] = None,
    **kwargs,
) -> PriceFeed:
    """
    Load CSV into a PriceFeed.

    Args:
        token_address: Token mint address.
        symbol: Token symbol.
        csv_path: Path to CSV file.
        feed: Existing PriceFeed to add to (created if None).

    Returns:
        PriceFeed with loaded history.
    """
    snapshots = load_tradingview_csv(token_address, symbol, csv_path, **kwargs)

    if feed is None:
        feed = PriceFeed()

    # Append to existing history (sorted by time)
    existing = feed.history.get(token_address, [])
    combined = existing + snapshots
    combined.sort(key=lambda s: s.timestamp)
    feed.history[token_address] = combined
    feed.add_to_watchlist(token_address)

    return feed


def load_multiple_csvs(
    token_map: dict,
    data_dir: str | Path,
    **kwargs,
) -> PriceFeed:
    """
    Load multiple CSVs from a directory.

    Args:
        token_map: {symbol: (token_address, filename)} mapping.
                   Example: {"BONK": ("DezXAZ...", "bonk_5m.csv")}
        data_dir: Directory containing CSV files.

    Returns:
        PriceFeed with all loaded histories.
    """
    data_dir = Path(data_dir)
    feed = PriceFeed()

    for symbol, (address, filename) in token_map.items():
        csv_path = data_dir / filename
        if csv_path.exists():
            load_to_feed(address, symbol, csv_path, feed=feed, **kwargs)
            count = len(feed.history.get(address, []))
            print(f"  Loaded {symbol}: {count} bars")
        else:
            print(f"  Skipped {symbol}: {csv_path} not found")

    return feed
