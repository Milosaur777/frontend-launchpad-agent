"""
Robinhood Chain listener — detects new token launches via Uniswap V2 PairCreated events.
Uses EVM JSON-RPC (websockets or polling) on Robinhood Chain (chain ID 4663).
"""

import asyncio
import json
import time
from typing import Optional, Callable, List, Dict, Awaitable
from dataclasses import dataclass, field
from datetime import datetime

import aiohttp


# ── Robinhood Chain constants ────────────────────────────────────────────────
CHAIN_ID = 4663
RPC_URL = "https://rpc.mainnet.chain.robinhood.com"
WSS_URL = "wss://rpc.mainnet.chain.robinhood.com/ws"

# Uniswap V2 on Robinhood Chain
UNISWAP_V2_FACTORY = "0x8bcEaA40B9AcdfAedF85AdF4FF01F5Ad6517937f"
UNISWAP_V2_ROUTER = "0x89e5DB8B5aA49aA85AC63f691524311AEB649eba"
WETH_ADDRESS = "0x4200000000000000000000000000000000000006"  # WETH on Robinhood Chain

# ERC-20 minimal ABI for balance/transfer checks
ERC20_ABI = [
    "function name() view returns (string)",
    "function symbol() view returns (string)",
    "function decimals() view returns (uint8)",
    "function totalSupply() view returns (uint256)",
    "function balanceOf(address) view returns (uint256)",
]

# Uniswap V2 Factory ABI (just the event we care about)
FACTORY_ABI = [
    "event PairCreated(address indexed token0, address indexed token1, address pair, uint)",
]

PAIR_ABI = [
    "function getReserves() view returns (uint112, uint112, uint32)",
    "function token0() view returns (address)",
    "function token1() view returns (address)",
]

# PairCreated event topic
PAIR_CREATED_TOPIC = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"


@dataclass
class NewToken:
    """A newly detected token on Robinhood Chain."""
    address: str
    pair_address: str
    token0: str
    token1: str
    timestamp: datetime
    weth_paired: bool  # True if paired with WETH
    block_number: int = 0


@dataclass
class TokenInfo:
    """Basic token info from on-chain read."""
    address: str
    name: str
    symbol: str
    decimals: int
    total_supply: int


class RobinhoodChainClient:
    """
    Detects new token launches on Robinhood Chain by:
    1. Polling for PairCreated events on Uniswap V2 Factory
    2. Optionally using WebSocket subscriptions
    """

    def __init__(
        self,
        rpc_url: str = RPC_URL,
        poll_interval: float = 2.0,
    ):
        self.rpc_url = rpc_url
        self.wss_url = WSS_URL
        self.poll_interval = poll_interval
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_block: int = 0
        self._seen_pairs: set = set()
        self._running = False

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                headers={"Content-Type": "application/json"},
            )
        return self._session

    async def _rpc_call(self, method: str, params: list) -> dict:
        """Make a JSON-RPC call."""
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

    async def get_block_number(self) -> int:
        """Get latest block number."""
        result = await self._rpc_call("eth_blockNumber", [])
        if result:
            return int(result, 16)
        return 0

    async def get_logs(
        self,
        from_block: int,
        to_block: str = "latest",
        address: str = UNISWAP_V2_FACTORY,
        topics: Optional[List[str]] = None,
    ) -> list:
        """Get event logs."""
        params = {
            "fromBlock": hex(from_block),
            "toBlock": to_block,
            "address": address,
        }
        if topics:
            params["topics"] = topics
        return await self._rpc_call("eth_getLogs", [params]) or []

    async def detect_new_pairs(self) -> List[NewToken]:
        """
        Poll for new PairCreated events since last check.
        Returns list of newly detected tokens.
        """
        current_block = await self.get_block_number()
        if current_block <= 0:
            return []

        if self._last_block == 0:
            self._last_block = current_block - 10  # Look back a few blocks on first run

        logs = await self.get_logs(
            from_block=self._last_block,
            topics=[PAIR_CREATED_TOPIC],
        )

        new_tokens = []
        for log_entry in logs if isinstance(logs, list) else []:
            tx_hash = log_entry.get("transactionHash", "")
            pair_addr = log_entry.get("address", "")
            block_num = int(log_entry.get("blockNumber", "0x0"), 16)

            if pair_addr in self._seen_pairs:
                continue
            self._seen_pairs.add(pair_addr)

            # Parse PairCreated event data
            # event PairCreated(address indexed token0, address indexed token1, address pair, uint)
            topics = log_entry.get("topics", [])
            data = log_entry.get("data", "0x")

            if len(topics) >= 3:
                token0 = "0x" + topics[1][-40:]
                token1 = "0x" + topics[2][-40:]
            else:
                continue

            # Check if either token is WETH
            weth_paired = (
                token0.lower() == WETH_ADDRESS.lower()
                or token1.lower() == WETH_ADDRESS.lower()
            )

            new_token = NewToken(
                address=token0 if token1.lower() == WETH_ADDRESS.lower() else token1,
                pair_address=pair_addr,
                token0=token0,
                token1=token1,
                timestamp=datetime.now(),
                weth_paired=weth_paired,
                block_number=block_num,
            )
            new_tokens.append(new_token)

        self._last_block = current_block
        return new_tokens

    async def get_token_info(self, token_address: str) -> Optional[TokenInfo]:
        """Get basic token info via eth_call."""
        # name()
        name_data = await self._rpc_call("eth_call", [
            {"to": token_address, "data": "0x06fdde03"},
            "latest",
        ])
        name = self._decode_string(name_data) if name_data else "Unknown"

        # symbol()
        symbol_data = await self._rpc_call("eth_call", [
            {"to": token_address, "data": "0x95d89b41"},
            "latest",
        ])
        symbol = self._decode_string(symbol_data) if symbol_data else "???"

        # decimals()
        decimals_data = await self._rpc_call("eth_call", [
            {"to": token_address, "data": "0x313ce567"},
            "latest",
        ])
        decimals = int(decimals_data, 16) if decimals_data and decimals_data != "0x" else 18

        return TokenInfo(
            address=token_address,
            name=name,
            symbol=symbol,
            decimals=decimals,
            total_supply=0,
        )

    def _decode_string(self, hex_data: str) -> str:
        """Decode a Solidity string from hex data."""
        if not hex_data or hex_data == "0x":
            return ""
        try:
            # Remove 0x prefix
            data = hex_data[2:]
            # Skip offset (first 32 bytes)
            if len(data) >= 128:
                data = data[64:]
            # Read length
            length = int(data[:64], 16) * 2
            # Read string bytes
            string_hex = data[64:64 + length]
            return bytes.fromhex(string_hex).decode("utf-8", errors="replace")
        except Exception:
            return ""

    async def poll_new_launches(
        self,
        callback: Callable[[NewToken], Awaitable[None]],
    ):
        """
        Continuously poll for new token launches and call callback.
        Run this in an async loop.
        """
        self._running = True
        while self._running:
            try:
                new_tokens = await self.detect_new_pairs()
                for token in new_tokens:
                    try:
                        await callback(token)
                    except Exception as e:
                        print(f"[Robinhood] Error processing {token.address}: {e}")
            except Exception as e:
                print(f"[Robinhood] Poll error: {e}")

            await asyncio.sleep(self.poll_interval)

    def stop(self):
        """Stop polling."""
        self._running = False

    async def close(self):
        """Close session."""
        self.stop()
        if self._session and not self._session.closed:
            await self._session.close()
