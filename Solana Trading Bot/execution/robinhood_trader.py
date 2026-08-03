"""
Robinhood Chain trade execution via Uniswap V2 Router.
Handles token swaps, slippage, and gas estimation.
"""

import asyncio
import time
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime

import aiohttp

from data.robinhood_chain import (
    RPC_URL,
    UNISWAP_V2_ROUTER,
    WETH_ADDRESS,
    CHAIN_ID,
)


# ── Uniswap V2 Router02 function selectors ──────────────────────────────────
# swapExactETHForTokens(uint amountOutMin, address[] path, address to, uint deadline)
SWAP_EXACT_ETH_FOR_TOKENS_SELECTOR = "0x7ff36ab5"
# swapExactTokensForETH(uint amountIn, uint amountOutMin, address[] path, address to, uint deadline)
SWAP_EXACT_TOKENS_FOR_ETH_SELECTOR = "0x18cbafe5"
# getAmountsOut(uint amountIn, address[] path)
GET_AMOUNTS_OUT_SELECTOR = "0xd06ca61f"


@dataclass
class SwapQuote:
    """A quote for a token swap."""
    token_address: str
    weth_amount: float
    expected_tokens: float
    min_tokens: float
    price_impact_pct: float
    path: list


@dataclass
class SwapResult:
    """Result of a swap execution."""
    success: bool
    tx_hash: Optional[str]
    token_address: str
    weth_spent: float
    tokens_received: float
    error: Optional[str]
    gas_used: int = 0
    paper: bool = False


