# PolyCryptoAlpha v2.0 — Solana + Robinhood Chain Viral Memecoin Trading Bot

A fully automated memecoin trading bot built with Python, machine learning, and free-tier infrastructure.

**Strategy:** Machine-learning-driven trading on **established memecoins that are going viral** — not PumpFun sniping. We require tokens to have proven liquidity, volume, transaction activity, and a minimum on-chain age before the model is even allowed to consider them.

## What It Does

- Discovers established, high-activity memecoins via **DexScreener** (free)
- Supports **Solana** and **Robinhood Chain** tokens
- Predicts short-term price direction with **LightGBM + XGBoost** ensemble
- Filters tokens for rugpull / low-liquidity / stale-token risk
- Executes swaps via **Jupiter** aggregator (Solana only)
- Manages risk with stop-loss, take-profit, **trailing stop-loss**, drawdown limits, and circuit breakers
- Supports a **fixed watchlist** of curated tokens (e.g., BONK, WIF, POPCAT, CASHCAT)
- Includes a **backtest harness** to tune parameters on synthetic history
- Runs in **paper mode** by default for safe testing
- **Desktop dashboard** for live monitoring and control
- **Learning journal** that persists trade notes and insights

## Architecture

```
data/              # Market data (DexScreener, Jupiter, Solana RPC)
execution/         # Wallet, swap execution, position tracking
ml/                # Feature engineering, regime detection, ML ensemble, learning journal
risk/              # Risk management and position sizing
strategy/          # Momentum, volume breakout, signal orchestration
monitoring/        # Logging and alerts
ui/                # Tkinter desktop dashboard
bot_core.py        # Main trading loop
main.py            # Entry point
```

## Quick Start

### 1. Install Python Dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add:

```env
SOLANA_PRIVATE_KEY=your_phantom_private_key_here
LIVE_MODE=false
INITIAL_CAPITAL=100
```

To get your Phantom private key:
1. Open Phantom wallet
2. Click the three dots → Settings
3. Export Private Key
4. Copy the base58 string

**WARNING:** Never commit `.env` to Git. It is already in `.gitignore`.

### 3. Run Tests

```bash
python tests/test_phase1.py   # Data + wallet + RPC
python tests/test_phase2.py   # Features + regime + risk scoring + trailing stop
python tests/test_phase3.py   # ML ensemble + training
python tests/test_bot.py      # Full paper trading cycle
python tests/test_backtest.py # Backtest engine
python tests/test_watchlist.py # Fixed watchlist config
```

### 4. Launch the Desktop Dashboard

```bash
python main.py --ui
```

The dashboard gives you:
- Real-time portfolio overview and PnL
- **Live price chart** with candlestick/line modes, multi-token overlays, time ranges (1h/4h/24h/ALL), EMA/RSI/MACD indicators, trade entry/exit markers, hover crosshair, volume bars, and PNG screenshot export
- Live token watchlist with safety scores
- Open positions with trailing stops
- Trade history
- ML model status
- Trading journal with AI-style notes
- Settings panel with **paper/live toggle**

### 5. Run a Backtest

```bash
python backtest/engine.py          # Synthetic data
python backtest/from_csv.py        # TradingView CSVs (if available)
```

Generates synthetic price histories (or loads your CSVs) and replays them through the full signal + risk + execution pipeline. Use this to tune `MIN_CONFIDENCE`, stop-loss, and take-profit before risking capital.

> **Note:** Synthetic backtests are optimistic and mainly validate plumbing. Real-market results will differ.

#### Exporting from TradingView

1. Open a chart for your token (e.g., BONK/USD on Raydium)
2. Set timeframe to **5 minutes**
3. Click the **three dots menu** → **Export chart data**
4. Save the CSV to `data/historical/`

Example filenames:
- `bonk_5m.csv`
- `wif_5m.csv`
- `popcat_5m.csv`

Then edit `backtest/from_csv.py` to map your filenames, and run it.

### 6. Run the Bot (Paper Mode)

```bash
python main.py
```

The bot starts in **paper mode** by default. It will not send real transactions.

### 7. Go Live (Only After Profitable Paper Trading)

Switch to live mode in the dashboard settings, or edit `.env`:

```bash
LIVE_MODE=true
python main.py
```

## Configuration

Key settings in `.env`:

