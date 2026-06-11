import sys
from unittest.mock import MagicMock

# Mock talib module before importing new_volprice_ema
mock_talib = MagicMock()
mock_talib.SMA.side_effect = lambda data, timeperiod: data
sys.modules['talib'] = mock_talib

import unittest
from unittest.mock import patch
import pandas as pd
import numpy as np

# We can import the main functions from the scripts
import ytd_volprice
import new_volprice_ema

class TestVolPrice(unittest.TestCase):
    def setUp(self):
        # Create dummy stock data DataFrame
        dates = pd.date_range(start="2024-01-01", periods=10)
        self.mock_df = pd.DataFrame({
            'Open': np.random.rand(10) * 100 + 50,
            'High': np.random.rand(10) * 100 + 50,
            'Low': np.random.rand(10) * 100 + 50,
            'Close': np.random.rand(10) * 100 + 50,
            'Volume': np.random.randint(1000, 10000, size=10)
        }, index=dates)

    @patch('yfinance.download')
    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.pyplot.show')
    def test_ytd_volprice_main(self, mock_show, mock_subplots, mock_download):
        mock_download.return_value = self.mock_df
        
        # Mock subplots fig and axes
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_ax1.twinx.return_value = mock_ax2
        mock_subplots.return_value = (mock_fig, mock_ax1)
        
        # Run the main function
        data = ytd_volprice.main('AAPL', show_plot=False)
        
        mock_download.assert_called_once()
        self.assertFalse(data.empty)

    @patch('yfinance.download')
    @patch('matplotlib.pyplot.figure')
    @patch('matplotlib.pyplot.plot')
    @patch('matplotlib.pyplot.show')
    def test_new_volprice_ema_main(self, mock_show, mock_plot, mock_figure, mock_download):
        mock_download.return_value = self.mock_df
        
        # Run the main function
        data = new_volprice_ema.main('AAPL', show_plot=False)
        
        mock_download.assert_called_once()
        self.assertFalse(data.empty)
        self.assertIn('Price/Volume', data.columns)

if __name__ == "__main__":
    unittest.main()
