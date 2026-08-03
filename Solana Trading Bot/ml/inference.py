"""
Fast inference engine for the memecoin ensemble.
Supports both native models and ONNX Runtime for low-latency predictions.
"""

from typing import Optional, List, Dict
from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
import joblib

from ml.ensemble import MemecoinEnsemble, Prediction
from config.settings import Config

# Optional ONNX support
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


try:
    from skl2onnx import convert_lightgbm, convert_xgboost
    from skl2onnx.common.data_types import FloatTensorType
    SKL2ONNX_AVAILABLE = True
except ImportError:
    SKL2ONNX_AVAILABLE = False


class InferenceEngine:
    """
    Load and run the memecoin prediction ensemble.

    Tries ONNX first for speed, falls back to native models.
    """

    def __init__(self, model_dir: Optional[Path] = None, use_onnx: bool = True):
        """
        Initialize inference engine.

        Args:
            model_dir: Directory containing saved models.
            use_onnx: Whether to try loading ONNX models.
        """
        self.model_dir = Path(model_dir) if model_dir else Config.MODELS_DIR
        self.use_onnx = use_onnx and ONNX_AVAILABLE

        self.native_ensemble: Optional[MemecoinEnsemble] = None
        self.onnx_sessions: Dict[str, ort.InferenceSession] = {}
        self.scaler = None
        self.feature_names: List[str] = []
        self.model_names: List[str] = []
        self.is_ready = False

    def load(self) -> bool:
        """Load models from disk. Returns True if successful."""
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Try ONNX first
        if self.use_onnx:
            if self._load_onnx():
                self.is_ready = True
                return True

        # Fallback to native models
        if self._load_native():
            self.is_ready = True
            return True

        return False

    def _load_native(self) -> bool:
        """Load native sklearn models."""
        try:
            metadata_path = self.model_dir / "metadata.json"
            if not metadata_path.exists():
                return False

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            self.model_names = metadata.get("model_names", [])
            self.feature_names = metadata.get("feature_names", [])

            ensemble = MemecoinEnsemble(models=self.model_names)
            ensemble.load(self.model_dir)

            self.native_ensemble = ensemble
            self.scaler = ensemble.scaler
            return ensemble.is_fitted
        except Exception as e:
            warnings.warn(f"Failed to load native models: {e}")
            return False

    def _load_onnx(self) -> bool:
        """Load ONNX models."""
        if not ONNX_AVAILABLE:
            return False

        try:
            metadata_path = self.model_dir / "metadata.json"
            if not metadata_path.exists():
                return False

            with open(metadata_path, "r") as f:
                metadata = json.load(f)

            self.model_names = metadata.get("model_names", [])
            self.feature_names = metadata.get("feature_names", [])

            self.onnx_sessions = {}
            for name in self.model_names:
                onnx_path = self.model_dir / f"{name}_model.onnx"
                if onnx_path.exists():
                    sess_options = ort.SessionOptions()
                    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                    sess_options.intra_op_num_threads = 1
                    self.onnx_sessions[name] = ort.InferenceSession(
                        str(onnx_path), sess_options
                    )

            # Load scaler
            scaler_path = self.model_dir / "scaler.pkl"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)

            return len(self.onnx_sessions) > 0
        except Exception as e:
            warnings.warn(f"Failed to load ONNX models: {e}")
            return False

    def _prepare_features(self, features: pd.Series) -> np.ndarray:
        """Prepare feature vector for inference."""
        if not self.feature_names:
            # Use all numeric columns except known metadata
            exclude = {"token_address", "symbol", "timestamp", "target", "open", "high", "low", "close", "volume"}
            self.feature_names = [c for c in features.index if c not in exclude]

        # Cast to float64 first to avoid overflow on large raw values (fdv, market_cap)
        row = features[self.feature_names].values.astype(np.float64)
        row = np.nan_to_num(row, nan=0.0, posinf=0.0, neginf=0.0)

        if self.scaler is not None:
            row = self.scaler.transform(row.reshape(1, -1))[0]

        # ONNX expects float32; native models are fine with float64
        return row.astype(np.float32) if self.onnx_sessions else row

    def predict(self, features: pd.Series) -> Optional[Prediction]:
        """Run inference on a single feature vector."""
        if not self.is_ready:
            return None

        row = self._prepare_features(features)

        if self.onnx_sessions:
            votes = {}
            for name, session in self.onnx_sessions.items():
                input_name = session.get_inputs()[0].name
                prob = session.run(None, {input_name: row.reshape(1, -1)})[1][0, 1]
                votes[name] = float(prob)

            avg_prob = np.mean(list(votes.values()))
            direction = 1 if avg_prob > 0.5 else 0
            confidence = max(avg_prob, 1 - avg_prob)

            return Prediction(
                direction=direction,
                probability_up=avg_prob,
                confidence=confidence,
                model_votes=votes,
            )

        elif self.native_ensemble:
            # Create DataFrame to preserve feature names
            feature_df = pd.DataFrame([features])
            preds = self.native_ensemble.predict(feature_df)
            return preds[0] if preds else None

        return None

    def predict_batch(self, df: pd.DataFrame) -> List[Optional[Prediction]]:
        """Run inference on multiple rows."""
        return [self.predict(row) for _, row in df.iterrows()]

    @staticmethod
    def export_onnx(ensemble: MemecoinEnsemble, model_dir: Path) -> bool:
        """
        Export native models to ONNX format.

        Returns:
            True if export succeeded for at least one model.
        """
        if not SKL2ONNX_AVAILABLE or not ONNX_AVAILABLE:
            warnings.warn("ONNX export not available. Install skl2onnx and onnxruntime.")
            return False

        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        exported = False
        n_features = len(ensemble.feature_names)
        initial_type = [("float_input", FloatTensorType([None, n_features]))]

        for name, model in ensemble.models.items():
            try:
                # CalibratedClassifierCV wraps base estimator
                base = model.calibrated_classifiers_[0].estimator

                if name == "lightgbm":
                    onnx_model = convert_lightgbm(base, initial_types=initial_type)
                elif name == "xgboost":
                    onnx_model = convert_xgboost(base, initial_types=initial_type)
                else:
                    continue

                onnx_path = model_dir / f"{name}_model.onnx"
                with open(onnx_path, "wb") as f:
                    f.write(onnx_model.SerializeToString())
                exported = True
            except Exception as e:
                warnings.warn(f"Failed to export {name} to ONNX: {e}")

        return exported
