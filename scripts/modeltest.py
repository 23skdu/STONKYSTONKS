#!/usr/bin/env python3
"""Benchmark a few scikit-learn classifiers on a synthetic dataset.

The script generates a binary classification dataset, cross-validates four
classic models and reports accuracy, precision, recall and F1 for each of them.

Example:
    python -m scripts modeltest
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from typing import Any

from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

__all__ = ["DEFAULT_SCORING", "evaluate_models", "main", "run_evaluation"]

#: Metric name -> scikit-learn scoring name, evaluated with the same folds.
DEFAULT_SCORING: dict[str, str] = {
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1",
}

RANDOM_STATE = 42


def evaluate_models(
    models: Mapping[str, Any],
    X: Any,
    y: Any,
    *,
    cv: int = 5,
    scoring: Mapping[str, str] = DEFAULT_SCORING,
    verbose: bool = True,
) -> dict[str, dict[str, float]]:
    """Cross-validate ``models`` and return ``{model: {metric: mean score}}``.

    All metrics share the same cross-validation splits so they are directly
    comparable between models.
    """
    results: dict[str, dict[str, float]] = {}
    metric_names = list(scoring)
    for name, model in models.items():
        scores = cross_validate(model, X, y, cv=cv, scoring=[scoring[m] for m in metric_names])
        metrics = {metric: float(scores[f"test_{scoring[metric]}"].mean()) for metric in metric_names}
        results[name] = metrics
        if verbose:
            formatted = ", ".join(f"{key.capitalize()}: {value:.2f}" for key, value in metrics.items())
            print(f"{name} - {formatted}")
    return results


def run_evaluation(*, verbose: bool = True) -> dict[str, dict[str, float]]:
    """Generate the synthetic dataset, evaluate the default models and report."""
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=2,
        n_redundant=10,
        random_state=RANDOM_STATE,
    )
    models: dict[str, Any] = {
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "DecisionTree": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "RandomForest": RandomForestClassifier(random_state=RANDOM_STATE),
        "SVM": SVC(),
    }
    return evaluate_models(models, X, y, verbose=verbose)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point used by ``python -m scripts modeltest``."""
    argparse.ArgumentParser(
        prog="modeltest",
        description="Cross-validate classic classifiers on a synthetic dataset.",
    ).parse_args(argv)
    run_evaluation()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
