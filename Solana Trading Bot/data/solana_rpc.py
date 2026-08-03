"""
Solana RPC client wrapper with fallback endpoints.
"""

import asyncio
from typing import Any, Dict, Optional, List

import aiohttp
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed

from config.settings import Config


class SolanaRPCClient:
    """Async Solana RPC client with multiple fallback endpoints."""

    FALLBACK_ENDPOINTS = [
        "https://api.mainnet-beta.solana.com",
        "https://solana-api.projectserum.com",
        "https://rpc.ankr.com/solana",
    ]

    def __init__(self, primary_url: Optional[str] = None):
        self.primary_url = primary_url or Config.PRIMARY_RPC_URL
        self.endpoints = [self.primary_url] + [
            url for url in self.FALLBACK_ENDPOINTS if url != self.primary_url
        ]
        self.clients = [AsyncClient(url, commitment=Confirmed) for url in self.endpoints]
        self.current_index = 0

    @property
    def client(self) -> AsyncClient:
        """Return current active RPC client."""
        return self.clients[self.current_index]

    async def _try_request(self, method_name: str, *args, **kwargs) -> Any:
        """Try request across all endpoints until one succeeds."""
        last_error = None
        for i, client in enumerate(self.clients):
            try:
                method = getattr(client, method_name)
                result = await method(*args, **kwargs)
                if i != self.current_index:
                    self.current_index = i
                return result
            except Exception as e:
                last_error = e
                continue
        raise RuntimeError(f"All RPC endpoints failed for {method_name}: {last_error}")

    async def get_slot(self) -> int:
        """Get current slot."""
        resp = await self._try_request("get_slot")
        return resp.value

    async def get_balance(self, pubkey: str) -> float:
        """Get SOL balance for a public key."""
        from solders.pubkey import Pubkey

        resp = await self._try_request("get_balance", Pubkey.from_string(pubkey))
        return resp.value / 1_000_000_000

    async def get_token_accounts_by_owner(self, owner: str, mint: str) -> List[Dict]:
        """Get token accounts for owner filtered by mint."""
        resp = await self._try_request(
            "get_token_accounts_by_owner_json_parsed",
            owner,
            {"mint": mint},
        )
        return [acc.to_json() for acc in resp.value] if resp.value else []

    async def get_signatures_for_address(
        self,
        address: str,
        limit: int = 10,
    ) -> List[Dict]:
        """Get recent transaction signatures for an address."""
        from solders.pubkey import Pubkey

        resp = await self._try_request(
            "get_signatures_for_address",
            Pubkey.from_string(address),
            limit=limit,
        )
        return resp.value

    async def get_transaction(self, signature: str) -> Optional[Dict]:
        """Get transaction details by signature."""
        resp = await self._try_request(
            "get_transaction",
            signature,
            encoding="jsonParsed",
        )
        return resp.value

    async def is_healthy(self) -> bool:
        """Check if RPC endpoint is healthy."""
        try:
            await asyncio.wait_for(self.get_slot(), timeout=5.0)
            return True
        except Exception:
            return False

    async def close(self):
        """Close all RPC connections."""
        await asyncio.gather(*[c.close() for c in self.clients])
