#!/usr/bin/env python3
"""Plot year-to-date close price and volume for a ticker on twin y-axes.

Example:
    python -m scripts ytd_volprice NVDA
    python scripts/ytd_volprice.py NVDA --start 2025-01-01 --no-show
"""

from __future__ import annotations

import argparse
import datetime as dt
from collections.abc import Sequence

import matplotlib.pyplot as plt

try:  # Imported as "python -m scripts ytd_volprice" or "from scripts import ..."
    from scripts.marketdata import download
except ModuleNotFoundError:  # Executed as "python scripts/ytd_volprice.py"
    from marketdata import download

__all__ = ["analyze", "main"]


def default_start() -> str:
    """Return the first day of the current year (``YYYY-01-01``)."""
    return f"{dt.date.today().year}-01-01"


def analyze(ticker: str, show_plot: bool = True, *, start: str | None = None):
    """Download YTD history for ``ticker`` and plot price vs. volume."""
    data = download(ticker, start=start or default_start())

    fig, ax1 = plt.subplots()
    price_colour = "tab:blue"
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Close", color=price_colour)
    ax1.plot(data.index, data["Close"], color=price_colour)
    ax1.tick_params(axis="y", labelcolor=price_colour)

    ax2 = ax1.twinx()
    volume_colour = "tab:red"
    ax2.set_ylabel("Volume", color=volume_colour)
    ax2.plot(data.index, data["Volume"], color=volume_colour)
    ax2.tick_params(axis="y", labelcolor=volume_colour)

    fig.tight_layout()
    if show_plot:
        plt.show()
    return data


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line wrapper around :func:`analyze`."""
    parser = argparse.ArgumentParser(
        prog="ytd_volprice",
        description="Plot year-to-date close price and volume for a ticker.",
    )
    parser.add_argument("ticker", help="Ticker symbol, for example NVDA")
    parser.add_argument(
        "--start",
        default=default_start(),
        help="First date to download (default: first day of the current year)",
    )
    parser.add_argument(
        "--no-show", action="store_true", help="Compute and return data without opening a plot"
    )
    args = parser.parse_args(argv)
    analyze(args.ticker, show_plot=not args.no_show, start=args.start)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
