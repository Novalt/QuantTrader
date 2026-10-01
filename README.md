# QuantTrader

A Python pipeline for collecting market data, computing technical indicators and generating trading signals. Built as a learning and research project in quantitative finance.

> Research project. Not financial advice.

## What it does

- **Data collection:** pulls market data from Alpha Vantage and macroeconomic series from FRED.
- **Processing:** cleans the data and computes technical indicators (RSI, MACD and others).
- **Strategies:** a moving-average crossover strategy with parameter optimization, built on a reusable base class that handles signal validation, performance calculation and signal export.
- **Export:** writes the generated signals to CSV.
- **Scheduling:** can run the full pipeline on a schedule.

## Project structure

```
QuantTrader/
├── main.py           # Entry point: loads data, runs strategies, scheduled execution
├── config/           # Settings and API endpoint definitions
├── pipelines/        # Data client, collector and processor
├── strategies/       # Base strategy and moving-average strategy
├── utils/            # Technical indicators and signal exporter
├── check_env.py      # Environment and API key check
├── test_imports.py   # Import smoke test
└── test_api_endpoints.py
```

## Getting started

```bash
git clone https://github.com/Novalt/QuantTrader.git
cd QuantTrader
pip install -r requirements.txt
```

Create a `.env` file in the project root with your own API keys:

```
ALPHA_VANTAGE_KEY=your_key
FRED_API_KEY=your_key
```

Check the setup and run:

```bash
python check_env.py
python main.py
```

## Tech stack

Python, Pandas, NumPy, SciPy, Statsmodels, Alpha Vantage API, FRED API.

## Roadmap

- Add RSI and MACD strategies on top of the existing indicators
- Add a dedicated backtesting module with standard performance metrics
- Replace the smoke tests with unit tests

## Related

The cointegration-based research code lives in [Cointegration-Portfolio](https://github.com/Novalt/Cointegration-Portfolio) and the shared research infrastructure in [NovalQuant-Core](https://github.com/Novalt/NovalQuant-Core).
