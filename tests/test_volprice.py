import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from scripts import new_volprice_ema, ytd_volprice


class TestVolPrice(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range(start="2024-01-01", periods=250)
        self.mock_df = pd.DataFrame(
            {
                "Open": np.random.rand(250) * 100 + 50,
                "High": np.random.rand(250) * 100 + 50,
                "Low": np.random.rand(250) * 100 + 50,
                "Close": np.random.rand(250) * 100 + 50,
                "Volume": np.random.randint(1000, 10000, size=250),
            },
            index=dates,
        )

    @patch("yfinance.download")
    @patch("matplotlib.pyplot.subplots")
    @patch("matplotlib.pyplot.show")
    def test_ytd_volprice_main(self, mock_show, mock_subplots, mock_download):
        mock_download.return_value = self.mock_df

        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax2 = MagicMock()
        mock_ax1.twinx.return_value = mock_ax2
        mock_subplots.return_value = (mock_fig, mock_ax1)

        data = ytd_volprice.analyze("AAPL", show_plot=False, start="2024-01-01")

        mock_download.assert_called_once()
        self.assertFalse(data.empty)
        mock_show.assert_not_called()

    @patch("yfinance.download")
    @patch("matplotlib.pyplot.figure")
    @patch("matplotlib.pyplot.plot")
    @patch("matplotlib.pyplot.show")
    def test_new_volprice_ema_main(self, mock_show, mock_plot, mock_figure, mock_download):
        mock_download.return_value = self.mock_df

        data = new_volprice_ema.analyze("AAPL", show_plot=False)

        mock_download.assert_called_once()
        self.assertFalse(data.empty)
        self.assertIn("Price/Volume", data.columns)
        for window in new_volprice_ema.MOVING_AVERAGES:
            self.assertIn(f"MA{window}", data.columns)
        mock_show.assert_not_called()

    @patch("yfinance.download")
    @patch("matplotlib.pyplot.figure")
    @patch("matplotlib.pyplot.plot")
    @patch("matplotlib.pyplot.show")
    def test_moving_averages_ignore_insufficient_history(
        self, mock_show, mock_plot, mock_figure, mock_download
    ):
        mock_download.return_value = self.mock_df.iloc[:10]

        data = new_volprice_ema.analyze("AAPL", show_plot=False)

        # Not enough rows for a 25-day average -> NaN, matching talib.SMA behaviour.
        self.assertTrue(data["MA25"].isna().all())

    @patch("yfinance.download")
    @patch("matplotlib.pyplot.show")
    def test_show_plot_requests_a_window(self, mock_show, mock_download):
        mock_download.return_value = self.mock_df
        mock_fig = MagicMock()
        mock_ax1 = MagicMock()
        mock_ax1.twinx.return_value = MagicMock()
        with patch("matplotlib.pyplot.subplots", return_value=(mock_fig, mock_ax1)):
            ytd_volprice.analyze("AAPL", show_plot=True, start="2024-01-01")

        mock_show.assert_called_once()


if __name__ == "__main__":
    unittest.main()
