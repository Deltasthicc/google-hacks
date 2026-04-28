"""
Model training module for FairLens AI / NyayaLens.

Trains a Logistic Regression classifier and provides evaluation utilities.
"""

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def train_model(features_train, income_labels_train):
    """
    Train a Logistic Regression classifier on the provided training data.

    Args:
        features_train:       pandas DataFrame of training features (scaled).
        income_labels_train:  pandas Series of binary labels (0 or 1).

    Returns:
        trained_model: Fitted LogisticRegression model object.
    """
    trained_model = LogisticRegression(max_iter=5000, random_state=42)
    trained_model.fit(features_train, income_labels_train)
    return trained_model


def evaluate_model(predictions, income_labels_test):
    """
    Compute standard classification metrics for a set of predictions.

    Args:
        predictions:         numpy array or list of predicted labels (0 or 1).
        income_labels_test:  pandas Series of true labels (0 or 1).

    Returns:
        metrics_dict: Dict with keys 'accuracy', 'precision', 'recall', 'f1'.
                      All values are plain Python floats (JSON-safe).
    """
    metrics_dict = {
        "accuracy":  float(accuracy_score(income_labels_test, predictions)),
        "precision": float(precision_score(income_labels_test, predictions)),
        "recall":    float(recall_score(income_labels_test, predictions)),
        "f1":        float(f1_score(income_labels_test, predictions)),
    }
    return metrics_dict
