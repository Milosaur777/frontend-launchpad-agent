"""
Jupiter API client.
Provides swap quotes and swap transaction building.
Docs: https://station.jup.ag/docs/

Note: Jupiter Price/Token APIs are unstable in some environments.
We rely on DexScreener for price data and Jupiter for swap execution.
"""

import asyncio
from typing import Dict, Optional
from dataclasses import dataclass

import aiohttp
import base58

from solders.keypair import Keypair
from solders.transaction import VersionedTransaction


@dataclass
class SwapQuote:
    """Normalized Jupiter swap quote."""

    input_mint: str
    output_mint: str
    in_amount: float
    out_amount: float
    price_impact_pct: float
    slippage_bps: int
    route_plan: list
    raw_quote: Dict


@dataclass
class SwapResult:
    """Result of a swap execution attempt."""

    success: bool
    signature: Optional[str]
    error: Optional[str]
    input_amount: float
    output_amount: float


class JupiterClient:
    """Async client for Jupiter Swap API."""

    BASE_URL = "https://api.jup.ag"

    def __init__(self, rate_limit_delay: float = 0.2):
        """
        Initialize client.

        Args:
            rate_limit_delay: Seconds between requests.
        """
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=20),
                headers={"Accept": "application/json"},
            )
        return self._session

    async def _request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
    ) -> Dict:
        """Make a rate-limited request."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - elapsed)

        session = await self._get_session()
        async with session.request(
            method, url, params=params, json=json_data
        ) as resp:
            self._last_request_time = asyncio.get_event_loop().time()
            resp.raise_for_status()
            return await resp.json()

    async def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: float,
        slippage_bps: int = 500,
        decimals: int = 9,
    ) -> Optional[SwapQuote]:
        """
        Get swap quote from Jupiter.

        Args:
            input_mint: Input token mint address.
            output_mint: Output token mint address.
            amount: Amount of input token (in human units).
            slippage_bps: Slippage tolerance in basis points.
            decimals: Input token decimals.
        """
        url = f"{self.BASE_URL}/swap/v1/quote"
        amount_lamports = int(amount * (10**decimals))

        params = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": str(amount_lamports),
            "slippageBps": slippage_bps,
            "onlyDirectRoutes": "false",
            "asLegacyTransaction": "false",
        }

        try:
            data = await self._request(url, params=params)
            return SwapQuote(
                input_mint=input_mint,
                output_mint=output_mint,
                in_amount=amount,
                out_amount=float(data.get("outAmount", 0)) / (10**6),  # USDC default 6 decimals
                price_impact_pct=float(data.get("priceImpactPct", 0)),
                slippage_bps=slippage_bps,
                route_plan=data.get("routePlan", []),
                raw_quote=data,
            )
        except Exception as e:
            return None

    async def build_swap_transaction(
        self,
        keypair: Keypair,
        quote: SwapQuote,
        wrap_and_unwrap_sol: bool = True,
    ) -> Optional[VersionedTransaction]:
        """
        Build a signed swap transaction from a Jupiter quote.

        Args:
            keypair: Trader's keypair for signing.
            quote: SwapQuote from get_quote().
            wrap_and_unwrap_sol: Auto-wrap/unwrap SOL if needed.
        """
        url = f"{self.BASE_URL}/swap/v1/swap"
        payload = {
            "quoteResponse": quote.raw_quote,
            "userPublicKey": str(keypair.pubkey()),
            "wrapAndUnwrapSol": wrap_and_unwrap_sol,
            "prioritizationFeeLamports": {
                "priorityLevelWithMaxLamports": {
                    "maxLamports": 100000,
                    "priorityLevel": "veryHigh",
                }
            },
        }

        try:
            data = await self._request(url, method="POST", json_data=payload)
            swap_transaction = data.get("swapTransaction")
            if not swap_transaction:
                return None

            raw_tx = base58.b58decode(swap_transaction)
            tx = VersionedTransaction.from_bytes(raw_tx)
            return tx
        except Exception as e:
            return None

    async def close(self):
        """Close aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