| Variable | Description | Default |
|---|---|---|
| `SOLANA_PRIVATE_KEY` | Your wallet private key | required |
| `LIVE_MODE` | `true` = real trades, `false` = paper | `false` |
| `INITIAL_CAPITAL` | Starting capital in USD | `100` |
| `MAX_RISK_PER_TRADE` | Max % of capital per trade | `0.20` |
| `MAX_DAILY_LOSS` | Daily loss limit as % of capital | `0.10` |
| `MAX_DRAWDOWN` | Max drawdown before halt | `0.30` |
| `STOP_LOSS_PCT` | Per-trade stop loss | `0.05` |
| `TAKE_PROFIT_PCT` | Per-trade take profit | `0.10` |
| `TRAILING_STOP_PCT` | Trailing stop distance | `0.03` |
| `TRAILING_STOP_ACTIVATION_PCT` | Trailing stop activation | `0.05` |
| `MIN_CONFIDENCE` | Minimum ML confidence to trade | `0.65` |
| `TIMEFRAME` | Analysis timeframe | `5m` |
| `MIN_LIQUIDITY_USD` | Minimum pool liquidity | `50000` |
| `MIN_VOLUME_24H_USD` | Minimum 24h volume | `100000` |
| `MIN_TOKEN_AGE_HOURS` | Minimum token age (no snipes) | `24` |
| `WATCHLIST_MODE` | `discovery` or `fixed` | `discovery` |
| `BACKTEST_INITIAL_CAPITAL` | Backtest starting capital | `100` |
| `BACKTEST_FEE_PCT` | Backtest fee per trade | `0.002` |

## Supported Chains

| Chain | Data | Execution | Notes |
|---|---|---|---|
| **Solana** | DexScreener + Jupiter | Jupiter swaps | Full support |
| **Robinhood Chain** | DexScreener | Paper only | Price tracking + signals; swaps not yet integrated |

## Watchlists

### Solana Fixed Watchlist

BONK, WIF, POPCAT, TRUMP, WEN, PONKE, BONK2, MOG, GIGA, PNUT

### Robinhood Chain Fixed Watchlist

CASHCAT, HOODRAT, TENDIES, WENLAMBO, DIH

Edit `config/settings.py` to customize.

## Data Sources

| Source | Cost | Purpose |
|---|---|---|
| DexScreener API | Free | Prices, liquidity, volume, trending pairs |
| Jupiter Swap API | Free | Swap quotes and transaction building |
| Solana Public RPC | Free | Transaction submission, balance queries |
| Helius RPC | Free tier | Optional faster RPC |

## Alpaca API

[Alpaca](https://alpaca.markets) offers a **free** API for commission-free US stock/ETF paper and live trading. It is a good choice if you want to:

- Trade memecoin-adjacent equities like **HOOD** (Robinhood) or **COIN** (Coinbase)
- Run a stock strategy alongside the crypto bot
- Use a regulated broker with a real public API

**Current status:** The bot does not yet execute through Alpaca. Robinhood Chain tokens are tracked and paper-traded via DexScreener prices. Alpaca integration can be added later as a separate execution venue for equities.

To prepare:
1. Sign up at [alpaca.markets](https://alpaca.markets)
2. Generate paper + live API keys
3. Add them in the dashboard Settings panel (`Alpaca API Key`, `Alpaca Secret`)

## Learning Journal

Every closed trade is automatically journaled in `data/journal/`:

- `trade_notes.json` — timestamped trade notes
- `patterns.json` — manually or programmatically learned patterns
- `insights.json` — rolling analysis of win rate, avg win/loss, and top tags

The journal helps the bot (and you) understand what is working and what is not.

## Cost

With free infrastructure, the only costs are:
- Solana transaction fees (~0.000005 SOL per tx)
- Jupiter priority fees (optional, ~0.00001 SOL)
- Jito tips (optional MEV protection, ~0.0001 SOL)

On $100 capital, expect ~$0.01-0.05 per round-trip trade.

## Risk Warning

**This bot trades memecoins, which are extremely risky.** Most memecoins go to zero. This is experimental software. Only trade money you can afford to lose. Always start in paper mode.

## Next Steps

1. Run paper mode for 1-2 weeks
2. Analyze trade logs in `data/positions.json`, `data/journal/`, and `logs/`
3. Tune `MIN_CONFIDENCE`, `STOP_LOSS_PCT`, `TAKE_PROFIT_PCT`
4. Consider upgrading to paid Helius RPC for faster execution
5. Add Jito bundles for MEV protection when profitable

## Build Standalone .exe

To build a portable Windows executable:

```bash
# Install build dependency
pip install -r requirements.txt

# Build the .exe
python build_exe.py
```

The executable will be created at:

```
dist\PolyCryptoAlpha.exe
```

Size is typically ~150 MB because it bundles Python, ML libraries (LightGBM, XGBoost, scikit-learn), and all dependencies.

To run the .exe:

```bash
dist\PolyCryptoAlpha.exe --ui
```

## License

MIT
