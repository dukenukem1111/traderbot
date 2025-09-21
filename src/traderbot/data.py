"""Data loading utilities."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Union

import pandas as pd

from .config import TradingConfig


def load_csv_data(path: Union[str, Path], tz: Optional[str] = None) -> pd.DataFrame:
    """Load OHLCV data from ``path`` and return a normalised dataframe.

    The CSV file is expected to contain columns labelled ``open``, ``high``,
    ``low``, ``close``, and ``volume``. A timestamp column is detected
    automatically and converted into the index.
    """

    data = pd.read_csv(path)
    timestamp_column = _detect_timestamp_column(data.columns)
    if timestamp_column is None:
        raise ValueError("CSV data must include a timestamp column.")

    data[timestamp_column] = pd.to_datetime(data[timestamp_column], utc=tz is None)
    if tz:
        data[timestamp_column] = data[timestamp_column].dt.tz_convert(tz)

    frame = data.set_index(timestamp_column)
    expected = {"open", "high", "low", "close", "volume"}
    if missing := expected.difference(frame.columns.str.lower()):
        raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

    frame = frame.rename(columns=str.lower)
    return frame[["open", "high", "low", "close", "volume"]]


def _detect_timestamp_column(columns: Iterable[str]) -> Optional[str]:
    for name in columns:
        lower = name.lower()
        if lower in {"timestamp", "time", "date"}:
            return name
    return None


def fetch_alpaca_data(
    config: TradingConfig,
    start: Union[str, datetime],
    end: Union[str, datetime],
    timeframe: Union[str, "TimeFrame"],
) -> pd.DataFrame:
    """Download historical bars from Alpaca using ``alpaca-py``.

    This helper requires that :mod:`alpaca-py` is installed. The dependency is
    optional because it is only necessary when requesting live Alpaca data. The
    resulting dataframe is indexed by timestamp and contains ``open`` ``high``
    ``low`` ``close`` ``volume`` columns.
    """

    try:
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockBarsRequest
        from alpaca.data.timeframe import TimeFrame
    except ImportError as exc:  # pragma: no cover - exercised in live usage
        raise ImportError(
            "fetch_alpaca_data requires the 'alpaca-py' package. Install it with "
            "pip install traderbot[live] or pip install alpaca-py"
        ) from exc

    config.require_alpaca_credentials()

    client = StockHistoricalDataClient(config.alpaca_api_key, config.alpaca_secret_key)
    timeframe_obj = _coerce_timeframe(timeframe)
    request = StockBarsRequest(
        symbol_or_symbols=config.symbol,
        timeframe=timeframe_obj,
        start=start,
        end=end,
    )
    bars = client.get_stock_bars(request)
    frame = bars.df
    if isinstance(frame.index, pd.MultiIndex):
        # Alpaca returns a MultiIndex with symbol as the first level.
        frame = frame.xs(config.symbol, level="symbol")
    return frame[["open", "high", "low", "close", "volume"]]


def _coerce_timeframe(timeframe: Union[str, "TimeFrame"]) -> "TimeFrame":
    try:
        from alpaca.data.timeframe import TimeFrame
    except ImportError:  # pragma: no cover - handled when calling fetch_alpaca_data
        raise

    if isinstance(timeframe, TimeFrame):
        return timeframe

    mapping = {
        "1min": TimeFrame.Minute,
        "5min": TimeFrame(5, "Min"),
        "15min": TimeFrame(15, "Min"),
        "1h": TimeFrame.Hour,
        "1day": TimeFrame.Day,
    }
    key = timeframe.lower() if isinstance(timeframe, str) else timeframe
    if key in mapping:
        return mapping[key]
    raise ValueError(f"Unsupported timeframe: {timeframe!r}")


__all__ = ["load_csv_data", "fetch_alpaca_data"]
