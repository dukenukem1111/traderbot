"""Backtesting utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np
import pandas as pd

from .strategies import MovingAverageCrossStrategy


@dataclass
class BacktestResult:
    signals: pd.DataFrame
    returns: pd.Series
    equity_curve: pd.Series
    metrics: Dict[str, float]


class Backtester:
    """Execute a vectorised backtest for a trading strategy."""

    def __init__(
        self,
        initial_cash: float = 10_000.0,
        commission: float = 0.0,
        slippage: float = 0.0,
        trading_days: int = 252,
    ) -> None:
        self.initial_cash = float(initial_cash)
        self.commission = float(commission)
        self.slippage = float(slippage)
        self.trading_days = trading_days

    def run(self, data: pd.DataFrame, strategy: Optional[MovingAverageCrossStrategy] = None) -> BacktestResult:
        """Backtest ``strategy`` on ``data``.

        Parameters
        ----------
        data:
            Dataframe containing at least a ``close`` column.
        strategy:
            Strategy instance, defaults to :class:`MovingAverageCrossStrategy` with
            the values stored on ``data``.
        """

        if "close" not in data:
            raise ValueError("Price data must contain a 'close' column")

        if strategy is None:
            strategy = MovingAverageCrossStrategy()

        signals = strategy.generate_signals(data["close"])
        returns = data["close"].pct_change().fillna(0.0)
        position = signals["signal"].shift(1).fillna(0.0)
        strat_returns = position * returns

        if self.slippage:
            strat_returns -= position.diff().abs().fillna(0.0) * self.slippage

        equity_curve = (1.0 + strat_returns).cumprod() * self.initial_cash

        if self.commission:
            trades = signals["positions"].abs().cumsum()
            equity_curve -= trades * self.commission

        metrics = self._compute_metrics(strat_returns, equity_curve)
        return BacktestResult(
            signals=signals,
            returns=strat_returns,
            equity_curve=equity_curve,
            metrics=metrics,
        )

    def _compute_metrics(self, returns: pd.Series, equity_curve: pd.Series) -> Dict[str, float]:
        annualised_return = (equity_curve.iloc[-1] / self.initial_cash) ** (
            self.trading_days / len(equity_curve)
        ) - 1 if len(equity_curve) else 0.0
        total_return = equity_curve.iloc[-1] / self.initial_cash - 1 if len(equity_curve) else 0.0
        volatility = returns.std() * np.sqrt(self.trading_days)
        sharpe = returns.mean() / returns.std() * np.sqrt(self.trading_days) if returns.std() != 0 else 0.0
        drawdown = (equity_curve / equity_curve.cummax() - 1.0).min() if len(equity_curve) else 0.0
        return {
            "annualised_return": float(annualised_return),
            "total_return": float(total_return),
            "volatility": float(volatility) if not np.isnan(volatility) else 0.0,
            "sharpe": float(sharpe) if not np.isnan(sharpe) else 0.0,
            "max_drawdown": float(drawdown) if not np.isnan(drawdown) else 0.0,
        }


__all__ = ["Backtester", "BacktestResult"]
