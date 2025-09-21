import pandas as pd
import pytest

from traderbot.strategies import MovingAverageCrossStrategy


def test_generate_signals_produces_columns():
    dates = pd.date_range("2022-01-01", periods=50, freq="D")
    prices = pd.Series(range(50), index=dates, dtype=float)

    strategy = MovingAverageCrossStrategy(fast_window=5, slow_window=10)
    signals = strategy.generate_signals(prices)

    assert set(["price", "fast_ma", "slow_ma", "signal", "positions"]).issubset(signals.columns)
    assert signals["signal"].isin([-1, 0, 1]).all()


def test_invalid_windows_raise():
    with pytest.raises(ValueError):
        MovingAverageCrossStrategy(fast_window=10, slow_window=5)

    with pytest.raises(ValueError):
        MovingAverageCrossStrategy(fast_window=0, slow_window=5)
