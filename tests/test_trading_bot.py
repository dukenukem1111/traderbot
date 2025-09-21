from pathlib import Path

from traderbot.config import TradingConfig
from traderbot.trading_bot import TradingBot


def test_backtest_with_csv_data():
    config = TradingConfig(
        symbol="AAPL",
        cash=5_000,
        fast_window=3,
        slow_window=5,
        data_source="csv",
        csv_data_path=Path("data/sample_prices.csv"),
    )
    bot = TradingBot(config)
    result = bot.backtest()
    assert result.equity_curve.iloc[-1] > 0
