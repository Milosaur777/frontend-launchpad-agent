# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['F:\\1. CORE\\Projekt\\18.OpenCode\\Frontend Agent\\Solana Trading Bot\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('F:\\1. CORE\\Projekt\\18.OpenCode\\Frontend Agent\\Solana Trading Bot\\.env', '.'), ('F:\\1. CORE\\Projekt\\18.OpenCode\\Frontend Agent\\Solana Trading Bot\\data', 'data'), ('F:\\1. CORE\\Projekt\\18.OpenCode\\Frontend Agent\\Solana Trading Bot\\models', 'models'), ('F:\\1. CORE\\Projekt\\18.OpenCode\\Frontend Agent\\Solana Trading Bot\\ui\\assets', 'ui\\assets'), ('C:\\Users\\Milo\\AppData\\Roaming\\Python\\Python314\\site-packages\\xgboost', 'xgboost'), ('C:\\Users\\Milo\\AppData\\Roaming\\Python\\Python314\\site-packages\\lightgbm', 'lightgbm')],
    hiddenimports=['sklearn', 'sklearn.ensemble', 'sklearn.tree', 'sklearn.utils._typedefs', 'sklearn.neighbors._partition_nodes', 'sklearn.linear_model._sgd_fast', 'lightgbm', 'xgboost', 'joblib', 'numpy', 'pandas', 'PIL', 'aiohttp', 'requests', 'tkinter', 'loguru', 'sniper', 'sniper.sniper_bot', 'data.robinhood_chain', 'execution.robinhood_trader'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PolyCryptoAlpha',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['F:\\1. CORE\\Projekt\\18.OpenCode\\Frontend Agent\\Solana Trading Bot\\ui\\assets\\icon.ico'],
)
