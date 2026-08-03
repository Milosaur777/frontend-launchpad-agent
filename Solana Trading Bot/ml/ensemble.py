"""
ML ensemble for memecoin direction prediction.
Combines LightGBM and XGBoost with probability calibration.
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
import pandas as pd

import lightgbm as lgb
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler


@dataclass
class Prediction:
    """Prediction result for a single sample."""

    direction: int  # 1 = up, 0 = down/flat
    probability_up: float
    confidence: float
    model_votes: Dict[str, float]


class MemecoinEnsemble:
    """
    Ensemble of LightGBM and XGBoost for predicting short-term price direction.
    """

    # Columns to exclude from feature matrix
    META_COLS = {"token_address", "symbol", "timestamp", "target", "open", "high", "low", "close", "volume"}

    def __init__(
        self,
        models: Optional[List[str]] = None,
        lgb_params: Optional[Dict] = None,
        xgb_params: Optional[Dict] = None,
        calibrate: bool = True,
    ):
        """
        Initialize ensemble.

        Args:
            models: List of model names to use. Default: ["lightgbm", "xgboost"].
            lgb_params: Custom LightGBM parameters.
            xgb_params: Custom XGBoost parameters.
            calibrate: Whether to calibrate probabilities.
        """
        self.model_names = models or ["lightgbm", "xgboost"]
        self.calibrate = calibrate
        self.scaler = StandardScaler()

        self.lgb_params = lgb_params or {
            "objective": "binary",
            "metric": "binary_logloss",
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "feature_fraction": 0.8,
            "bagging_fraction": 0.8,
            "bagging_freq": 5,
            "verbose": -1,
            "n_estimators": 200,
            "random_state": 42,
        }

        self.xgb_params = xgb_params or {
            "objective": "binary:logistic",
            "eval_metric": "logloss",
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "n_estimators": 200,
            "random_state": 42,
        }

        self.models: Dict[str, object] = {}
        self.feature_names: List[str] = []
        self.is_fitted = False

    def _get_feature_matrix(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Extract feature matrix and target from dataframe."""
        feature_cols = [c for c in df.columns if c not in self.META_COLS]
        self.feature_names = feature_cols

        X = df[feature_cols].copy()
        y = df["target"].copy() if "target" in df.columns else None

        # Replace infinities and NaNs
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(X.median())

        return X, y

    def fit(self, df: pd.DataFrame) -> "MemecoinEnsemble":
        """
        Fit ensemble models on training data.

        Args:
            df: DataFrame with features and 'target' column.
        """
        X, y = self._get_feature_matrix(df)
        if y is None:
            raise ValueError("Training dataframe must contain 'target' column")

        if len(X) < 50:
            raise ValueError(f"Need at least 50 samples, got {len(X)}")

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Compute class weights for imbalance
        class_counts = y.value_counts()
        scale_pos_weight = class_counts.min() / class_counts.max()

        for name in self.model_names:
            if name == "lightgbm":
                params = self.lgb_params.copy()
                params["scale_pos_weight"] = scale_pos_weight
                base_model = lgb.LGBMClassifier(**params)

                if self.calibrate:
                    model = CalibratedClassifierCV(base_model, cv=3, method="isotonic")
                    model.fit(X_scaled, y)
                else:
                    model = base_model
                    model.fit(X_scaled, y)

                self.models[name] = model

            elif name == "xgboost":
                params = self.xgb_params.copy()
                params["scale_pos_weight"] = scale_pos_weight
                base_model = xgb.XGBClassifier(**params)

                if self.calibrate:
                    model = CalibratedClassifierCV(base_model, cv=3, method="isotonic")
                    model.fit(X_scaled, y)
                else:
                    model = base_model
                    model.fit(X_scaled, y)

                self.models[name] = model

        self.is_fitted = True
        return self

    def predict(self, df: pd.DataFrame) -> List[Prediction]:
        """
        Predict direction for each row in dataframe.

        Args:
            df: DataFrame with features.

        Returns:
            List of Prediction objects.
        """
        if not self.is_fitted:
            raise RuntimeError("Ensemble must be fitted before prediction")

        X, _ = self._get_feature_matrix(df)
        X_scaled = self.scaler.transform(X)
        X_scaled_df = pd.DataFrame(X_scaled, columns=self.feature_names)

        predictions = []
        for i in range(len(X_scaled_df)):
            row_df = X_scaled_df.iloc[i:i + 1]

            votes = {}
            for name, model in self.models.items():
                prob_up = float(model.predict_proba(row_df)[0, 1])
                votes[name] = prob_up

            # Simple average ensemble
            avg_prob = np.mean(list(votes.values()))
            direction = 1 if avg_prob > 0.5 else 0
            confidence = max(avg_prob, 1 - avg_prob)

            predictions.append(
                Prediction(
                    direction=direction,
                    probability_up=avg_prob,
                    confidence=confidence,
                    model_votes=votes,
                )
            )

        return predictions

    def predict_single(self, features: pd.Series) -> Prediction:
        """Predict for a single feature vector."""
        df = pd.DataFrame([features])
        return self.predict(df)[0]

    def feature_importance(self) -> Optional[pd.Series]:
        """Get aggregated feature importance from tree models."""
        if not self.is_fitted:
            return None

        importances = []
        for name, model in self.models.items():
            if name == "lightgbm":
                # CalibratedClassifierCV wraps the base estimator
                base = model.calibrated_classifiers_[0].estimator
                imp = base.feature_importances_
            elif name == "xgboost":
                base = model.calibrated_classifiers_[0].estimator
                imp = base.feature_importances_
            else:
                continue

            importances.append(imp)

        if not importances:
            return None

        avg_importance = np.mean(importances, axis=0)
        return pd.Series(avg_importance, index=self.feature_names).sort_values(ascending=False)

    def save(self, path: Path):
        """Save ensemble to disk."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

        import joblib
        for name, model in self.models.items():
            joblib.dump(model, path / f"{name}_model.pkl")

        joblib.dump(self.scaler, path / "scaler.pkl")

        metadata = {
            "model_names": self.model_names,
            "feature_names": self.feature_names,
            "calibrate": self.calibrate,
        }
        with open(path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

    def load(self, path: Path) -> "MemecoinEnsemble":
        """Load ensemble from disk."""
        path = Path(path)
        import joblib

        self.models = {}
        for name in self.model_names:
            model_path = path / f"{name}_model.pkl"
            if model_path.exists():
                self.models[name] = joblib.load(model_path)

        scaler_path = path / "scaler.pkl"
        if scaler_path.exists():
            self.scaler = joblib.load(scaler_path)

        metadata_path = path / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            self.feature_names = metadata.get("feature_names", [])

        self.is_fitted = len(self.models) > 0
        return self
