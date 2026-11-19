import ast
import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock tensorflow before importing scripts.stonky (TensorFlow is not needed for these tests).
mock_tf = MagicMock()


class MockSequential:
    """Stand-in for keras.Sequential returning a batch-shaped constant prediction."""

    def __init__(self, *args, **kwargs):
        pass

    def add(self, layer):
        pass

    def compile(self, *args, **kwargs):
        pass

    def fit(self, *args, **kwargs):
        pass

    def predict(self, x_input, *args, **kwargs):
        return np.full((np.asarray(x_input).shape[0], 1), 0.5)


mock_tf.saved_model.save = MagicMock()
mock_tf.keras.models.Sequential = MockSequential
mock_tf.keras.layers.LSTM = MagicMock()
mock_tf.keras.layers.Dense = MagicMock()

sys.modules["tensorflow"] = mock_tf
sys.modules["tensorflow.keras"] = mock_tf.keras
sys.modules["tensorflow.keras.models"] = mock_tf.keras.models
sys.modules["tensorflow.keras.layers"] = mock_tf.keras.layers

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from scripts import stonky


class TestCreateDataset(unittest.TestCase):
    def test_create_dataset(self):
        data = np.arange(10, dtype=float).reshape(-1, 1)
        time_step = 3

        X, Y = stonky.create_dataset(data, time_step)

        self.assertEqual(len(X), 6)
        self.assertEqual(len(Y), 6)
        np.testing.assert_array_equal(X[0], [0.0, 1.0, 2.0])
        self.assertEqual(Y[0], 3.0)


class TestPredictNextDays(unittest.TestCase):
    def test_returns_one_value_per_requested_day(self):
        """The forecast loop must iterate ``n_days`` times (it used to return early)."""
        values = np.linspace(0.0, 1.0, 20).reshape(-1, 1)
        scaler = MinMaxScaler().fit(values)
        scaled = scaler.transform(values)

        predictions = stonky.predict_next_days(MockSequential(), scaled, scaler, n_days=5, time_step=4)

        self.assertEqual(len(predictions), 5)

    def test_predictions_are_inverse_transformed(self):
        values = np.linspace(50.0, 150.0, 20).reshape(-1, 1)
        scaler = MinMaxScaler().fit(values)
        scaled = scaler.transform(values)

        predictions = stonky.predict_next_days(MockSequential(), scaled, scaler, n_days=3, time_step=4)

        # The mock always predicts 0.5 in scaled space -> the midpoint of [50, 150].
        np.testing.assert_allclose(predictions, 100.0)


class TestImportOrder(unittest.TestCase):
    """Regression guard: yfinance must be imported before TensorFlow.

    Importing TensorFlow first breaks curl_cffi's browser impersonation, so
    every Yahoo download fails at run time with ``ImpersonateError`` - a bug
    that only shows up in a real (unmocked) run.
    """

    @staticmethod
    def _top_level_imports() -> list[str]:
        source = (Path(__file__).resolve().parents[1] / "scripts" / "stonky.py").read_text(encoding="utf-8")
        modules: list[str] = []
        for node in ast.parse(source).body:
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module or "")
            elif isinstance(node, ast.Try):  # the marketdata import fallback
                for branch in (node.body, node.orelse):
                    modules.extend(stmt.module or "" for stmt in branch if isinstance(stmt, ast.ImportFrom))
        return modules

    def test_marketdata_is_imported_before_tensorflow(self):
        modules = self._top_level_imports()
        marketdata = next((i for i, name in enumerate(modules) if name.endswith("marketdata")), None)
        tensorflow = next((i for i, name in enumerate(modules) if name == "tensorflow"), None)

        self.assertIsNotNone(marketdata, "stonky must import the yfinance helper")
        self.assertIsNotNone(tensorflow, "stonky must import tensorflow")
        self.assertLess(marketdata, tensorflow, "import yfinance (marketdata) before tensorflow")


class TestTrainAndPredict(unittest.TestCase):
    @patch("yfinance.download")
    def test_train_and_predict_integration(self, mock_download):
        dates = pd.date_range(start="2024-01-01", periods=120)
        mock_df = pd.DataFrame(
            {
                "Close": np.random.rand(120) * 100 + 50,
                "Volume": np.random.randint(1000, 10000, size=120),
            },
            index=dates,
        )
        mock_download.return_value = mock_df

        with redirect_stdout(StringIO()):
            predictions = stonky.train_and_predict(
                stocks=["MOCK"],
                time_step=10,
                future_days=1,
                epochs=1,
                save_model=False,
            )

        mock_download.assert_called_once()
        self.assertIn("MOCK+1", predictions)
        self.assertEqual(len(predictions["MOCK+1"]), 1)

    @patch("yfinance.download")
    def test_skips_ticker_without_data(self, mock_download):
        mock_download.return_value = pd.DataFrame()

        with redirect_stdout(StringIO()):
            predictions = stonky.train_and_predict(stocks=["EMPTY"], time_step=10, epochs=1, save_model=False)

        self.assertEqual(predictions, {})


if __name__ == "__main__":
    unittest.main()
