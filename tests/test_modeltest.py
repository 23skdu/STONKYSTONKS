import unittest
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from modeltest import evaluate_models

class TestModelTest(unittest.TestCase):
    def test_evaluate_models(self):
        # Create a simple dataset
        X, y = make_classification(n_samples=100, n_features=5, n_informative=3, n_redundant=2, random_state=42)
        
        # Test evaluation with a simple Logistic Regression model
        models = {'LogisticRegression': LogisticRegression()}
        
        results = evaluate_models(models, X, y)
        
        self.assertIn('LogisticRegression', results)
        metrics = results['LogisticRegression']
        self.assertIn('accuracy', metrics)
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1', metrics)
        
        self.assertTrue(0.0 <= metrics['accuracy'] <= 1.0)
        self.assertTrue(0.0 <= metrics['precision'] <= 1.0)
        self.assertTrue(0.0 <= metrics['recall'] <= 1.0)
        self.assertTrue(0.0 <= metrics['f1'] <= 1.0)

if __name__ == "__main__":
    unittest.main()
