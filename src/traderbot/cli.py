"""Command line interface for the trader bot."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from .config import TradingConfig
from .trading_bot import TradingBot


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Traderbot CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backtest = subparsers.add_parser("backtest", help="Run a backtest")
    backtest.add_argument("--config", type=Path, help="Path to JSON configuration file")
    backtest.add_argument("--csv", type=Path, help="CSV data path")

    live = subparsers.add_parser("live", help="Start live trading against Alpaca")
    live.add_argument("--config", type=Path, help="Path to JSON configuration file")
    live.add_argument("--timeframe", default="1Day", help="Bar timeframe, e.g. 1Min, 1Day")
    live.add_argument("--lookback", type=int, default=200, help="Number of bars for signal evaluation")
    live.add_argument("--iterations", type=int, help="Limit the number of iterations for testing")

    return parser


def run_backtest(bot: TradingBot) -> None:
    result = bot.backtest()
    print("Backtest complete")
    print("=================")
    for key, value in result.metrics.items():
        print(f"{key:>20}: {value:.4f}")


def run_live(bot: TradingBot, timeframe: str, lookback: int, iterations: Optional[int]) -> None:
    bot.start_live_trading(timeframe=timeframe, lookback=lookback, max_iterations=iterations)


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.config:
        config = TradingConfig.from_json(args.config)
    else:
        config = TradingConfig.from_env()

    csv_path = getattr(args, "csv", None)
    if csv_path:
        config.csv_data_path = csv_path
        config.data_source = "csv"

    bot = TradingBot(config)

    if args.command == "backtest":
        run_backtest(bot)
    elif args.command == "live":
        run_live(bot, args.timeframe, args.lookback, args.iterations)


if __name__ == "__main__":  # pragma: no cover - manual invocation
    main()
