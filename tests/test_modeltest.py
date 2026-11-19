import unittest

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression

from scripts.modeltest import evaluate_models


class TestModelTest(unittest.TestCase):
    def test_evaluate_models(self):
        X, y = make_classification(
            n_samples=100,
            n_features=5,
            n_informative=3,
            n_redundant=2,
            random_state=42,
        )
        models = {"LogisticRegression": LogisticRegression(max_iter=1000)}

        results = evaluate_models(models, X, y, verbose=False)

        self.assertIn("LogisticRegression", results)
        metrics = results["LogisticRegression"]
        for name in ("accuracy", "precision", "recall", "f1"):
            self.assertIn(name, metrics)
            self.assertTrue(0.0 <= metrics[name] <= 1.0)

    def test_scoring_is_configurable(self):
        X, y = make_classification(n_samples=100, n_features=5, random_state=42)
        models = {"LogisticRegression": LogisticRegression(max_iter=1000)}

        results = evaluate_models(models, X, y, cv=3, scoring={"accuracy": "accuracy"}, verbose=False)

        self.assertEqual(set(results["LogisticRegression"]), {"accuracy"})


if __name__ == "__main__":
    unittest.main()
