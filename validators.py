"""
validators.py

Small helper functions to check the form data before we save anything
to the database. Kept separate from app.py so the routes don't get
cluttered with if/else checks.
"""

import re
from datetime import datetime, date

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Clinically plausible ranges for a living adult patient.
# These are wider than the "normal" reference ranges (which the model
# itself uses to flag risk) - the point here is just to reject values
# that are physiologically impossible or almost certainly typos,
# before they ever reach the prediction model.
#
#   Glucose (fasting):  normal ~70-100, prediabetic ~100-125, diabetic >125
#                        below ~40 is severe hypoglycemia (medical emergency)
#                        above ~600 is an extreme hyperglycemic crisis
#   Haemoglobin:         normal ~12-17 g/dL for adults
#                        below ~3 or above ~20 is not physiologically plausible
#   Cholesterol (total): normal <200, borderline 200-239, high >240
#                        below ~50 or above ~500 is implausible/likely a typo
GLUCOSE_RANGE = (40, 600)
HAEMOGLOBIN_RANGE = (3, 20)
CHOLESTEROL_RANGE = (50, 500)


def is_valid_email(email):
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email.strip()))


def is_valid_dob(dob_string):
    """
    dob_string comes from an HTML date input, format YYYY-MM-DD.
    Returns (True, date_object) if valid, (False, None) if not.
    """
    try:
        dob = datetime.strptime(dob_string, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return False, None

    if dob > date.today():
        return False, None

    return True, dob


def is_valid_number(value, min_val=0, max_val=1000):
    """
    Checks the blood test values are numeric and within a clinically
    plausible range for a living adult patient. This catches both
    obvious junk (letters, negative numbers) and values that are
    technically numeric but medically impossible (e.g. glucose of 5,
    which would mean the patient is not alive to have it measured).

    Rejecting these here means they never reach the prediction model,
    which was trained on realistic clinical ranges and gives
    unreliable output for extreme out-of-range inputs.
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return False, None

    if num < min_val or num > max_val:
        return False, None

    return True, num


def validate_patient_form(form):
    """
    Runs all checks on a submitted form and returns a dict of errors.
    Empty dict means everything passed.
    """
    errors = {}

    full_name = form.get("full_name", "").strip()
    if not full_name:
        errors["full_name"] = "Full name is required."

    email = form.get("email", "").strip()
    if not is_valid_email(email):
        errors["email"] = "Please enter a valid email address."

    dob_ok, dob_value = is_valid_dob(form.get("date_of_birth", ""))
    if not dob_ok:
        errors["date_of_birth"] = "Enter a valid date of birth (cannot be in the future)."

    glucose_ok, glucose_value = is_valid_number(form.get("glucose", ""), *GLUCOSE_RANGE)
    if not glucose_ok:
        errors["glucose"] = f"Glucose must be a realistic value between {GLUCOSE_RANGE[0]} and {GLUCOSE_RANGE[1]} mg/dL."

    hb_ok, hb_value = is_valid_number(form.get("haemoglobin", ""), *HAEMOGLOBIN_RANGE)
    if not hb_ok:
        errors["haemoglobin"] = f"Haemoglobin must be a realistic value between {HAEMOGLOBIN_RANGE[0]} and {HAEMOGLOBIN_RANGE[1]} g/dL."

    chol_ok, chol_value = is_valid_number(form.get("cholesterol", ""), *CHOLESTEROL_RANGE)
    if not chol_ok:
        errors["cholesterol"] = f"Cholesterol must be a realistic value between {CHOLESTEROL_RANGE[0]} and {CHOLESTEROL_RANGE[1]} mg/dL."

    cleaned = {
        "full_name": full_name,
        "email": email,
        "date_of_birth": dob_value,
        "glucose": glucose_value,
        "haemoglobin": hb_value,
        "cholesterol": chol_value,
    }

    return errors, cleaned