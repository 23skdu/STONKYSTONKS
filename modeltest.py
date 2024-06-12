#!/usr/bin/env python3
from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Generate a synthetic binary classification dataset
X, y = make_classification(n_samples=1000, n_features=20, n_informative=2, n_redundant=10, random_state=42)

# Create model instances
models = {
    'LogisticRegression': LogisticRegression(),
    'DecisionTree': DecisionTreeClassifier(),
    'RandomForest': RandomForestClassifier(),
    'SVM': SVC()
}

# Function to evaluate models
def evaluate_models(models, X, y):
    for name, model in models.items():
        # Perform cross-validation
        cv_accuracy = cross_val_score(model, X, y, cv=5, scoring='accuracy')
        cv_precision = cross_val_score(model, X, y, cv=5, scoring='precision')
        cv_recall = cross_val_score(model, X, y, cv=5, scoring='recall')
        cv_f1 = cross_val_score(model, X, y, cv=5, scoring='f1')
        
        # Output the performance
        print(f"{name} - Accuracy: {cv_accuracy.mean():.2f}, Precision: {cv_precision.mean():.2f}, Recall: {cv_recall.mean():.2f}, F1: {cv_f1.mean():.2f}")

# Evaluate all models
evaluate_models(models, X, y)

