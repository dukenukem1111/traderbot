"""Trading strategies."""

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass
class MovingAverageCrossStrategy:
    """Simple moving average cross-over strategy.

    The strategy goes long when the fast moving average crosses above the slow
    moving average and goes short when it crosses below. Signals are represented
    as integers: ``1`` for a long position, ``-1`` for a short position, and ``0``
    for neutral.
    """

    fast_window: int = 12
    slow_window: int = 26

    def __post_init__(self) -> None:
        if self.fast_window <= 0 or self.slow_window <= 0:
            raise ValueError("Moving average windows must be positive integers")
        if self.fast_window >= self.slow_window:
            raise ValueError("fast_window must be strictly smaller than slow_window")

    def generate_signals(self, prices: pd.Series) -> pd.DataFrame:
        """Return a dataframe containing moving average signals."""

        if prices.empty:
            raise ValueError("Price series must not be empty")

        signals = pd.DataFrame(index=prices.index)
        signals["price"] = prices
        signals["fast_ma"] = prices.rolling(window=self.fast_window).mean()
        signals["slow_ma"] = prices.rolling(window=self.slow_window).mean()

        signals["signal"] = 0
        signals.loc[signals["fast_ma"] > signals["slow_ma"], "signal"] = 1
        signals.loc[signals["fast_ma"] < signals["slow_ma"], "signal"] = -1
        signals["positions"] = signals["signal"].diff().fillna(0)
        return signals


__all__ = ["MovingAverageCrossStrategy"]
