#!/usr/bin/env python3
"""Calculate descriptive statistics for numbers read from standard input.

Examples:
    printf "1\\n2\\n3\\n4\\n5\\n" | python -m scripts stats
    python scripts/stats.py < data/series.txt
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Sequence

import numpy as np
from scipy.stats import kurtosis, skew

__all__ = ["calculate_stats", "main"]


def calculate_stats(data: Iterable[float]) -> dict[str, float]:
    """Return descriptive statistics for the values in ``data``.

    The result contains quartiles, Fibonacci retracement levels, moments and a
    few dispersion measures, all as plain floats keyed by a human readable
    label.
    """
    values = np.asarray(list(data), dtype=float)
    if values.size == 0:
        raise ValueError("at least one data point is required")

    mean = float(np.mean(values))
    with np.errstate(divide="ignore", invalid="ignore"):
        inverse_sum = float(np.sum(1.0 / values))
    harmonic_mean = float(values.size / inverse_sum) if inverse_sum else float("nan")

    return {
        "Min": float(np.min(values)),
        "23.6% Fibonacci": float(np.percentile(values, 23.6)),
        "1st Quartile": float(np.percentile(values, 25)),
        "38.2% Fibonacci": float(np.percentile(values, 38.2)),
        "Median": float(np.median(values)),
        "Mean": mean,
        "HarmonicMean": harmonic_mean,
        "61.8% Fibonacci": float(np.percentile(values, 61.8)),
        "3rd Quartile": float(np.percentile(values, 75)),
        "78.6% Fibonacci": float(np.percentile(values, 78.6)),
        "Max": float(np.max(values)),
        "Standard Deviation": float(np.std(values)),
        "Kurtosis": float(kurtosis(values)),
        "Skew": float(skew(values)),
        "Average Deviation": float(np.mean(np.abs(values - mean))),
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Read numbers from stdin and print their descriptive statistics."""
    argparse.ArgumentParser(
        prog="stats",
        description="Read one number per line from stdin and print descriptive statistics.",
    ).parse_args(argv)

    data = [float(line) for line in sys.stdin if line.strip()]
    try:
        results = calculate_stats(data)
    except ValueError as exc:
        print(f"stats: {exc}", file=sys.stderr)
        return 2

    for name, value in results.items():
        print(f"{name}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
