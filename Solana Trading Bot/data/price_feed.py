"""
Aggregated price feed combining DexScreener and Jupiter data.
Maintains a rolling price cache for feature engineering.
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import json
from pathlib import Path

from data.dexscreener import DexScreenerClient, TokenPair
from data.jupiter import JupiterClient
from config.settings import Config


@dataclass
class PriceSnapshot:
    """A single price snapshot for a token."""

    token_address: str
    symbol: str
    price_usd: float
    liquidity_usd: float
    volume_24h_usd: float
    volume_1h_usd: float
    price_change_1h_pct: float
    price_change_24h_pct: float
    txns_24h_buy: int
    txns_24h_sell: int
    fdv: float
    market_cap: float
    timestamp: datetime
    source: str
    pair_created_at: Optional[datetime] = None


class PriceFeed:
    """
    Aggregates real-time price data and maintains rolling cache.

    Since free APIs don't provide historical OHLCV easily, we sample
    prices periodically and build our own candle history.
    """

    def __init__(
        self,
        dexscreener: Optional[DexScreenerClient] = None,
        jupiter: Optional[JupiterClient] = None,
        cache_dir: Optional[Path] = None,
    ):
        self.dex = dexscreener or DexScreenerClient()
        self.jupiter = jupiter or JupiterClient()
        self.cache_dir = cache_dir or Config.CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory price history: token_address -> list of snapshots
        self.history: Dict[str, List[PriceSnapshot]] = defaultdict(list)
        self._watchlist: Dict[str, str] = {}  # address -> chain

    def add_to_watchlist(self, token_address: str, chain: str = "solana"):
        """Add token to watchlist with chain info."""
        self._watchlist[token_address] = chain

    def remove_from_watchlist(self, token_address: str):
        """Remove token from watchlist."""
        self._watchlist.pop(token_address, None)

    async def update_watchlist_from_dexscreener(
        self,
        chain: str = "solana",
        top_n: int = 50,
    ) -> List[TokenPair]:
        """Update watchlist with trending tokens from DexScreener."""
        pairs = await self.dex.get_trending_tokens(
            chain=chain,
            min_liquidity=Config.MIN_LIQUIDITY_USD,
            min_volume_24h=Config.MIN_VOLUME_24H_USD,
            max_age_hours=Config.MAX_TOKEN_AGE_HOURS,
            top_n=top_n,
        )
        for pair in pairs:
            self.add_to_watchlist(pair.base_token_address, chain=chain)
        return pairs

    async def fetch_snapshot(self, token_address: str) -> Optional[PriceSnapshot]:
        """Fetch a single price snapshot for a token."""
        # Try DexScreener first (has liquidity + volume data)
        pairs = await self.dex.get_token_pairs(token_address)
        if pairs:
            best = max(pairs, key=lambda p: p.liquidity_usd)
            return PriceSnapshot(
                token_address=token_address,
                symbol=best.base_token_symbol,
                price_usd=best.price_usd,
                liquidity_usd=best.liquidity_usd,
                volume_24h_usd=best.volume_24h_usd,
                volume_1h_usd=best.volume_1h_usd,
                price_change_1h_pct=best.price_change_1h_pct,
                price_change_24h_pct=best.price_change_24h_pct,
                txns_24h_buy=best.txns_24h_buy,
                txns_24h_sell=best.txns_24h_sell,
                fdv=best.fdv,
                market_cap=best.market_cap,
                timestamp=datetime.now(),
                source="dexscreener",
                pair_created_at=best.pair_created_at,
            )

        # Fallback to Jupiter price API
        prices = await self.jupiter.get_price([token_address])
        if token_address in prices:
            return PriceSnapshot(
                token_address=token_address,
                symbol="UNKNOWN",
                price_usd=prices[token_address],
                liquidity_usd=0.0,
                volume_24h_usd=0.0,
                volume_1h_usd=0.0,
                price_change_1h_pct=0.0,
                price_change_24h_pct=0.0,
                txns_24h_buy=0,
                txns_24h_sell=0,
                fdv=0.0,
                market_cap=0.0,
                timestamp=datetime.now(),
                source="jupiter",
                pair_created_at=None,
            )

        return None

    async def update_all(self) -> Dict[str, PriceSnapshot]:
        """Update snapshots for all watched tokens using batch API."""
        results = {}
        if not self._watchlist:
            return results

        # Group tokens by chain
        solana_tokens = [addr for addr, chain in self._watchlist.items() if chain == "solana"]
        robinhood_tokens = [addr for addr, chain in self._watchlist.items() if chain == "robinhood"]

        # Fetch in batches (batch endpoint supports up to 30 tokens)
        all_pairs: Dict[str, List[TokenPair]] = {}

        if solana_tokens:
            for i in range(0, len(solana_tokens), 30):
                batch = solana_tokens[i:i+30]
                try:
                    batch_pairs = await self.dex.get_batch_token_pairs(batch, chain="solana")
                    all_pairs.update(batch_pairs)
                except Exception as e:
                    import logging
                    logging.warning(f"Failed to fetch Solana batch: {e}")

            # Fallback: if batch returned nothing for some tokens, try individually
            missing = [addr for addr in solana_tokens if addr not in all_pairs or not all_pairs.get(addr)]
            for addr in missing[:10]:  # Limit to avoid rate limits
                try:
                    pairs = await self.dex.get_token_pairs(addr)
                    if pairs:
                        all_pairs[addr] = pairs
                except Exception:
                    pass

        if robinhood_tokens:
            for i in range(0, len(robinhood_tokens), 30):
                batch = robinhood_tokens[i:i+30]
                try:
                    batch_pairs = await self.dex.get_batch_token_pairs(batch, chain="robinhood")
                    all_pairs.update(batch_pairs)
                except Exception as e:
                    import logging
                    logging.warning(f"Failed to fetch Robinhood batch: {e}")

        # Convert to snapshots
        now = datetime.now()
        for addr, pairs in all_pairs.items():
            if not pairs:
                continue
            best = max(pairs, key=lambda p: p.liquidity_usd)
            snap = PriceSnapshot(
                token_address=addr,
                symbol=best.base_token_symbol,
                price_usd=best.price_usd,
                liquidity_usd=best.liquidity_usd,
                volume_24h_usd=best.volume_24h_usd,
                volume_1h_usd=best.volume_1h_usd,
                price_change_1h_pct=best.price_change_1h_pct,
                price_change_24h_pct=best.price_change_24h_pct,
                txns_24h_buy=best.txns_24h_buy,
                txns_24h_sell=best.txns_24h_sell,
                fdv=best.fdv,
                market_cap=best.market_cap,
                timestamp=now,
                source="dexscreener",
                pair_created_at=best.pair_created_at,
            )
            self.history[addr].append(snap)
            self.history[addr] = self.history[addr][-500:]
            results[addr] = snap

        return results

    def get_history(self, token_address: str, max_age_minutes: Optional[int] = None) -> List[PriceSnapshot]:
        """Get price history for a token, optionally filtered by age."""
        history = self.history.get(token_address, [])
        if max_age_minutes is None:
            return history

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=max_age_minutes)
        filtered = []
        for h in history:
            ts = h.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if ts >= cutoff:
                filtered.append(h)
        return filtered

    def get_latest(self, token_address: str) -> Optional[PriceSnapshot]:
        """Get latest snapshot for a token."""
        history = self.history.get(token_address, [])
        return history[-1] if history else None

    def save_cache(self):
        """Persist history to disk."""
        cache_file = self.cache_dir / "price_history.json"
        serializable = {}
        for addr, snaps in self.history.items():
            serializable[addr] = [
                {
                    "token_address": s.token_address,
                    "symbol": s.symbol,
                    "price_usd": s.price_usd,
                    "liquidity_usd": s.liquidity_usd,
                    "volume_24h_usd": s.volume_24h_usd,
                    "volume_1h_usd": s.volume_1h_usd,
                    "price_change_1h_pct": s.price_change_1h_pct,
                    "price_change_24h_pct": s.price_change_24h_pct,
                    "txns_24h_buy": s.txns_24h_buy,
                    "txns_24h_sell": s.txns_24h_sell,
                    "fdv": s.fdv,
                    "market_cap": s.market_cap,
                    "timestamp": s.timestamp.isoformat(),
                    "source": s.source,
                    "pair_created_at": s.pair_created_at.isoformat() if s.pair_created_at else None,
                }
                for s in snaps
            ]
        with open(cache_file, "w") as f:
            json.dump(serializable, f, indent=2)

    def load_cache(self):
        """Load history from disk."""
        cache_file = self.cache_dir / "price_history.json"
        if not cache_file.exists():
            return

        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
            for addr, snaps in data.items():
                self.history[addr] = [
                    PriceSnapshot(
                        token_address=s["token_address"],
                        symbol=s["symbol"],
                        price_usd=s["price_usd"],
                        liquidity_usd=s["liquidity_usd"],
                        volume_24h_usd=s["volume_24h_usd"],
                        volume_1h_usd=s["volume_1h_usd"],
                        price_change_1h_pct=s["price_change_1h_pct"],
                        price_change_24h_pct=s["price_change_24h_pct"],
                        txns_24h_buy=s["txns_24h_buy"],
                        txns_24h_sell=s["txns_24h_sell"],
                        fdv=s["fdv"],
                        market_cap=s["market_cap"],
                        timestamp=datetime.fromisoformat(s["timestamp"]),
                        source=s["source"],
                        pair_created_at=datetime.fromisoformat(s["pair_created_at"]) if s.get("pair_created_at") else None,
                    )
                    for s in snaps
                ]
        except Exception:
            pass

    async def close(self):
        """Close underlying API clients."""
        await self.dex.close()
        await self.jupiter.close()
