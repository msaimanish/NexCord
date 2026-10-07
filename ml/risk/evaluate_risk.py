from sklearn.metrics import (
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from collections import Counter
from risk.test_risk import generate_dataset
from risk.model import IncidentRiskPredictor


def main() -> None:
    samples, labels = generate_dataset()
    print(
        "Class distribution:",
        Counter(labels),
    )

    train_samples, test_samples, train_labels, test_labels = (
        train_test_split(
            samples,
            labels,
            test_size=0.2,
            random_state=42,
            stratify=labels,
        )
    )

    predictor = IncidentRiskPredictor()

    predictor.fit(
        train_samples,
        train_labels,
    )

    test_vectors = [
        sample.to_vector()
        for sample in test_samples
    ]

    predictions = predictor.model.predict(
        test_vectors
    )

    probabilities = predictor.model.predict_proba(
        test_vectors
    )[:, 1]

    print("Classification report:")
    print(
        classification_report(
            test_labels,
            predictions,
        )
    )

    print(
        "ROC-AUC:",
        roc_auc_score(
            test_labels,
            probabilities,
        ),
    )


if __name__ == "__main__":
    main()