import unittest
from unittest.mock import patch

import pandas as pd

from scripts import marketdata


class TestMarketData(unittest.TestCase):
    @patch("yfinance.download")
    def test_flattens_multiindex_columns(self, mock_download):
        columns = pd.MultiIndex.from_product([["Close", "Volume"], ["AAPL"]])
        mock_download.return_value = pd.DataFrame([[100.0, 1000.0]], columns=columns)

        data = marketdata.download("AAPL", period="max")

        self.assertEqual(list(data.columns), ["Close", "Volume"])
        mock_download.assert_called_once_with("AAPL", period="max", progress=False)

    @patch("yfinance.download")
    def test_keeps_plain_columns(self, mock_download):
        mock_download.return_value = pd.DataFrame({"Close": [1.0], "Volume": [2]})

        data = marketdata.download("AAPL", start="2024-01-01", progress=True)

        self.assertEqual(list(data.columns), ["Close", "Volume"])
        mock_download.assert_called_once_with("AAPL", start="2024-01-01", progress=True)


if __name__ == "__main__":
    unittest.main()
