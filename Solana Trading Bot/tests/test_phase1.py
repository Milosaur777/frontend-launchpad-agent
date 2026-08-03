"""
Phase 1 tests: Foundation (config, data clients, wallet, RPC).
Run with: python tests/test_phase1.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from solders.keypair import Keypair

from config.settings import Config
from data.dexscreener import DexScreenerClient
from data.jupiter import JupiterClient
from data.solana_rpc import SolanaRPCClient
from execution.wallet import SolanaWallet


async def test_config():
    print("\n[1/5] Testing Config...")
    try:
        Config.validate()
        print(f"  [OK] Config valid")
        print(f"  - RPC: {Config.PRIMARY_RPC_URL}")
        print(f"  - Live mode: {Config.LIVE_MODE}")
        print(f"  - Capital: ${Config.INITIAL_CAPITAL}")
        print(f"  - Timeframe: {Config.TIMEFRAME}")
    except ValueError as e:
        print(f"  [WARN] Config validation failed (expected if no private key set):")
        print(f"    {e}")


async def test_dexscreener():
    print("\n[2/5] Testing DexScreener API...")
    client = DexScreenerClient()
    try:
        # Search for SOL/USDC pairs
        pairs = await client.search_pairs("SOL USDC")
        sol_pairs = [p for p in pairs if p.chain_id.lower() == "solana"]
        if sol_pairs:
            top = sol_pairs[0]
            print(f"  [OK] Found {len(sol_pairs)} SOL pairs on Solana")
            print(f"  - Top pair: {top.base_token_symbol}/{top.quote_token_symbol}")
            print(f"  - Price: ${top.price_usd:.4f}")
            print(f"  - Liquidity: ${top.liquidity_usd:,.2f}")
            print(f"  - Volume 24h: ${top.volume_24h_usd:,.2f}")
        else:
            print("  [FAIL] No SOL pairs found")
    except Exception as e:
        print(f"  [FAIL] DexScreener error: {e}")
    finally:
        await client.close()


async def test_jupiter():
    print("\n[3/5] Testing Jupiter Swap Quote API...")
    client = JupiterClient()
    try:
        # SOL -> USDC quote for 0.1 SOL
        sol = "So11111111111111111111111111111111111111112"
        usdc = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        quote = await client.get_quote(sol, usdc, amount=0.1, decimals=9)
        if quote:
            print(f"  [OK] Swap quote received")
            print(f"  - Input: {quote.in_amount} SOL")
            print(f"  - Output: {quote.out_amount:.4f} USDC")
            print(f"  - Price impact: {quote.price_impact_pct:.4f}%")
        else:
            print("  [FAIL] Could not fetch swap quote")
    except Exception as e:
        print(f"  [FAIL] Jupiter error: {e}")
    finally:
        await client.close()


async def test_rpc():
    print("\n[4/5] Testing Solana RPC...")
    client = SolanaRPCClient()
    try:
        healthy = await client.is_healthy()
        if healthy:
            slot = await client.get_slot()
            print(f"  [OK] RPC healthy, current slot: {slot}")
        else:
            print("  [FAIL] RPC not healthy")
    except Exception as e:
        print(f"  [FAIL] RPC error: {e}")
    finally:
        await client.close()


async def test_wallet():
    print("\n[5/5] Testing Wallet...")
    try:
        # Generate a random test keypair
        import base58
        keypair = Keypair()
        print(f"  Generated test keypair: {keypair.pubkey()}")

        # Use the generated key (note: this is a test wallet, no real funds)
        private_key_b58 = base58.b58encode(bytes(keypair)).decode("utf-8")
        wallet = SolanaWallet(private_key=private_key_b58)
        print(f"  [OK] Wallet loaded: {wallet.public_key}")

        balance = await wallet.get_balance()
        print(f"  - Balance: {balance:.6f} SOL")

        await wallet.close()
    except Exception as e:
        print(f"  [FAIL] Wallet error: {e}")


async def main():
    print("=" * 60)
    print("PolyCryptoAlpha Phase 1 Tests")
    print("=" * 60)

    await test_config()
    await test_dexscreener()
    await test_jupiter()
    await test_rpc()
    await test_wallet()

    print("\n" + "=" * 60)
    print("Phase 1 tests complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
