"""Build script for PolyCryptoAlpha Trading Bot .exe"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyInstaller.__main__ import run
import xgboost
import lightgbm

# Paths
icon_path = PROJECT_ROOT / "ui" / "assets" / "icon.ico"
xgboost_pkg = Path(xgboost.__file__).parent
lightgbm_pkg = Path(lightgbm.__file__).parent

# Build arguments
args = [
    str(PROJECT_ROOT / "main.py"),
    "--name", "PolyCryptoAlpha",
    "--onefile",
    "--windowed",
    "--clean",
    "--noconfirm",
    "--icon", str(icon_path),
    "--add-data", f"{PROJECT_ROOT / '.env'};.",
    "--add-data", f"{PROJECT_ROOT / 'data'};data",
    "--add-data", f"{PROJECT_ROOT / 'models'};models",
    "--add-data", f"{PROJECT_ROOT / 'ui' / 'assets'};ui\\assets",
    "--add-data", f"{xgboost_pkg};xgboost",
    "--add-data", f"{lightgbm_pkg};lightgbm",
    "--hidden-import", "sklearn",
    "--hidden-import", "sklearn.ensemble",
    "--hidden-import", "sklearn.tree",
    "--hidden-import", "sklearn.utils._typedefs",
    "--hidden-import", "sklearn.neighbors._partition_nodes",
    "--hidden-import", "sklearn.linear_model._sgd_fast",
    "--hidden-import", "lightgbm",
    "--hidden-import", "xgboost",
    "--hidden-import", "joblib",
    "--hidden-import", "numpy",
    "--hidden-import", "pandas",
    "--hidden-import", "PIL",
    "--hidden-import", "aiohttp",
    "--hidden-import", "requests",
    "--hidden-import", "tkinter",
    "--hidden-import", "loguru",
    "--hidden-import", "sniper",
    "--hidden-import", "sniper.sniper_bot",
    "--hidden-import", "data.robinhood_chain",
    "--hidden-import", "execution.robinhood_trader",
]

print("Building PolyCryptoAlpha executable...")
print(f"Icon: {icon_path}")
run(args)
print("\nBuild complete!")
print(f"Executable: {PROJECT_ROOT / 'dist' / 'PolyCryptoAlpha.exe'}")
