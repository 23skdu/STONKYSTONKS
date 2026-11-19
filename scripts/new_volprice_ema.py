#!/usr/bin/env python3
"""Plot the close-price/volume ratio together with simple moving averages.

Example:
    python -m scripts new_volprice_ema NVDA
    python scripts/new_volprice_ema.py NVDA --period 2y --no-show
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

import matplotlib.pyplot as plt

try:  # Imported as "python -m scripts new_volprice_ema" or "from scripts import ..."
    from scripts.marketdata import download
except ModuleNotFoundError:  # Executed as "python scripts/new_volprice_ema.py"
    from marketdata import download

__all__ = ["MOVING_AVERAGES", "analyze", "main"]

#: Moving-average windows (in trading days) computed and plotted.
MOVING_AVERAGES: tuple[int, ...] = (25, 50, 100, 200)

PLOT_COLOURS = {
    "Price/Volume": "blue",
    "MA25": "red",
    "MA50": "green",
    "MA100": "orange",
    "MA200": "purple",
}


def analyze(ticker: str, show_plot: bool = True, *, period: str = "1y"):
    """Download ``ticker`` history, add the ratio/MAs to it and plot them."""
    data = download(ticker, period=period)

    data["Price/Volume"] = data["Close"] / data["Volume"]
    for window in MOVING_AVERAGES:
        # Equivalent to talib.SMA(..., timeperiod=N) without the C dependency.
        data[f"MA{window}"] = data["Close"].rolling(window=window, min_periods=window).mean()

    plt.figure(figsize=(14, 7))
    for column in ["Price/Volume", *(f"MA{window}" for window in MOVING_AVERAGES)]:
        plt.plot(data.index, data[column], label=column, color=PLOT_COLOURS[column])

    plt.title(f"Price/Volume and Moving Averages for {ticker}")
    plt.xlabel("Date")
    plt.ylabel("Price/Volume")
    plt.legend()
    plt.grid()
    if show_plot:
        plt.show()
    return data


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line wrapper around :func:`analyze`."""
    parser = argparse.ArgumentParser(
        prog="new_volprice_ema",
        description="Plot price/volume ratio with 25/50/100/200-day moving averages.",
    )
    parser.add_argument("ticker", help="Ticker symbol, for example NVDA")
    parser.add_argument("--period", default="1y", help="History window understood by yfinance (default: 1y)")
    parser.add_argument(
        "--no-show", action="store_true", help="Compute and return data without opening a plot"
    )
    args = parser.parse_args(argv)
    analyze(args.ticker, show_plot=not args.no_show, period=args.period)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
