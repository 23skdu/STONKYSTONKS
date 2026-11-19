#!/usr/bin/env python3
"""Train a small LSTM on a ticker's close price and print future predictions.

Example:
    python -m scripts stonky NVDA --epochs 100 --time-step 100
    python scripts/stonky.py NVDA MSFT --no-save
"""

from __future__ import annotations

import argparse
import os
from collections.abc import Sequence
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")  # Must be set before TensorFlow is imported.

# yfinance (and its curl_cffi transport) MUST be imported before TensorFlow:
# once TensorFlow's native libraries are loaded first, curl_cffi's browser
# impersonation stops working and every Yahoo download fails with
# "ImpersonateError: Impersonating chromeXXX is not supported".
# Enforced by tests/test_stonky.py::TestImportOrder.
try:  # Imported as "python -m scripts stonky" or "from scripts import ..."
    from scripts.marketdata import download
except ModuleNotFoundError:  # Executed as "python scripts/stonky.py"
    from marketdata import download

import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential

tf.get_logger().setLevel("ERROR")

__all__ = ["create_dataset", "main", "predict_next_days", "train_and_predict"]

DEFAULT_TICKERS: tuple[str, ...] = ("NVDA",)
DEFAULT_TIME_STEP = 100
DEFAULT_EPOCHS = 100
DEFAULT_MODEL_DIR = "models"
TRAIN_SPLIT = 0.7


def create_dataset(dataset: np.ndarray, time_step: int = DEFAULT_TIME_STEP) -> tuple[np.ndarray, np.ndarray]:
    """Turn a 2-D scaled series into sliding-window ``(X, y)`` training pairs."""
    x, y = [], []
    for i in range(len(dataset) - time_step - 1):
        x.append(dataset[i : i + time_step, 0])
        y.append(dataset[i + time_step, 0])
    return np.array(x), np.array(y)


def predict_next_days(
    model,
    last_data: np.ndarray,
    scaler: MinMaxScaler,
    n_days: int,
    time_step: int,
) -> np.ndarray:
    """Forecast ``n_days`` ahead by feeding each prediction back into the model.

    ``last_data`` and the model output are assumed to live in scaled space; the
    returned values are inverse-transformed back to the original price scale.
    """
    window = list(np.asarray(last_data).reshape(-1)[-time_step:])
    scaled_predictions: list[float] = []
    for _ in range(n_days):
        x_input = np.asarray(window[-time_step:]).reshape(1, -1, 1)
        next_day_pred = float(model.predict(x_input, verbose=0)[0][0])
        window.append(next_day_pred)
        scaled_predictions.append(next_day_pred)

    return scaler.inverse_transform(np.asarray(scaled_predictions).reshape(-1, 1)).flatten()


def _save_model(model, path: Path) -> None:
    """Export a trained model as a TensorFlow SavedModel directory.

    Keras 3 exposes :meth:`Model.export`; older Keras versions fall back to
    :func:`tf.saved_model.save`.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(model, "export"):
        model.export(str(path))
    else:
        tf.saved_model.save(model, str(path))


def train_and_predict(
    stocks: Sequence[str] = DEFAULT_TICKERS,
    time_step: int = DEFAULT_TIME_STEP,
    future_days: int = 1,
    epochs: int = DEFAULT_EPOCHS,
    save_model: bool = True,
    model_dir: str | Path = DEFAULT_MODEL_DIR,
) -> dict[str, np.ndarray]:
    """Train one LSTM per ticker and print predictions for several horizons."""
    predictions: dict[str, np.ndarray] = {}
    horizons = tuple(dict.fromkeys(future_days + offset for offset in (0, 2, 6, 10, 16, 70)))

    for ticker in stocks:
        print(ticker)
        data = download(ticker, period="max")
        if data.empty:
            print(f"No data fetched for {ticker}. Skipping.")
            continue

        data = data[["Close"]].copy()
        rows = len(data)
        print(f"Rows: {rows}")
        print(data.iloc[-1].to_string())
        data.ffill(inplace=True)

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data)
        split = int(len(scaled_data) * TRAIN_SPLIT)
        train_data, test_data = scaled_data[:split], scaled_data[split:]

        x_train, y_train = create_dataset(train_data, time_step)
        x_test, y_test = create_dataset(test_data, time_step)
        if len(x_train) == 0 or len(x_test) == 0:
            print(
                f"Not enough history for {ticker}: each split needs more than {time_step + 1} rows. Skipping."
            )
            continue
        x_train = x_train.reshape(x_train.shape[0], x_train.shape[1], 1)
        x_test = x_test.reshape(x_test.shape[0], x_test.shape[1], 1)

        model = Sequential(
            [
                keras.Input(shape=(time_step, 1)),
                LSTM(50, return_sequences=True),
                LSTM(50, return_sequences=False),
                Dense(1),
            ]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")
        model.fit(x_train, y_train, batch_size=64, epochs=epochs, verbose=0)

        if save_model:
            _save_model(model, Path(model_dir) / f"{ticker}.tfmodel.100")

        test_predictions = scaler.inverse_transform(model.predict(x_test, verbose=0))
        rmse = float(
            np.sqrt(mean_squared_error(scaler.inverse_transform(y_test.reshape(-1, 1)), test_predictions))
        )
        print(f"Test RMSE: {rmse:.4f}")

        for horizon in horizons:
            future = predict_next_days(model, scaled_data, scaler, horizon, time_step)
            predictions[f"{ticker}+{horizon}"] = future
            print(f"Prediction ({ticker}, +{horizon}d): {future}")

    return predictions


def main(argv: Sequence[str] | None = None) -> int:
    """Command-line wrapper around :func:`train_and_predict`."""
    parser = argparse.ArgumentParser(
        prog="stonky",
        description="Train an LSTM on historical close prices and forecast future prices.",
    )
    parser.add_argument(
        "tickers", nargs="*", default=list(DEFAULT_TICKERS), help="Ticker symbols (default: NVDA)"
    )
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS, help="Training epochs (default: 100)")
    parser.add_argument(
        "--time-step",
        type=int,
        default=DEFAULT_TIME_STEP,
        help="Look-back window in days (default: 100)",
    )
    parser.add_argument(
        "--future-days",
        type=int,
        default=1,
        help="Base forecast horizon in days (default: 1)",
    )
    parser.add_argument(
        "--model-dir",
        default=DEFAULT_MODEL_DIR,
        help=f"Directory for saved models (default: {DEFAULT_MODEL_DIR})",
    )
    parser.add_argument("--no-save", action="store_true", help="Skip writing the trained model to disk")
    args = parser.parse_args(argv)

    train_and_predict(
        stocks=args.tickers,
        time_step=args.time_step,
        future_days=args.future_days,
        epochs=args.epochs,
        save_model=not args.no_save,
        model_dir=args.model_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
