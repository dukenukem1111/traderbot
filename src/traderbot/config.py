"""Configuration helpers for the trader bot."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional
import json
import os


@dataclass
class TradingConfig:
    """Container for configuration settings.

    Parameters
    ----------
    symbol:
        Ticker symbol that the bot trades.
    cash:
        Initial cash for backtests.
    fast_window, slow_window:
        Window sizes for the moving average strategy.
    data_source:
        Source for historical data ("alpaca" or "csv").
    csv_data_path:
        Optional path to a CSV file containing OHLCV data.
    alpaca_api_key, alpaca_secret_key:
        Credentials for Alpaca. Leave ``None`` when running purely locally.
    alpaca_base_url:
        Base URL for the Alpaca trading API.
    alpaca_data_url:
        Base URL for Alpaca's market data API.
    use_paper:
        Toggle between Alpaca's paper trading and live trading endpoints.
    poll_interval:
        How often (in seconds) the live bot polls for new bar data.
    """

    symbol: str = "AAPL"
    cash: float = 10_000.0
    fast_window: int = 12
    slow_window: int = 26
    data_source: str = "csv"
    csv_data_path: Optional[Path] = None
    alpaca_api_key: Optional[str] = None
    alpaca_secret_key: Optional[str] = None
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    alpaca_data_url: str = "https://data.alpaca.markets/v2"
    use_paper: bool = True
    poll_interval: int = 60
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> "TradingConfig":
        """Create a configuration instance using environment variables.

        The method honours the following environment variables when they are
        available:

        ``TRADERBOT_SYMBOL``
            Overrides :attr:`symbol`.
        ``TRADERBOT_FAST_WINDOW`` and ``TRADERBOT_SLOW_WINDOW``
            Configure the moving average window sizes.
        ``TRADERBOT_DATA_SOURCE``
            Selects ``"csv"`` or ``"alpaca"``.
        ``TRADERBOT_CSV_PATH``
            Points to a CSV file used for backtesting.
        ``ALPACA_API_KEY`` and ``ALPACA_SECRET_KEY``
            Supply credentials for live or paper trading.
        ``ALPACA_BASE_URL`` and ``ALPACA_DATA_URL``
            Allow overriding the default endpoints.
        """

        defaults = cls()
        csv_path = os.getenv("TRADERBOT_CSV_PATH")
        return cls(
            symbol=os.getenv("TRADERBOT_SYMBOL", defaults.symbol),
            cash=float(os.getenv("TRADERBOT_CASH", defaults.cash)),
            fast_window=int(os.getenv("TRADERBOT_FAST_WINDOW", defaults.fast_window)),
            slow_window=int(os.getenv("TRADERBOT_SLOW_WINDOW", defaults.slow_window)),
            data_source=os.getenv("TRADERBOT_DATA_SOURCE", defaults.data_source),
            csv_data_path=Path(csv_path) if csv_path else None,
            alpaca_api_key=os.getenv("ALPACA_API_KEY"),
            alpaca_secret_key=os.getenv("ALPACA_SECRET_KEY"),
            alpaca_base_url=os.getenv("ALPACA_BASE_URL", defaults.alpaca_base_url),
            alpaca_data_url=os.getenv("ALPACA_DATA_URL", defaults.alpaca_data_url),
            use_paper=os.getenv("TRADERBOT_USE_PAPER", "true").lower() != "false",
            poll_interval=int(os.getenv("TRADERBOT_POLL_INTERVAL", defaults.poll_interval)),
        )

    @classmethod
    def from_json(cls, path: Path) -> "TradingConfig":
        """Load configuration values from a JSON file."""

        with Path(path).expanduser().open("r", encoding="utf-8") as handle:
            payload: Dict[str, Any] = json.load(handle)
        csv_path = payload.get("csv_data_path")
        payload["csv_data_path"] = Path(csv_path) if csv_path else None
        extra = payload.pop("extra", {})
        config = cls(**payload)
        config.extra.update(extra)
        return config

    def to_json(self, path: Path) -> None:
        """Persist the configuration to ``path``."""

        payload = self.__dict__.copy()
        csv_path = payload.pop("csv_data_path")
        payload["csv_data_path"] = str(csv_path) if csv_path else None
        with Path(path).expanduser().open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def require_alpaca_credentials(self) -> None:
        """Raise ``RuntimeError`` if the Alpaca credentials are missing."""

        if not self.alpaca_api_key or not self.alpaca_secret_key:
            raise RuntimeError(
                "Alpaca credentials are required for live trading. Set the "
                "ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables or "
                "provide them through a configuration file."
            )


__all__ = ["TradingConfig"]
