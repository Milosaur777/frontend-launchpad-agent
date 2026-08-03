"""
Walk-forward training pipeline for the memecoin ensemble.
"""

from typing import Optional, Dict, List
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit

from ml.features import FeatureEngineer
from ml.ensemble import MemecoinEnsemble
from config.settings import Config


class ModelTrainer:
    """
    Trains the ML ensemble using walk-forward analysis.

    Key principles:
    - No lookahead bias: train only on past data
    - Purged cross-validation: remove overlapping periods
    - Regime-aware: evaluate separately by market regime
    """

    def __init__(
        self,
        engineer: Optional[FeatureEngineer] = None,
        n_splits: int = 5,
        purge_bars: int = 3,
    ):
        self.engineer = engineer or FeatureEngineer()
        self.n_splits = n_splits
        self.purge_bars = purge_bars
        self.metrics: List[Dict] = []

    def _purge_split(
        self,
        train_idx: np.ndarray,
        test_idx: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Remove purge window between train and test sets."""
        if len(test_idx) == 0:
            return train_idx, test_idx

        test_start = test_idx.min()
        # Remove last purge_bars from train that are closest to test set
        train_idx = train_idx[train_idx < test_start - self.purge_bars]
        return train_idx, test_idx

    def walk_forward_validation(
        self,
        df: pd.DataFrame,
    ) -> Dict:
        """
        Run walk-forward cross-validation.

        Returns:
            Dict with average metrics across folds.
        """
        if "target" not in df.columns:
            raise ValueError("DataFrame must contain 'target' column")

        X = df.drop(columns=["target"])
        y = df["target"]

        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        fold_metrics = []

        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            train_idx, test_idx = self._purge_split(train_idx, test_idx)

            if len(train_idx) < 50 or len(test_idx) < 10:
                continue

            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

            train_df = X_train.copy()
            train_df["target"] = y_train

            model = MemecoinEnsemble()
            model.fit(train_df)

            test_df = X_test.copy()
            test_df["target"] = y_test
            preds = model.predict(test_df)

            pred_labels = [p.direction for p in preds]
            actual = y_test.values

            accuracy = np.mean(np.array(pred_labels) == actual)
            # Directional hit rate on positive class
            up_mask = actual == 1
            hit_rate = np.mean(np.array(pred_labels)[up_mask] == 1) if up_mask.any() else 0.0

            fold_metrics.append({
                "fold": fold + 1,
                "accuracy": accuracy,
                "hit_rate": hit_rate,
                "n_train": len(train_idx),
                "n_test": len(test_idx),
            })

        self.metrics = fold_metrics

        if not fold_metrics:
            return {"error": "No valid folds"}

        return {
            "avg_accuracy": np.mean([m["accuracy"] for m in fold_metrics]),
            "avg_hit_rate": np.mean([m["hit_rate"] for m in fold_metrics]),
            "folds": fold_metrics,
        }

    def train_final_model(
        self,
        df: pd.DataFrame,
        model_dir: Optional[Path] = None,
    ) -> MemecoinEnsemble:
        """
        Train final model on all available data.

        Args:
            df: Training dataframe with features and target.
            model_dir: Directory to save model.

        Returns:
            Fitted MemecoinEnsemble.
        """
        model = MemecoinEnsemble()
        model.fit(df)

        if model_dir:
            model_dir = Path(model_dir)
            model_dir.mkdir(parents=True, exist_ok=True)
            model.save(model_dir)

        return model

    def generate_training_data(
        self,
        snapshot_history: Dict[str, List],
        forward_bars: int = 3,
    ) -> Optional[pd.DataFrame]:
        """
        Generate training dataset from price history.

        Args:
            snapshot_history: Dict mapping token -> list of snapshots.
            forward_bars: Bars ahead to predict.

        Returns:
            Combined training dataframe.
        """
        return self.engineer.create_training_dataset(
            snapshot_history,
            forward_bars=forward_bars,
        )
