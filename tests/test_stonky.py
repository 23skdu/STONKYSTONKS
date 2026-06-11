import sys
import os
import numpy as np
from unittest.mock import MagicMock

# Mock tensorflow modules
mock_tf = MagicMock()
mock_tf.saved_model.save = MagicMock()

# Mock Keras classes
class MockSequential:
    def __init__(self, *args, **kwargs):
        pass
    def add(self, layer):
        pass
    def compile(self, *args, **kwargs):
        pass
    def fit(self, *args, **kwargs):
        pass
    def predict(self, x_input, *args, **kwargs):
        return np.array([[0.5]])

mock_tf.keras.models.Sequential = MockSequential
mock_tf.keras.layers.LSTM = MagicMock()
mock_tf.keras.layers.Dense = MagicMock()

sys.modules['tensorflow'] = mock_tf
sys.modules['tensorflow.keras'] = mock_tf.keras
sys.modules['tensorflow.keras.models'] = mock_tf.keras.models
sys.modules['tensorflow.keras.layers'] = mock_tf.keras.layers

import unittest
from unittest.mock import patch
import pandas as pd
import importlib.util
from importlib.machinery import SourceFileLoader

# Dynamically import extension-less 'stonky' script using SourceFileLoader
stonky_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "stonky"))
loader = SourceFileLoader("stonky", stonky_path)
spec = importlib.util.spec_from_loader("stonky", loader)
stonky = importlib.util.module_from_spec(spec)
loader.exec_module(stonky)

class TestStonky(unittest.TestCase):
    def test_create_dataset(self):
        # Create dummy scaled data
        data = np.arange(10, dtype=float).reshape(-1, 1)
        time_step = 3
        X, Y = stonky.create_dataset(data, time_step)
        
        # Expected outputs
        self.assertEqual(len(X), 6)
        self.assertEqual(len(Y), 6)
        np.testing.assert_array_equal(X[0], [0.0, 1.0, 2.0])
        self.assertEqual(Y[0], 3.0)

    @patch('yfinance.download')
    def test_train_and_predict_integration(self, mock_download):
        # Mock yfinance data
        dates = pd.date_range(start="2024-01-01", periods=120)
        mock_df = pd.DataFrame({
            'Close': np.random.rand(120) * 100 + 50,
            'Volume': np.random.randint(1000, 10000, size=120)
        }, index=dates)
        mock_download.return_value = mock_df
        
        # Run train_and_predict
        stonky.train_and_predict(
            stocks=['MOCK'],
            time_step=10,
            future_days=1,
            epochs=1,
            save_model=False
        )
        
        mock_download.assert_called_once()

if __name__ == "__main__":
    unittest.main()
