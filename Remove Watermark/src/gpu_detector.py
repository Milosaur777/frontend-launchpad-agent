"""Auto-detect GPU capabilities (CUDA / MPS / CPU fallback)."""

from __future__ import annotations

import subprocess
import sys


def detect_gpu() -> dict[str, object]:
    """Detect the best available compute device.

    Returns a dict with:
        available (bool): True if GPU is usable.
        type (str): "cuda", "mps", or "cpu".
        name (str): Human-readable device name.
    """
    # Try torch first
    try:
        import torch

        if torch.cuda.is_available():
            return {
                "available": True,
                "type": "cuda",
                "name": torch.cuda.get_device_name(0),
            }
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return {
                "available": True,
                "type": "mps",
                "name": "Apple Silicon (MPS)",
            }
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: try nvidia-smi
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            gpu_name = result.stdout.strip().split("\n")[0].strip()
            if gpu_name:
                return {
                    "available": True,
                    "type": "cuda",
                    "name": gpu_name,
                }
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        pass

    return {
        "available": False,
        "type": "cpu",
        "name": "CPU Only",
    }


if __name__ == "__main__":
    info = detect_gpu()
    print(f"GPU Available: {info['available']}")
    print(f"Type: {info['type']}")
    print(f"Name: {info['name']}")
