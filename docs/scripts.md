# Tool reference

Every tool lives in [`scripts/`](../scripts) and can be invoked in two ways:

```bash
python -m scripts <tool> [options]   # preferred, single entry point
python scripts/<tool>.py [options]   # equivalent, direct execution
```

Inside the container the same entry point is used (`docker run --rm stonkystonks <tool> ...`).

| Tool                | Purpose |
| ------------------- | ------- |
| `stonky`            | Trains a small LSTM on historical close prices and forecasts future prices. |
| `stats`             | Descriptive statistics for numbers read from stdin. |
| `modeltest`         | Benchmarks classic scikit-learn classifiers on a synthetic dataset. |
| `new_volprice_ema`  | Price/volume ratio with 25/50/100/200-day moving averages. |
| `ytd_volprice`      | Year-to-date close price vs. volume on twin y-axes. |

Run `python -m scripts <tool> --help` for a tool's own options.

## `stonky` - LSTM price prediction

Downloads the full history of one or more tickers, trains a two-layer LSTM
(50 + 50 units, 100-day look-back, Adam/MAE-MSE) on the first 70% of the data,
reports the test RMSE and prints forecasts for 1/3/7/11/17/71 days ahead.

```bash
python -m scripts stonky NVDA                       # defaults: 100 epochs, saves the model
python -m scripts stonky NVDA MSFT --epochs 20 --no-save
python -m scripts stonky NVDA --time-step 60 --future-days 5 --model-dir models
```

Trained models are exported as TensorFlow SavedModels in `models/<TICKER>.tfmodel.100`
(created on demand, ignored by git - see `make clean`).

TensorFlow is chatty: `TF_CPP_MIN_LOG_LEVEL` is set to `3` before it is imported.

## `stats` - descriptive statistics

Reads one number per line from stdin and prints min/max, quartiles, Fibonacci
retracement levels (23.6 / 38.2 / 61.8 / 78.6), mean, median, harmonic mean,
standard deviation, kurtosis, skew and mean absolute deviation.

```bash
printf "1\n2\n3\n4\n5\n" | python -m scripts stats
python scripts/stats.py < data/series.txt
```

## `modeltest` - classifier benchmark

Generates a synthetic binary dataset (1000 x 20, fixed seed) and runs 5-fold
cross-validation for Logistic Regression, Decision Tree, Random Forest and SVM,
reporting accuracy, precision, recall and F1 on identical folds.

```bash
python -m scripts modeltest
```

## `new_volprice_ema` - price/volume ratio and moving averages

```bash
python -m scripts new_volprice_ema NVDA
python scripts/new_volprice_ema.py NVDA --period 2y --no-show
```

The moving averages are plain pandas rolling windows
(`rolling(N, min_periods=N).mean()`), which reproduces `talib.SMA(..., timeperiod=N)`
without requiring the TA-Lib C library.

## `ytd_volprice` - year-to-date price vs. volume

```bash
python -m scripts ytd_volprice NVDA
python scripts/ytd_volprice.py NVDA --start 2025-01-01 --no-show
```

The start date defaults to the first day of the current year.

## Shared market data helper

`scripts/marketdata.py` wraps `yfinance.download()` for every tool: progress
output is disabled by default and MultiIndex columns (`('Close', 'AAPL')`) are
flattened to a plain OHLCV frame, so the tools behave the same across
yfinance versions.
