# Traderbot

Traderbot is a small Python project that demonstrates how to research a trading
strategy, backtest it locally, and then execute the same logic against a real or
paper trading account on [Alpaca](https://alpaca.markets/). The repository ships
with a simple moving-average cross-over strategy, tooling for loading historical
price data, a vectorised backtester, and a thin wrapper around Alpaca's trading
API for live deployment.

> **Warning**
> This project is for educational use only. Algorithmic trading involves risk and
> you are solely responsible for any losses that may occur when trading a live
> account.

## Project layout

```
.
├── data/                 # Sample OHLCV data for quick experimentation
├── src/traderbot/        # Python package with backtesting and live trading code
├── tests/                # Automated tests covering the core components
└── pyproject.toml        # Packaging metadata and dependencies
```

## Installation

Create a virtual environment (optional but recommended) and install the project
in editable mode along with the development dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

If you intend to connect to Alpaca for paper or live trading install the
optional dependency as well:

```bash
pip install -e .[live]
```

## Backtesting

The `traderbot` package ships with a command line interface. To backtest the
moving-average strategy using the bundled CSV sample run:

```bash
traderbot backtest --csv data/sample_prices.csv
```

You can also create a configuration file (`config.json`) to override the default
parameters:

```json
{
  "symbol": "AAPL",
  "cash": 10000,
  "fast_window": 5,
  "slow_window": 20,
  "data_source": "csv",
  "csv_data_path": "data/sample_prices.csv"
}
```

The configuration file can be passed to the CLI with `--config config.json`. The
same configuration file is used for live trading.

## Live trading with Alpaca

1. Create an account on [Alpaca](https://alpaca.markets/).
2. Generate API keys for either paper trading or live trading.
3. Export the credentials as environment variables:

   ```bash
   export ALPACA_API_KEY="your-key"
   export ALPACA_SECRET_KEY="your-secret"
   export TRADERBOT_SYMBOL="AAPL"
   export TRADERBOT_FAST_WINDOW=5
   export TRADERBOT_SLOW_WINDOW=20
   ```

4. Start the trader in paper trading mode:

   ```bash
   traderbot live --timeframe 1Day --lookback 200
   ```

   The optional `--iterations` flag limits the number of polling iterations for
   testing. Omit it to keep the process running indefinitely.

The live integration uses Alpaca's `alpaca-py` client. The bot polls Alpaca for
recent bars, computes the moving-average signal, and places market orders to
rebalance the portfolio so that it is either fully invested (long) or in cash.

## Development

Run the automated tests with:

```bash
pytest
```

Key modules to explore:

- `traderbot.config.TradingConfig`: configuration container that can load from
  environment variables or JSON files.
- `traderbot.strategies.MovingAverageCrossStrategy`: the moving average crossover
  signal generator.
- `traderbot.backtest.Backtester`: vectorised backtester that computes equity
  curves and summary statistics.
- `traderbot.live.AlpacaPaperTrader`: minimal live trading integration with
  Alpaca's API.

Feel free to experiment with alternative strategies or integrate additional data
sources.
