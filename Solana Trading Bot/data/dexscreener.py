"""
DexScreener API client (free tier).
Provides token prices, liquidity, volume, and trending pairs.
Docs: https://docs.dexscreener.com/
"""

import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

import aiohttp


@dataclass
class TokenPair:
    """Normalized token pair data from DexScreener."""

    chain_id: str
    dex_id: str
    pair_address: str
    base_token_address: str
    base_token_symbol: str
    quote_token_address: str
    quote_token_symbol: str
    price_usd: float
    liquidity_usd: float
    volume_24h_usd: float
    volume_6h_usd: float
    volume_1h_usd: float
    price_change_24h_pct: float
    price_change_6h_pct: float
    price_change_1h_pct: float
    txns_24h_buy: int
    txns_24h_sell: int
    fdv: float
    market_cap: float
    pair_created_at: Optional[datetime]
    url: str


class DexScreenerClient:
    """Async client for DexScreener API."""

    BASE_URL = "https://api.dexscreener.com"

    def __init__(self, rate_limit_delay: float = 0.5):
        """
        Initialize client.

        Args:
            rate_limit_delay: Seconds between requests to avoid rate limits.
        """
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"Accept": "application/json"},
            )
        return self._session

    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a rate-limited GET request."""
        # Basic rate limiting
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)

        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"

        try:
            async with session.get(url, params=params) as resp:
                self._last_request_time = asyncio.get_event_loop().time()
                if resp.status >= 400:
                    return {}
                return await resp.json()
        except Exception:
            return {}

    def _parse_pair(self, pair: Dict) -> Optional[TokenPair]:
        """Parse raw DexScreener pair data into TokenPair."""
        try:
            base = pair.get("baseToken", {})
            quote = pair.get("quoteToken", {})
            liquidity = pair.get("liquidity", {}) or {}
            volume = pair.get("volume", {}) or {}
            price_change = pair.get("priceChange", {}) or {}
            txns = pair.get("txns", {}) or {}
            txns_24h = txns.get("h24", {}) or {}

            created_at = pair.get("pairCreatedAt")
            if created_at:
                created_at = datetime.fromtimestamp(created_at / 1000)

            return TokenPair(
                chain_id=pair.get("chainId", ""),
                dex_id=pair.get("dexId", ""),
                pair_address=pair.get("pairAddress", ""),
                base_token_address=base.get("address", ""),
                base_token_symbol=base.get("symbol", ""),
                quote_token_address=quote.get("address", ""),
                quote_token_symbol=quote.get("symbol", ""),
                price_usd=float(pair.get("priceUsd", 0) or 0),
                liquidity_usd=float(liquidity.get("usd", 0) or 0),
                volume_24h_usd=float(volume.get("h24", 0) or 0),
                volume_6h_usd=float(volume.get("h6", 0) or 0),
                volume_1h_usd=float(volume.get("h1", 0) or 0),
                price_change_24h_pct=float(price_change.get("h24", 0) or 0),
                price_change_6h_pct=float(price_change.get("h6", 0) or 0),
                price_change_1h_pct=float(price_change.get("h1", 0) or 0),
                txns_24h_buy=int(txns_24h.get("buys", 0) or 0),
                txns_24h_sell=int(txns_24h.get("sells", 0) or 0),
                fdv=float(pair.get("fdv", 0) or 0),
                market_cap=float(pair.get("marketCap", 0) or 0),
                pair_created_at=created_at,
                url=pair.get("url", ""),
            )
        except (KeyError, ValueError, TypeError):
            return None

    async def search_pairs(self, query: str) -> List[TokenPair]:
        """Search for token pairs by symbol or address."""
        data = await self._request(f"/latest/dex/search", params={"q": query})
        pairs = data.get("pairs", []) or []
        parsed = [self._parse_pair(p) for p in pairs]
        return [p for p in parsed if p is not None]

    async def get_token_pairs(self, token_address: str) -> List[TokenPair]:
        """Get all pairs for a specific token address."""
        data = await self._request(f"/latest/dex/tokens/{token_address}")
        pairs = data.get("pairs", []) or []
        parsed = [self._parse_pair(p) for p in pairs]
        return [p for p in parsed if p is not None]

    async def get_batch_token_pairs(self, token_addresses: List[str], chain: str = "solana") -> Dict[str, List[TokenPair]]:
        """Get pairs for multiple tokens in one request (reduces rate limit usage)."""
        if not token_addresses:
            return {}

        # DexScreener batch endpoint: /tokens/v1/{chain}/{tokenAddresses}
        addr_str = ",".join(token_addresses[:30])  # Max 30 per request
        data = await self._request(f"/tokens/v1/{chain}/{addr_str}")

        # Group by token address
        result: Dict[str, List[TokenPair]] = {addr: [] for addr in token_addresses}
        pairs = data if isinstance(data, list) else data.get("pairs", []) or []

        for p in pairs:
            parsed = self._parse_pair(p)
            if parsed:
                addr = parsed.base_token_address
                if addr in result:
                    result[addr].append(parsed)

        return result

    async def get_pair(self, chain: str, pair_address: str) -> Optional[TokenPair]:
        """Get a specific pair by chain and pair address."""
        data = await self._request(f"/latest/dex/pairs/{chain}/{pair_address}")
        pairs = data.get("pairs", []) or []
        if not pairs:
            return None
        return self._parse_pair(pairs[0])

    async def get_trending_tokens(
        self,
        chain: str = "solana",
        min_liquidity: float = 50_000.0,
        min_volume_24h: float = 100_000.0,
        min_token_age_hours: float = 24.0,
        max_token_age_hours: Optional[float] = 720.0,
        min_txns_24h: int = 500,
        min_buy_ratio: float = 0.35,
        max_buy_ratio: float = 0.75,
        top_n: int = 30,
    ) -> List[TokenPair]:
        """
        Get established, high-activity viral memecoins on Solana.

        We deliberately avoid brand-new launches / PumpFun snipes.
        Filters enforce proven liquidity, volume, transaction activity,
        healthy buy/sell balance, and a minimum on-chain age.

        Note: DexScreener's free API has no dedicated trending endpoint,
        so we search broadly and apply strict filters.
        """
        # Search for Solana pairs — broad query to get many candidates
        pairs = await self.search_pairs(f"{chain} USDC")

        now = datetime.now()
        filtered = []
        for pair in pairs:
            if pair.chain_id.lower() != chain.lower():
                continue
            if pair.liquidity_usd < min_liquidity:
                continue
            if pair.volume_24h_usd < min_volume_24h:
                continue

            age = timedelta(hours=max_token_age_hours + 1)
            if pair.pair_created_at:
                age = now - pair.pair_created_at

            if age < timedelta(hours=min_token_age_hours):
                continue  # Too new — skip snipes
            if max_token_age_hours and age > timedelta(hours=max_token_age_hours):
                continue  # Too stale

            total_txns = pair.txns_24h_buy + pair.txns_24h_sell
            if total_txns < min_txns_24h:
                continue

            buy_ratio = pair.txns_24h_buy / total_txns if total_txns > 0 else 0.0
            if buy_ratio < min_buy_ratio or buy_ratio > max_buy_ratio:
                continue  # Unhealthy imbalance

            filtered.append(pair)

        # Virality score: high volume relative to liquidity + strong price momentum
        def _virality_score(pair: TokenPair) -> float:
            vol_liq_ratio = pair.volume_24h_usd / max(pair.liquidity_usd, 1.0)
            momentum = abs(pair.price_change_24h_pct) + abs(pair.price_change_6h_pct)
            activity = pair.txns_24h_buy + pair.txns_24h_sell
            return vol_liq_ratio * momentum * activity

        filtered.sort(key=_virality_score, reverse=True)
        return filtered[:top_n]

    async def close(self):
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
