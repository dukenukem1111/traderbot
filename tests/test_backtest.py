from pathlib import Path

import pandas as pd
import pytest

from traderbot.backtest import Backtester
from traderbot.strategies import MovingAverageCrossStrategy


def load_sample_data() -> pd.DataFrame:
    path = Path("data/sample_prices.csv")
    data = pd.read_csv(path, parse_dates=["timestamp"]).set_index("timestamp")
    return data


def test_backtester_runs_and_computes_metrics():
    data = load_sample_data()
    strategy = MovingAverageCrossStrategy(fast_window=3, slow_window=5)
    tester = Backtester(initial_cash=1_000)
    result = tester.run(data, strategy)

    assert not result.equity_curve.empty
    assert result.metrics["total_return"] == pytest.approx(result.equity_curve.iloc[-1] / tester.initial_cash - 1)
    assert all(key in result.metrics for key in ["annualised_return", "sharpe", "max_drawdown"])
