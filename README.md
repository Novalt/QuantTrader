# QuantTrader — Quantitative Trading System 🚀

> End-to-end quantitative trading pipeline: data collection, processing, strategy execution, and backtesting.

## Overview

A professional quantitative trading system that automates the complete research-to-execution workflow. Integrates multiple financial data sources with a modular strategy layer and comprehensive backtesting framework.

## Features

| Module | Description |
|--------|-------------|
| **Data Collection** | Alpha Vantage, FRED, Forex real-time feeds |
| **Processing** | Technical indicators, feature engineering |
| **Strategies** | Moving Average, RSI, MACD with signal generation |
| **Backtesting** | Sharpe ratio, drawdown, win rate, P&L metrics |
| **Automation** | Full pipeline from data ingestion to order signals |

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/Novalt/quant_trader.git
cd quant_trader
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your API keys

# 3. Run
python main.py
```

## Configuration

```env
ALPHA_VANTAGE_KEY=your_key
FRED_API_KEY=your_key
```

## Project Structure

```
quant_trader/
├── pipelines/          # Data ingestion and processing
├── strategies/         # Trading strategy implementations
├── config/             # API keys and parameters
├── utils/              # Metrics and utility functions
└── data/               # Local data storage
```

## Backtesting Metrics

- Sharpe Ratio
- Maximum Drawdown
- Win Rate
- Total Return
- P&L by strategy

## Tech Stack

Python · Pandas · NumPy · Alpha Vantage API · FRED API · Matplotlib

---

# NovalQuant Core — Quantitative Infrastructure v1.0 🏗️

> Modular quantitative infrastructure for scalable research and systematic trading.

## Overview

A clean, modular foundation for building quantitative trading strategies. Separates data acquisition, research, and portfolio management into independent components designed for reuse and scalability.

## Architecture

```
novalquant-core/
│
├── core/
│   ├── downloader.py       # Raw data acquisition → data/raw/
│   ├── cleaner.py          # Data cleaning and standardization → data/clean/
│   └── utils.py            # Shared utility functions
│
├── research/
│   ├── pair_selection.py   # Cointegrated pair identification (JSON/CSV output)
│   ├── spread_analysis.py  # Spread calculation, thresholds, Z-score
│   ├── signal_generator.py # Trade signals from Z-score and thresholds
│   ├── backtester.py       # Strategy simulation and performance metrics
│   └── portfolio_manager.py # Multi-strategy/pair portfolio aggregation
│
└── data/
    ├── raw/                # Original downloaded data
    ├── clean/              # Processed and standardized data
    ├── pairs/              # Identified cointegrated pairs
    ├── spreads/            # Spread series and analysis
    ├── plots/              # Visualizations
    └── reports/            # Performance reports
```

## Design Principles

- **Separation of concerns** — each module has a single responsibility
- **Pipeline architecture** — outputs of each stage feed cleanly into the next
- **Research-first** — built to support hypothesis testing before live deployment
- **Extensible** — designed to plug in new strategies, data sources, or execution layers

## Usage

```python
from core.downloader import DataDownloader
from core.cleaner import DataCleaner
from research.pair_selection import PairSelector
from research.backtester import Backtester

# Download and clean
downloader = DataDownloader()
raw_data = downloader.fetch(tickers=["EURUSD", "GBPUSD", "AUDUSD"])

cleaner = DataCleaner()
clean_data = cleaner.process(raw_data)

# Research
selector = PairSelector()
pairs = selector.find_cointegrated(clean_data, confidence=0.95)

# Backtest
bt = Backtester()
results = bt.run(pairs, clean_data)
print(results.summary())
```

## Tech Stack

Python · Pandas · NumPy · Scipy · Statsmodels

---

*NovalQuant Core serves as the shared infrastructure powering QuantTrader and the Cointegration Portfolio Trading Platform.*