class RobinhoodTrader:
    """
    Executes trades on Robinhood Chain via Uniswap V2 Router.
    Paper mode simulates trades without on-chain execution.
    """

    def __init__(
        self,
        private_key: Optional[str] = None,
        rpc_url: str = RPC_URL,
        router_address: str = UNISWAP_V2_ROUTER,
        slippage_bps: int = 500,  # 5%
        paper_mode: bool = True,
    ):
        self.rpc_url = rpc_url
        self.router_address = router_address
        self.private_key = private_key
        self.slippage_bps = slippage_bps
        self.paper_mode = paper_mode
        self._session: Optional[aiohttp.ClientSession] = None
        self._wallet_address: Optional[str] = None

        # Paper tracking
        self._paper_balances: Dict[str, float] = {}
        self._paper_weth: float = 10.0  # Start with 10 WETH in paper

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={"Content-Type": "application/json"},
            )
        return self._session

    async def _rpc_call(self, method: str, params: list) -> dict:
        session = await self._get_session()
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        try:
            async with session.post(self.rpc_url, json=payload) as resp:
                data = await resp.json()
                if "error" in data:
                    return {}
                return data.get("result", {})
        except Exception:
            return {}

    async def get_weth_balance(self) -> float:
        """Get WETH balance for the wallet."""
        if self.paper_mode:
            return self._paper_weth

        if not self._wallet_address:
            return 0.0

        # balanceOf(address) selector: 0x70a08231
        data = "0x70a08231" + self._wallet_address[2:].lower().zfill(64)
        result = await self._rpc_call("eth_call", [
            {"to": WETH_ADDRESS, "data": data},
            "latest",
        ])
        if result and result != "0x":
            return int(result, 16) / 1e18
        return 0.0

    async def get_token_balance(self, token_address: str) -> float:
        """Get ERC-20 token balance."""
        if self.paper_mode:
            return self._paper_balances.get(token_address.lower(), 0.0)

        if not self._wallet_address:
            return 0.0

        data = "0x70a08231" + self._wallet_address[2:].lower().zfill(64)
        result = await self._rpc_call("eth_call", [
            {"to": token_address, "data": data},
            "latest",
        ])
        if result and result != "0x":
            return int(result, 16) / 1e18
        return 0.0

    async def get_amounts_out(self, amount_in_wei: int, path: list) -> Optional[list]:
        """Get expected output amounts from Uniswap V2 Router."""
        # encode path
        path_encoded = ""
        for addr in path:
            path_encoded += addr[2:].lower()

        # getAmountsOut(uint256,address[])
        data = GET_AMOUNTS_OUT_SELECTOR
        data += hex(amount_in_wei)[2:].zfill(64)
        # offset to array (32 bytes = 0x20)
        data += "0000000000000000000000000000000000000000000000000000000000000040"
        # array length
        data += hex(len(path))[2:].zfill(64)
        # array elements
        for addr in path:
            data += addr[2:].lower().zfill(64)

        result = await self._rpc_call("eth_call", [
            {"to": self.router_address, "data": "0x" + data},
            "latest",
        ])

        if not result or result == "0x":
            return None

        # Decode result: uint256[] amounts
        result_hex = result[2:]  # remove 0x
        amounts = []
        for i in range(0, len(result_hex), 64):
            chunk = result_hex[i:i + 64]
            if chunk:
                amounts.append(int(chunk, 16))
        return amounts if amounts else None

    async def quote_buy(self, token_address: str, weth_amount: float) -> Optional[SwapQuote]:
        """Get a quote for buying tokens with WETH."""
        weth_wei = int(weth_amount * 1e18)
        path = [WETH_ADDRESS, token_address]

        amounts = await self.get_amounts_out(weth_wei, path)
        if not amounts or len(amounts) < 2:
            return None

        expected = amounts[1] / 1e18
        min_tokens = expected * (1 - self.slippage_bps / 10000)

        return SwapQuote(
            token_address=token_address,
            weth_amount=weth_amount,
            expected_tokens=expected,
            min_tokens=min_tokens,
            price_impact_pct=0.0,
            path=path,
        )

    async def buy_token(
        self,
        token_address: str,
        weth_amount: float,
    ) -> SwapResult:
        """
        Buy tokens with WETH on Uniswap V2.
        In paper mode, simulates the trade.
        """
        if self.paper_mode:
            return await self._paper_buy(token_address, weth_amount)

        # Live execution would go here
        # For now, return error since we need signing
        return SwapResult(
            success=False,
            tx_hash=None,
            token_address=token_address,
            weth_spent=weth_amount,
            tokens_received=0.0,
            error="Live trading not yet implemented — use paper mode",
        )

    async def sell_token(
        self,
        token_address: str,
        token_amount: float,
    ) -> SwapResult:
        """Sell tokens for WETH."""
        if self.paper_mode:
            return await self._paper_sell(token_address, token_amount)

        return SwapResult(
            success=False,
            tx_hash=None,
            token_address=token_address,
            weth_spent=0.0,
            tokens_received=token_amount,
            error="Live trading not yet implemented — use paper mode",
        )

    async def _paper_buy(self, token_address: str, weth_amount: float) -> SwapResult:
        """Simulate a buy in paper mode."""
        if weth_amount > self._paper_weth:
            return SwapResult(
                success=False,
                tx_hash=None,
                token_address=token_address,
                weth_spent=weth_amount,
                tokens_received=0.0,
                error="Insufficient paper WETH",
                paper=True,
            )

        # Simulate: get a fake amount of tokens
        # In production, this would use a price oracle
        # For now, assume 1 WETH = some amount of tokens
        quote = await self.quote_buy(token_address, weth_amount)
        tokens_received = quote.expected_tokens if quote else weth_amount * 1_000_000

        self._paper_weth -= weth_amount
        addr_lower = token_address.lower()
        self._paper_balances[addr_lower] = self._paper_balances.get(addr_lower, 0.0) + tokens_received

        return SwapResult(
            success=True,
            tx_hash="PAPER_TX_" + str(int(time.time() * 1000)),
            token_address=token_address,
            weth_spent=weth_amount,
            tokens_received=tokens_received,
            error=None,
            paper=True,
        )

    async def _paper_sell(self, token_address: str, token_amount: float) -> SwapResult:
        """Simulate a sell in paper mode."""
        addr_lower = token_address.lower()
        current = self._paper_balances.get(addr_lower, 0.0)
        if token_amount > current:
            return SwapResult(
                success=False,
                tx_hash=None,
                token_address=token_address,
                weth_spent=0.0,
                tokens_received=token_amount,
                error="Insufficient paper tokens",
                paper=True,
            )

        # Simulate WETH received
        weth_received = token_amount * 0.000001  # Rough estimate
        self._paper_balances[addr_lower] = current - token_amount
        self._paper_weth += weth_received

        return SwapResult(
            success=True,
            tx_hash="PAPER_TX_" + str(int(time.time() * 1000)),
            token_address=token_address,
            weth_spent=weth_received,
            tokens_received=token_amount,
            error=None,
            paper=True,
        )

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
