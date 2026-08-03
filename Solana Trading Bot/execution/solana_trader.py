"""
Solana trade execution via Jupiter aggregator.
Handles swap quotes, transaction building, signing, and submission.
"""

from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime

from solders.transaction import VersionedTransaction
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.rpc.async_api import TxOptsModel

from data.jupiter import JupiterClient, SwapQuote
from data.dexscreener import DexScreenerClient
from execution.wallet import SolanaWallet
from config.settings import Config


@dataclass
class TradeResult:
    """Result of a trade execution."""

    success: bool
    side: str  # "buy" or "sell"
    token_address: str
    amount: float
    price: float
    signature: Optional[str]
    error: Optional[str]
    paper_trade: bool


class SolanaTrader:
    """Executes trades on Solana via Jupiter."""

    SOL_MINT = "So11111111111111111111111111111111111111112"
    USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"

    def __init__(
        self,
        wallet: Optional[SolanaWallet] = None,
        jupiter: Optional[JupiterClient] = None,
        rpc_client: Optional[AsyncClient] = None,
        paper_mode: Optional[bool] = None,
        price_feed=None,
    ):
        self.wallet = wallet or SolanaWallet()
        self.jupiter = jupiter or JupiterClient()
        self.rpc = rpc_client or AsyncClient(Config.PRIMARY_RPC_URL, commitment=Confirmed)
        self.paper_mode = paper_mode if paper_mode is not None else not Config.LIVE_MODE
        self._price_feed = price_feed

    async def get_token_price_usd(self, token_address: str) -> float:
        """Get token price in USD via Jupiter quote (1 token -> USDC)."""
        if token_address == self.USDC_MINT:
            return 1.0

        quote = await self.jupiter.get_quote(
            input_mint=token_address,
            output_mint=self.USDC_MINT,
            amount=1.0,
            decimals=9,  # Assume 9 decimals; should be looked up in production
            slippage_bps=1000,
        )
        if quote:
            return quote.out_amount
        return 0.0

    async def buy_token(
        self,
        token_address: str,
        sol_amount: float,
        slippage_bps: Optional[int] = None,
    ) -> TradeResult:
        """
        Buy a token with SOL.

        Args:
            token_address: Token mint address to buy.
            sol_amount: Amount of SOL to spend.
            slippage_bps: Slippage tolerance in basis points.

        Returns:
            TradeResult.
        """
        slippage_bps = slippage_bps or Config.MAX_SLIPPAGE_BPS

        if self.paper_mode:
            return await self._paper_buy(token_address, sol_amount)

        try:
            quote = await self.jupiter.get_quote(
                input_mint=self.SOL_MINT,
                output_mint=token_address,
                amount=sol_amount,
                decimals=9,
                slippage_bps=slippage_bps,
            )

            if not quote:
                return TradeResult(
                    success=False,
                    side="buy",
                    token_address=token_address,
                    amount=sol_amount,
                    price=0.0,
                    signature=None,
                    error="Could not get Jupiter quote",
                    paper_trade=False,
                )

            tx = await self.jupiter.build_swap_transaction(
                keypair=self.wallet.keypair,
                quote=quote,
            )

            if not tx:
                return TradeResult(
                    success=False,
                    side="buy",
                    token_address=token_address,
                    amount=sol_amount,
                    price=0.0,
                    signature=None,
                    error="Could not build swap transaction",
                    paper_trade=False,
                )

            # Sign and send transaction
            signed_tx = self._sign_versioned_transaction(tx)
            signature = await self._send_transaction(signed_tx)

            if signature:
                return TradeResult(
                    success=True,
                    side="buy",
                    token_address=token_address,
                    amount=sol_amount,
                    price=sol_amount / max(quote.out_amount, 1e-9),
                    signature=signature,
                    error=None,
                    paper_trade=False,
                )
            else:
                return TradeResult(
                    success=False,
                    side="buy",
                    token_address=token_address,
                    amount=sol_amount,
                    price=0.0,
                    signature=None,
                    error="Transaction submission failed",
                    paper_trade=False,
                )

        except Exception as e:
            return TradeResult(
                success=False,
                side="buy",
                token_address=token_address,
                amount=sol_amount,
                price=0.0,
                signature=None,
                error=str(e),
                paper_trade=False,
            )

    async def sell_token(
        self,
        token_address: str,
        token_amount: float,
        token_decimals: int = 9,
        slippage_bps: Optional[int] = None,
    ) -> TradeResult:
        """
        Sell a token for SOL.

        Args:
            token_address: Token mint address to sell.
            token_amount: Amount of token to sell.
            token_decimals: Token decimals.
            slippage_bps: Slippage tolerance.

        Returns:
            TradeResult.
        """
        slippage_bps = slippage_bps or Config.MAX_SLIPPAGE_BPS

        if self.paper_mode:
            return await self._paper_sell(token_address, token_amount)

        try:
            quote = await self.jupiter.get_quote(
                input_mint=token_address,
                output_mint=self.SOL_MINT,
                amount=token_amount,
                decimals=token_decimals,
                slippage_bps=slippage_bps,
            )

            if not quote:
                return TradeResult(
                    success=False,
                    side="sell",
                    token_address=token_address,
                    amount=token_amount,
                    price=0.0,
                    signature=None,
                    error="Could not get Jupiter quote",
                    paper_trade=False,
                )

            tx = await self.jupiter.build_swap_transaction(
                keypair=self.wallet.keypair,
                quote=quote,
            )

            if not tx:
                return TradeResult(
                    success=False,
                    side="sell",
                    token_address=token_address,
                    amount=token_amount,
                    price=0.0,
                    signature=None,
                    error="Could not build swap transaction",
                    paper_trade=False,
                )

            signed_tx = self._sign_versioned_transaction(tx)
            signature = await self._send_transaction(signed_tx)

            if signature:
                return TradeResult(
                    success=True,
                    side="sell",
                    token_address=token_address,
                    amount=token_amount,
                    price=quote.out_amount / max(token_amount, 1e-9),
                    signature=signature,
                    error=None,
                    paper_trade=False,
                )
            else:
                return TradeResult(
                    success=False,
                    side="sell",
                    token_address=token_address,
                    amount=token_amount,
                    price=0.0,
                    signature=None,
                    error="Transaction submission failed",
                    paper_trade=False,
                )

        except Exception as e:
            return TradeResult(
                success=False,
                side="sell",
                token_address=token_address,
                amount=token_amount,
                price=0.0,
                signature=None,
                error=str(e),
                paper_trade=False,
            )

    def _sign_versioned_transaction(self, tx: VersionedTransaction) -> VersionedTransaction:
        """Sign a versioned transaction with the wallet keypair."""
        # Get message bytes
        message = tx.message
        # Sign message with keypair
        signature = self.wallet.keypair.sign_message(bytes(message))
        # Create new transaction with signature
        signatures = [signature]
        return VersionedTransaction(message, signatures)

    async def _send_transaction(self, tx: VersionedTransaction) -> Optional[str]:
        """Send a signed transaction to the network."""
        try:
            serialized = bytes(tx)
            resp = await self.rpc.send_raw_transaction(
                serialized,
                opts=TxOptsModel(skip_preflight=False, preflight_commitment=Confirmed),
            )
            return str(resp.value) if resp.value else None
        except Exception as e:
            return None

    async def _paper_buy(self, token_address: str, sol_amount: float) -> TradeResult:
        """Simulate a buy in paper trading mode."""
        price = await self._get_paper_price(token_address)
        return TradeResult(
            success=True,
            side="buy",
            token_address=token_address,
            amount=sol_amount,
            price=price,
            signature="PAPER_TRADE",
            error=None,
            paper_trade=True,
        )

    async def _paper_sell(self, token_address: str, token_amount: float) -> TradeResult:
        """Simulate a sell in paper trading mode."""
        price = await self._get_paper_price(token_address)
        return TradeResult(
            success=True,
            side="sell",
            token_address=token_address,
            amount=token_amount,
            price=price,
            signature="PAPER_TRADE",
            error=None,
            paper_trade=True,
        )

    async def _get_paper_price(self, token_address: str) -> float:
        """Get price for paper trading — use DexScreener via price_feed if available,
        fall back to Jupiter (which may be inaccurate due to decimal assumptions)."""
        if self._price_feed:
            latest = self._price_feed.get_latest(token_address)
            if latest and latest.price_usd > 0:
                return latest.price_usd
        return await self.get_token_price_usd(token_address)

    async def close(self):
        """Close connections."""
        await self.jupiter.close()
        await self.rpc.close()
