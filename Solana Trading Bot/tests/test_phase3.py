"""
Phase 3 tests: ML ensemble, trainer, inference.
Run with: python tests/test_phase3.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random
import warnings

sys.path.insert(0, str(Path(__file__).parent.parent))
warnings.filterwarnings("ignore")

import pandas as pd

from data.price_feed import PriceSnapshot
from ml.features import FeatureEngineer
from ml.ensemble import MemecoinEnsemble
from ml.trainer import ModelTrainer
from ml.inference import InferenceEngine


def generate_trending_snapshots(
    n: int = 300,
    token_address: str = "TEST",
    trend: float = 0.002,
) -> list:
    """Generate synthetic snapshots with a slight upward bias."""
    snapshots = []
    price = 0.001
    base_time = datetime.now() - timedelta(minutes=n * 5)

    for i in range(n):
        change = random.gauss(trend, 0.015)
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


def test_ensemble():
    print("\n[1/4] Testing Memecoin Ensemble...")

    # Generate training data for 3 tokens
    history = {}
    for i in range(3):
        trend = 0.002 if i % 2 == 0 else -0.001
        history[f"TOKEN_{i}"] = generate_trending_snapshots(300, f"TOKEN_{i}", trend)

    engineer = FeatureEngineer(timeframe_minutes=5)
    trainer = ModelTrainer(engineer=engineer)
    df = trainer.generate_training_data(history, forward_bars=3)

    if df is None or len(df) < 100:
        print(f"  [FAIL] Not enough training data: {df.shape if df is not None else 'None'}")
        return

    print(f"  [OK] Training data: {df.shape[0]} rows x {df.shape[1]} columns")

    ensemble = MemecoinEnsemble()
    ensemble.fit(df)
    print(f"  [OK] Ensemble fitted with {len(ensemble.models)} models")

    # Predict on latest row
    latest_features = df.iloc[-1].drop("target", errors="ignore")
    pred = ensemble.predict_single(latest_features)
    print(f"  [OK] Prediction: direction={pred.direction}, prob_up={pred.probability_up:.3f}, confidence={pred.confidence:.3f}")

    importance = ensemble.feature_importance()
    if importance is not None:
        print(f"  - Top feature: {importance.index[0]} ({importance.iloc[0]:.4f})")


def test_trainer():
    print("\n[2/4] Testing Walk-Forward Trainer...")

    history = {}
    for i in range(3):
        trend = 0.002 if i % 2 == 0 else -0.001
        history[f"TOKEN_{i}"] = generate_trending_snapshots(300, f"TOKEN_{i}", trend)

    trainer = ModelTrainer(engineer=FeatureEngineer(timeframe_minutes=5))
    df = trainer.generate_training_data(history, forward_bars=3)

    if df is None or len(df) < 100:
        print("  [FAIL] Not enough data")
        return

    metrics = trainer.walk_forward_validation(df)
    if "error" in metrics:
        print(f"  [WARN] Walk-forward validation: {metrics['error']}")
    else:
        print(f"  [OK] Walk-forward validation complete")
        print(f"  - Avg accuracy: {metrics['avg_accuracy']:.3f}")
        print(f"  - Avg hit rate: {metrics['avg_hit_rate']:.3f}")


def test_save_load():
    print("\n[3/4] Testing Model Save/Load...")

    history = {}
    for i in range(2):
        history[f"TOKEN_{i}"] = generate_trending_snapshots(300, f"TOKEN_{i}")

    trainer = ModelTrainer(engineer=FeatureEngineer(timeframe_minutes=5))
    df = trainer.generate_training_data(history, forward_bars=3)

    if df is None or len(df) < 100:
        print("  [FAIL] Not enough data")
        return

    model_dir = Path(__file__).parent.parent / "models" / "test_model"
    ensemble = trainer.train_final_model(df, model_dir=model_dir)
    print(f"  [OK] Model saved to {model_dir}")

    loaded = MemecoinEnsemble()
    loaded.load(model_dir)
    print(f"  [OK] Model loaded, fitted={loaded.is_fitted}")


def test_inference():
    print("\n[4/4] Testing Inference Engine...")

    history = {}
    for i in range(2):
        history[f"TOKEN_{i}"] = generate_trending_snapshots(300, f"TOKEN_{i}")

    trainer = ModelTrainer(engineer=FeatureEngineer(timeframe_minutes=5))
    df = trainer.generate_training_data(history, forward_bars=3)

    if df is None or len(df) < 100:
        print("  [FAIL] Not enough data")
        return

    model_dir = Path(__file__).parent.parent / "models" / "test_model"
    trainer.train_final_model(df, model_dir=model_dir)

    engine = InferenceEngine(model_dir=model_dir, use_onnx=False)
    if not engine.load():
        print("  [FAIL] Could not load inference engine")
        return

    latest_features = df.iloc[-1].drop("target", errors="ignore")
    pred = engine.predict(latest_features)
    if pred:
        print(f"  [OK] Inference: direction={pred.direction}, prob_up={pred.probability_up:.3f}, confidence={pred.confidence:.3f}")
    else:
        print("  [FAIL] Inference returned None")


def main():
    print("=" * 60)
    print("PolyCryptoAlpha Phase 3 Tests")
    print("=" * 60)

    test_ensemble()
    test_trainer()
    test_save_load()
    test_inference()

    print("\n" + "=" * 60)
    print("Phase 3 tests complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
