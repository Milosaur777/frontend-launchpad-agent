"""
Phase 2 tests: Feature engineering, regime detection, token scoring.
Run with: python tests/test_phase2.py
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.price_feed import PriceSnapshot
from ml.features import FeatureEngineer
from ml.regime import RegimeDetector, Regime
from ml.token_scorer import TokenScorer


def generate_synthetic_snapshots(n: int = 200, token_address: str = "TEST") -> list:
    """Generate synthetic price snapshots for testing."""
    snapshots = []
    price = 0.001
    base_time = datetime.now() - timedelta(minutes=n * 5)

    for i in range(n):
        # Random walk with some momentum
        change = random.gauss(0.001, 0.02)
        price = price * (1 + change)
        price = max(price, 0.0001)

        snapshots.append(
            PriceSnapshot(
                token_address=token_address,
                symbol="TEST",
                price_usd=price,
                liquidity_usd=50_000 + i * 100,
                volume_24h_usd=20_000 + random.gauss(0, 5_000),
                volume_1h_usd=2_000 + random.gauss(0, 500),
                price_change_1h_pct=random.gauss(0, 5),
                price_change_24h_pct=random.gauss(0, 20),
                txns_24h_buy=random.randint(50, 200),
                txns_24h_sell=random.randint(50, 200),
                fdv=price * 1_000_000_000,
                market_cap=price * 500_000_000,
                timestamp=base_time + timedelta(minutes=i * 5),
                source="test",
                pair_created_at=base_time,
            )
        )

    return snapshots


def test_features():
    print("\n[1/3] Testing Feature Engineering...")
    snapshots = generate_synthetic_snapshots(200)
    engineer = FeatureEngineer(timeframe_minutes=5)

    df = engineer.build_features(snapshots)
    if df is None:
        print("  [FAIL] Could not build features")
        return

    print(f"  [OK] Built features: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  - Feature columns: {list(df.columns)[:10]}...")

    latest = engineer.get_latest_feature_vector(snapshots)
    if latest is not None:
        print(f"  [OK] Latest feature vector has {len(latest)} features")
    else:
        print("  [FAIL] Could not get latest feature vector")


def test_regime():
    print("\n[2/3] Testing Regime Detection...")
    snapshots = generate_synthetic_snapshots(200)
    engineer = FeatureEngineer(timeframe_minutes=5)
    df = engineer.build_features(snapshots)

    if df is None or len(df) < 20:
        print("  [FAIL] Not enough data for regime detection")
        return

    detector = RegimeDetector(n_components=3, lookback_bars=50)
    detector.fit(df)
    result = detector.predict(df)

    print(f"  [OK] Detected regime: {result.regime.value}")
    print(f"  - Probability: {result.probability:.2f}")
    print(f"  - Tradable: {detector.is_tradable(result)}")


def test_token_scorer():
    print("\n[3/3] Testing Token Scoring...")
    scorer = TokenScorer()

    # Safe token
    safe_snapshot = PriceSnapshot(
        token_address="SAFE",
        symbol="SAFE",
        price_usd=0.01,
        liquidity_usd=500_000,
        volume_24h_usd=100_000,
        volume_1h_usd=10_000,
        price_change_1h_pct=5.0,
        price_change_24h_pct=20.0,
        txns_24h_buy=100,
        txns_24h_sell=90,
        fdv=1_000_000,
        market_cap=900_000,
        timestamp=datetime.now() - timedelta(hours=48),
        source="test",
        pair_created_at=datetime.now() - timedelta(hours=48),
    )
    safe_risk = scorer.score(safe_snapshot)
    print(f"  [OK] Safe token score: {safe_risk.total_score:.1f}/100")
    print(f"  - Is safe: {safe_risk.is_safe}")
    if not safe_risk.is_safe:
        print(f"  - Reasons: {safe_risk.reasons[:3]}")

    # Risky token
    risky_snapshot = PriceSnapshot(
        token_address="RISKY",
        symbol="RISKY",
        price_usd=0.0001,
        liquidity_usd=2_000,
        volume_24h_usd=200_000,
        volume_1h_usd=50_000,
        price_change_1h_pct=150.0,
        price_change_24h_pct=500.0,
        txns_24h_buy=500,
        txns_24h_sell=20,
        fdv=50_000_000,
        market_cap=1_000_000,
        timestamp=datetime.now() - timedelta(minutes=10),
        source="test",
        pair_created_at=datetime.now() - timedelta(minutes=10),
    )
    risky_risk = scorer.score(risky_snapshot)
    print(f"  [OK] Risky token score: {risky_risk.total_score:.1f}/100")
    print(f"  - Is safe: {risky_risk.is_safe}")
    print(f"  - Reasons: {risky_risk.reasons[:3]}")


def test_trailing_stop():
    print("\n[4/4] Testing Trailing Stop-Loss...")
    from execution.position_manager import PositionManager

    pm = PositionManager()
    pm.open_position(
        token_address="TEST",
        symbol="TEST",
        entry_price=100.0,
        token_amount=1.0,
        sol_invested=0.5,
        stop_loss_pct=0.10,
        take_profit_pct=0.20,
        trailing_stop_pct=0.05,
        trailing_stop_activation_pct=0.10,
    )

    # Price rises 12% — trailing stop should activate
    closed = pm.update_position_price("TEST", 112.0)
    assert closed is None, "Should not close on gain yet"

    # Price pulls back 5% from peak (112 -> 106.4), should hit trailing stop
    closed = pm.update_position_price("TEST", 106.0)
    assert closed is not None, "Trailing stop should have closed"
    assert closed.reason == "trailing_stop", f"Expected trailing_stop, got {closed.reason}"
    print(f"  [OK] Trailing stop closed at ${closed.exit_price:.2f}, PnL: {closed.pnl_pct:+.2f}%")


def main():
    print("=" * 60)
    print("PolyCryptoAlpha Phase 2 Tests")
    print("=" * 60)

    test_features()
    test_regime()
    test_token_scorer()
    test_trailing_stop()

    print("\n" + "=" * 60)
    print("Phase 2 tests complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
