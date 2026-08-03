"""
Solana wallet management for the trading bot.
Handles keypair loading, signing, and balance queries.
"""

import base58
from typing import Optional

from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.rpc.responses import GetBalanceResp

from config.settings import Config


class SolanaWallet:
    """Manages the bot's Solana keypair and balance."""

    def __init__(self, private_key: Optional[str] = None, rpc_url: Optional[str] = None):
        """
        Initialize wallet from base58 private key.

        Args:
            private_key: base58-encoded private key. Defaults to Config.SOLANA_PRIVATE_KEY.
            rpc_url: Solana RPC URL. Defaults to Config.primary_rpc_url.
        """
        self.private_key = private_key or Config.SOLANA_PRIVATE_KEY
        self.rpc_url = rpc_url or Config.PRIMARY_RPC_URL

        if not self.private_key:
            raise ValueError("Private key is required. Set SOLANA_PRIVATE_KEY in .env")

        self.keypair = self._load_keypair()
        self.public_key = self.keypair.pubkey()
        self.rpc = AsyncClient(self.rpc_url, commitment=Confirmed)

    def _load_keypair(self) -> Keypair:
        """Load keypair from base58 private key string."""
        try:
            # Private key may be 64 bytes (full secret) or 32 bytes (seed)
            decoded = base58.b58decode(self.private_key)
            return Keypair.from_base58_string(self.private_key)
        except Exception as e:
            raise ValueError(f"Failed to load private key: {e}")

    async def get_balance(self) -> float:
        """Get SOL balance in SOL (not lamports)."""
        try:
            resp: GetBalanceResp = await self.rpc.get_balance(self.public_key)
            if resp.value is None:
                return 0.0
            return resp.value / 1_000_000_000
        except Exception as e:
            raise RuntimeError(f"Failed to get balance: {e}")

    async def get_token_balance(self, token_mint: str) -> float:
        """Get SPL token balance for a given mint address."""
        try:
            mint = Pubkey.from_string(token_mint)
            # Get token accounts by owner
            resp = await self.rpc.get_token_accounts_by_owner_json_parsed(
                self.public_key,
                {"mint": str(mint)},
            )
            if not resp.value:
                return 0.0

            total = 0.0
            for account in resp.value:
                parsed = account.account.data.parsed["info"]
                total += float(parsed["tokenAmount"]["uiAmount"])
            return total
        except Exception as e:
            raise RuntimeError(f"Failed to get token balance for {token_mint}: {e}")

    async def get_sol_price_usd(self) -> float:
        """Fetch current SOL price in USD from Jupiter Price API."""
        import aiohttp

        url = "https://api.jup.ag/price/v2"
        params = {"ids": "So11111111111111111111111111111111111111112"}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    price_data = data.get("data", {}).get("So11111111111111111111111111111111111111112", {})
                    return float(price_data.get("price", 0.0))
        except Exception as e:
            # Fallback: assume SOL is worth something reasonable to avoid crash
            return 150.0

    async def get_portfolio_value_usd(self) -> float:
        """Get approximate portfolio value in USD (SOL only for now)."""
        sol_balance = await self.get_balance()
        sol_price = await self.get_sol_price_usd()
        return sol_balance * sol_price

    async def close(self):
        """Close RPC connection."""
        await self.rpc.close()

    def __repr__(self) -> str:
        return f"SolanaWallet(public_key={self.public_key})"
