from pathlib import Path

import pytest

from traderbot.config import TradingConfig


def test_from_env(monkeypatch):
    monkeypatch.setenv("TRADERBOT_SYMBOL", "MSFT")
    monkeypatch.setenv("TRADERBOT_CASH", "5000")
    monkeypatch.setenv("TRADERBOT_FAST_WINDOW", "5")
    monkeypatch.setenv("TRADERBOT_SLOW_WINDOW", "20")
    config = TradingConfig.from_env()

    assert config.symbol == "MSFT"
    assert config.cash == 5000
    assert config.fast_window == 5
    assert config.slow_window == 20


def test_json_roundtrip(tmp_path: Path):
    config = TradingConfig(symbol="AAPL", csv_data_path=Path("data/sample_prices.csv"))
    config.extra["foo"] = "bar"
    path = tmp_path / "config.json"
    config.to_json(path)

    restored = TradingConfig.from_json(path)
    assert restored.symbol == config.symbol
    assert restored.csv_data_path == config.csv_data_path
    assert restored.extra["foo"] == "bar"
