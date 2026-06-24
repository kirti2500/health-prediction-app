"""
train_model.py

Quick script to train a small logistic regression model that predicts
health risk based on glucose, haemoglobin and cholesterol values.

NOTE: I couldn't find a clean public dataset for exactly this combination
of 3 features, so I generated synthetic training data based on common
clinical reference ranges (normal/borderline/high values for each test).
This is obviously not a medical-grade model - it's just enough to
demonstrate a working ML integration for this assignment.

Run this once with: python train_model.py
It will create model.pkl in the project folder.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# seeding so results are repeatable while I was testing this
np.random.seed(42)

NUM_SAMPLES = 600


def generate_training_data(n=NUM_SAMPLES):
    """
    Builds a synthetic dataset.

    Reference ranges I used (rough, just for this assignment):
    - Glucose (fasting):     normal < 100, prediabetic 100-125, high > 125 mg/dL
    - Haemoglobin:           normal ~13-17 (men), ~12-15 (women), low < 12 g/dL
    - Cholesterol (total):   normal < 200, borderline 200-239, high > 240 mg/dL

    Risk label (0 = low risk, 1 = high risk) is decided using a noisy
    combination of these so the model has to actually learn the pattern
    rather than just one cutoff.
    """
    glucose = np.random.normal(110, 35, n).clip(60, 300)
    haemoglobin = np.random.normal(14, 2.5, n).clip(6, 20)
    cholesterol = np.random.normal(210, 50, n).clip(100, 400)

    risk_score = (
        (glucose > 125) * 1.5
        + (glucose > 180) * 1.0
        + (haemoglobin < 12) * 1.2
        + (cholesterol > 240) * 1.3
        + (cholesterol > 280) * 0.8
    )

    # add a bit of randomness so it's not a perfectly clean rule
    noise = np.random.normal(0, 0.6, n)
    risk_score = risk_score + noise

    labels = (risk_score > 1.4).astype(int)

    df = pd.DataFrame({
        "glucose": glucose,
        "haemoglobin": haemoglobin,
        "cholesterol": cholesterol,
        "risk": labels
    })
    return df


def main():
    df = generate_training_data()
    print(f"Generated {len(df)} synthetic rows")
    print(df["risk"].value_counts())

    X = df[["glucose", "haemoglobin", "cholesterol"]]
    y = df["risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test accuracy: {acc:.2f}")

    joblib.dump(model, "model.pkl")
    print("Saved model to model.pkl")


if __name__ == "__main__":
    main()