"""
Watchlist mode test.
Run with: python tests/test_watchlist.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import Config


def test_fixed_watchlist_config():
    print("\n[Watchlist] Verifying fixed watchlist config...")
    assert isinstance(Config.FIXED_WATCHLIST, dict)
    assert len(Config.FIXED_WATCHLIST) >= 3
    assert Config.WATCHLIST_MODE in ("discovery", "fixed")

    # Verify known tokens have non-empty addresses
    for symbol, address in Config.FIXED_WATCHLIST.items():
        assert len(address) > 30, f"Invalid address for {symbol}"

    print(f"  [OK] Fixed watchlist has {len(Config.FIXED_WATCHLIST)} tokens")
    print(f"  [OK] Current mode: {Config.WATCHLIST_MODE}")


if __name__ == "__main__":
    print("=" * 60)
    print("PolyCryptoAlpha Watchlist Test")
    print("=" * 60)
    test_fixed_watchlist_config()
    print("\n" + "=" * 60)
    print("Watchlist test complete")
    print("=" * 60)
