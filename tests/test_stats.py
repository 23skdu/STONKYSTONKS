import unittest
import numpy as np
from stats import calculate_stats

class TestStats(unittest.TestCase):
    def test_calculate_stats_basic(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        res = calculate_stats(data)
        
        self.assertEqual(res["Min"], 1.0)
        self.assertEqual(res["Max"], 5.0)
        self.assertEqual(res["Median"], 3.0)
        self.assertEqual(res["Mean"], 3.0)
        
        # Standard deviation of [1, 2, 3, 4, 5] is sqrt(2) ~ 1.414
        self.assertAlmostEqual(res["Standard Deviation"], 1.41421356, places=5)
        
        # Test keys presence
        expected_keys = [
            "Min", "23.6% Fibonacci", "1st Quartile", "38.2% Fibonacci",
            "Median", "Mean", "HarmonicMean", "61.8% Fibonacci",
            "3rd Quartile", "78.6% Fibonacci", "Max", "Standard Deviation",
            "Kurtosis", "Skew", "Average Deviation"
        ]
        for key in expected_keys:
            self.assertIn(key, res)

if __name__ == "__main__":
    unittest.main()
