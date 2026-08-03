"""
Robinhood Chain Sniper Bot — auto-detects new token launches and buys small amounts.
Designed for Day-1 readiness on Robinhood Chain meme coin launches.
"""

import asyncio
import time
from typing import Optional, Dict, List, Callable, Awaitable
from dataclasses import dataclass, field
from datetime import datetime

from data.robinhood_chain import RobinhoodChainClient, NewToken, TokenInfo
from execution.robinhood_trader import RobinhoodTrader, SwapResult
from monitoring.logger import log


@dataclass
class SnipedToken:
    """A token that was sniped (bought)."""
    address: str
    symbol: str
    name: str
    pair_address: str
    buy_time: datetime
    weth_spent: float
    tokens_received: float
    buy_price_usd: float = 0.0
    current_price_usd: float = 0.0
    pnl_pct: float = 0.0
    status: str = "holding"  # holding, sold, rugged


class SniperBot:
    """
    Monitors Robinhood Chain for new Uniswap V2 pair creations
    and automatically buys small amounts of each new token.

    Strategy:
    - Poll Uniswap V2 Factory for PairCreated events
    - When a new WETH-paired token is detected, buy $1 worth
    - Track positions for manual or auto sell
    """

    def __init__(
        self,
        buy_amount_weth: float = 0.0005,  # ~$1 at ~$2000/ETH
        max_concurrent_buys: int = 3,
        buy_delay_seconds: float = 0.5,
        auto_sell_pnl_pct: float = 100.0,  # Auto-sell at 2x
        auto_stop_loss_pct: float = -50.0,  # Stop loss at -50%
        paper_mode: bool = True,
    ):
        self.buy_amount_weth = buy_amount_weth
        self.max_concurrent_buys = max_concurrent_buys
        self.buy_delay_seconds = buy_delay_seconds
        self.auto_sell_pnl_pct = auto_sell_pnl_pct
        self.auto_stop_loss_pct = auto_stop_loss_pct
        self.paper_mode = paper_mode

        # Components
        self.chain_client = RobinhoodChainClient()
        self.trader = RobinhoodTrader(paper_mode=paper_mode)

        # State
        self.sniped_tokens: Dict[str, SnipedToken] = {}
        self._running = False
        self._active_buys = 0

        # Stats
        self.total_sniped = 0
        self.total_weth_spent = 0.0
        self.successful_buys = 0
        self.failed_buys = 0

        # Callbacks
        self._on_new_token: Optional[Callable[[NewToken], Awaitable[None]]] = None
        self._on_buy: Optional[Callable[[SnipedToken], Awaitable[None]]] = None
        self._on_sell: Optional[Callable[[SnipedToken, SwapResult], Awaitable[None]]] = None
        self._on_error: Optional[Callable[[str], Awaitable[None]]] = None

    def on_new_token(self, callback: Callable[[NewToken], Awaitable[None]]):
        """Register callback for new token detection."""
        self._on_new_token = callback

    def on_buy(self, callback: Callable[[SnipedToken], Awaitable[None]]):
        """Register callback for successful buy."""
        self._on_buy = callback

    def on_sell(self, callback: Callable[[SnipedToken, SwapResult], Awaitable[None]]):
        """Register callback for sell."""
        self._on_sell = callback

    def on_error(self, callback: Callable[[str], Awaitable[None]]):
        """Register callback for errors."""
        self._on_error = callback

    async def start(self):
        """Start the sniper bot."""
        self._running = True
        log.info(
            f"[Sniper] Starting — buy={self.buy_amount_weth} WETH, "
            f"paper={self.paper_mode}, max_concurrent={self.max_concurrent_buys}"
        )

        # Run the detection loop
        await self.chain_client.poll_new_launches(self._handle_new_token)

    async def _handle_new_token(self, token: NewToken):
        """Handle a newly detected token."""
        log.info(
            f"[Sniper] NEW TOKEN: {token.address[:10]}... "
            f"pair={token.pair_address[:10]}... "
            f"weth_paired={token.weth_paired}"
        )

        if self._on_new_token:
            await self._on_new_token(token)

        # Only buy WETH-paired tokens (most likely meme coins)
        if not token.weth_paired:
            log.info(f"[Sniper] Skipping non-WETH pair: {token.address[:10]}...")
            return

        # Check if already sniped
        if token.address in self.sniped_tokens:
            log.info(f"[Sniper] Already sniped: {token.address[:10]}...")
            return

        # Rate limit concurrent buys
        if self._active_buys >= self.max_concurrent_buys:
            log.warning(f"[Sniper] Max concurrent buys reached, skipping {token.address[:10]}...")
            return

        # Get token info
        token_info = await self.chain_client.get_token_info(token.address)
        symbol = token_info.symbol if token_info else "???"
        name = token_info.name if token_info else "Unknown"

        log.info(f"[Sniper] Token info: {symbol} ({name})")

        # Execute buy
        await self._execute_buy(token, symbol, name)

        # Small delay between buys to avoid gas wars
        await asyncio.sleep(self.buy_delay_seconds)

    async def _execute_buy(self, token: NewToken, symbol: str, name: str):
        """Execute a buy for a detected token."""
        self._active_buys += 1
        try:
            log.info(
                f"[Sniper] BUYING {symbol} — "
                f"{self.buy_amount_weth} WETH → {token.address[:10]}..."
            )

            result = await self.trader.buy_token(
                token.address,
                self.buy_amount_weth,
            )

            if result.success:
                sniped = SnipedToken(
                    address=token.address,
                    symbol=symbol,
                    name=name,
                    pair_address=token.pair_address,
                    buy_time=datetime.now(),
                    weth_spent=result.weth_spent,
                    tokens_received=result.tokens_received,
                    status="holding",
                )
                self.sniped_tokens[token.address] = sniped
                self.total_sniped += 1
                self.total_weth_spent += result.weth_spent
                self.successful_buys += 1

                log.info(
                    f"[Sniper] ✓ BOUGHT {symbol}: "
                    f"{result.tokens_received:,.0f} tokens for {result.weth_spent:.6f} WETH"
                )

                if self._on_buy:
                    await self._on_buy(sniped)
            else:
                self.failed_buys += 1
                log.warning(f"[Sniper] ✗ FAILED to buy {symbol}: {result.error}")

                if self._on_error:
                    await self._on_error(f"Buy failed for {symbol}: {result.error}")

        except Exception as e:
            self.failed_buys += 1
            log.error(f"[Sniper] Error buying {symbol}: {e}")
            if self._on_error:
                await self._on_error(f"Exception buying {symbol}: {e}")
        finally:
            self._active_buys -= 1

    async def check_positions(self):
        """Check all sniped positions for take-profit or stop-loss."""
        for addr, sniped in list(self.sniped_tokens.items()):
            if sniped.status != "holding":
                continue

            # Get current price (would need price feed integration)
            # For now, just track P&L based on held tokens
            pass

    def get_stats(self) -> dict:
        """Get sniper bot statistics."""
        return {
            "total_sniped": self.total_sniped,
            "total_weth_spent": self.total_weth_spent,
            "successful_buys": self.successful_buys,
            "failed_buys": self.failed_buys,
            "active_positions": sum(
                1 for t in self.sniped_tokens.values() if t.status == "holding"
            ),
            "paper_mode": self.paper_mode,
        }

    def stop(self):
        """Stop the sniper bot."""
        self._running = False
        self.chain_client.stop()
        log.info("[Sniper] Stopped")

    async def close(self):
        """Clean up resources."""
        self.stop()
        await self.chain_client.close()
        await self.trader.close()
