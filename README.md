# Crypto Risk–Return Report (SOL vs SUI vs ETH)

Reproducible risk–return analytics using daily Binance klines (1d, last ~1000 days).
Metrics: rolling annualized volatility (30/90/180), CAGR, Max Drawdown, Sortino, Calmar, VaR/CVaR(95), liquidity (Amihud 30D, 30D avg $volume).

## Data Window
- Source: Binance `/api/v3/klines`, `interval=1d`, `limit=1000` (~last 2.7 years).
- Volatility: rolling windows of 30/90/180 **ending at the last date**.
- CAGR/Sortino/Calmar/MDD/VaR/CVaR/Beta: **entire available window** (~1000 days).
- Liquidity: Amihud **30D rolling** (last point) + 30D average dollar volume.

## Quickstart
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 1) Fetch data
python scripts/fetch.py --symbol SOLUSDT
python scripts/fetch.py --symbol SUIUSDT
python scripts/fetch.py --symbol ETHUSDT

# 2) Compute metrics
python scripts/compute_metrics.py --config config.yaml

# 3) Make figures
python scripts/make_figures.py --symbols SOLUSDT SUIUSDT ETHUSDT
