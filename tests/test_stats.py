import unittest

import numpy as np

from scripts.stats import calculate_stats


class TestStats(unittest.TestCase):
    def test_calculate_stats_basic(self):
        res = calculate_stats([1.0, 2.0, 3.0, 4.0, 5.0])

        self.assertEqual(res["Min"], 1.0)
        self.assertEqual(res["Max"], 5.0)
        self.assertEqual(res["Median"], 3.0)
        self.assertEqual(res["Mean"], 3.0)

        # Standard deviation of [1, 2, 3, 4, 5] is sqrt(2) ~ 1.414
        self.assertAlmostEqual(res["Standard Deviation"], 1.41421356, places=5)

        expected_keys = [
            "Min",
            "23.6% Fibonacci",
            "1st Quartile",
            "38.2% Fibonacci",
            "Median",
            "Mean",
            "HarmonicMean",
            "61.8% Fibonacci",
            "3rd Quartile",
            "78.6% Fibonacci",
            "Max",
            "Standard Deviation",
            "Kurtosis",
            "Skew",
            "Average Deviation",
        ]
        for key in expected_keys:
            self.assertIn(key, res)

    def test_harmonic_mean_is_a_scalar(self):
        # n / sum(1/x) == 5 / (1 + 1/2 + 1/3 + 1/4 + 1/5) == 300/137
        res = calculate_stats([1.0, 2.0, 3.0, 4.0, 5.0])

        self.assertIsInstance(res["HarmonicMean"], float)
        self.assertAlmostEqual(res["HarmonicMean"], 300 / 137, places=10)

    def test_accepts_numpy_input(self):
        res = calculate_stats(np.arange(1, 6, dtype=float))

        self.assertEqual(res["Mean"], 3.0)

    def test_rejects_empty_input(self):
        with self.assertRaises(ValueError):
            calculate_stats([])


if __name__ == "__main__":
    unittest.main()
