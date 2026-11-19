"""Shared helpers for downloading and normalising market data from Yahoo Finance."""

from __future__ import annotations

from typing import Any

import pandas as pd
import yfinance as yf

__all__ = ["download"]


def download(ticker: str, **kwargs: Any) -> pd.DataFrame:
    """Download OHLCV history for ``ticker`` and return a single-level frame.

    ``yfinance`` returns MultiIndex columns (``('Close', 'AAPL')``) for some
    call patterns; the tools in this package always work on a plain
    ``(date, OHLCV)`` frame, so the ticker level is dropped here.

    Any keyword argument is forwarded to :func:`yfinance.download` (for example
    ``period="max"`` or ``start="2024-01-01"``). Download progress output is
    disabled by default.
    """
    kwargs.setdefault("progress", False)
    data = yf.download(ticker, **kwargs)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data
