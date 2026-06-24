"""
predictor.py

Loads the trained model (model.pkl) and uses it to generate the
"Remarks" text for a patient based on their blood test values.

The model only outputs 0/1 + a probability - turning that into a
readable sentence for the Remarks field is just regular Python logic,
not the model's job.
"""

import joblib
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

_model = None


def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "model.pkl not found. Run 'python train_model.py' first to "
                "generate the trained model before starting the app."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def generate_remarks(glucose, haemoglobin, cholesterol):
    model = get_model()

    # model expects a 2D array - one row, three columns
    features = [[glucose, haemoglobin, cholesterol]]
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]  # probability of "high risk" class

    flags = []
    if glucose > 125:
        flags.append("elevated glucose")
    if haemoglobin < 12:
        flags.append("low haemoglobin")
    if cholesterol > 240:
        flags.append("high cholesterol")

    if prediction == 1:
        risk_text = f"high risk ({probability * 100:.0f}% confidence)"
    else:
        risk_text = f"low risk ({(1 - probability) * 100:.0f}% confidence)"

    if flags:
        flag_text = ", ".join(flags)
        remarks = (
            f"Model prediction: {risk_text}. "
            f"Notable values - {flag_text}. "
            f"Recommend consulting a physician for further evaluation."
        )
    else:
        remarks = (
            f"Model prediction: {risk_text}. "
            f"All three values are within normal reference ranges."
        )

    return remarks