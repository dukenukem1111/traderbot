"""High level orchestration for the trader bot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd

from .backtest import Backtester, BacktestResult
from .config import TradingConfig
from .data import fetch_alpaca_data, load_csv_data
from .live import AlpacaPaperTrader
from .strategies import MovingAverageCrossStrategy


@dataclass
class TradingBot:
    config: TradingConfig
    strategy: Optional[MovingAverageCrossStrategy] = None

    def __post_init__(self) -> None:
        if self.strategy is None:
            self.strategy = MovingAverageCrossStrategy(
                fast_window=self.config.fast_window,
                slow_window=self.config.slow_window,
            )

    def load_data(self) -> pd.DataFrame:
        if self.config.data_source == "csv":
            if not self.config.csv_data_path:
                raise ValueError("csv_data_path must be set when data_source='csv'")
            return load_csv_data(self.config.csv_data_path)
        if self.config.data_source == "alpaca":
            start = self.config.extra.get("start")
            end = self.config.extra.get("end")
            timeframe = self.config.extra.get("timeframe", "1Day")
            if start is None or end is None:
                end_dt = datetime.utcnow()
                start_dt = end_dt - timedelta(days=365)
                start, end = start_dt.isoformat(), end_dt.isoformat()
            return fetch_alpaca_data(self.config, start=start, end=end, timeframe=timeframe)
        raise ValueError(f"Unsupported data_source: {self.config.data_source}")

    def backtest(self, data: Optional[pd.DataFrame] = None) -> BacktestResult:
        frame = data if data is not None else self.load_data()
        tester = Backtester(initial_cash=self.config.cash)
        return tester.run(frame, strategy=self.strategy)

    def start_live_trading(
        self,
        timeframe: str = "1Day",
        lookback: int = 200,
        max_iterations: Optional[int] = None,
        sleep: bool = True,
    ) -> None:
        trader = AlpacaPaperTrader(self.config)
        trader.run(
            strategy=self.strategy,
            timeframe=timeframe,
            lookback=lookback,
            max_iterations=max_iterations,
            sleep=sleep,
        )


__all__ = ["TradingBot"]
