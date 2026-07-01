"""
predictor.py

Calls the Groq API (external AI/ML service) to generate a health risk
assessment based on the patient's blood test values. The prediction
comes back from Groq's hosted LLM (Llama 3), not a local model.

Groq was chosen because it's free, fast, and provides access to
production-grade AI models via a simple REST API - which is exactly
what this application needs for the Remarks generation.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Make sure you have a .env file "
                "in the project root with your Groq API key."
            )
        _client = Groq(api_key=api_key)
    return _client


def generate_remarks(glucose, haemoglobin, cholesterol):
    client = get_client()

    prompt = f"""You are a clinical decision support assistant. Based on the following blood test results for an adult patient, provide a brief health risk assessment in 2-3 sentences. Be specific about which values are concerning and what condition they may indicate. Do not recommend specific medications. Keep the tone professional and informative.

Blood test results:
- Fasting Glucose: {glucose} mg/dL (normal range: 70-100 mg/dL)
- Haemoglobin: {haemoglobin} g/dL (normal range: 12-17 g/dL)
- Total Cholesterol: {cholesterol} mg/dL (normal range: below 200 mg/dL)

Provide the assessment as a single paragraph with no headers or bullet points."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a clinical decision support assistant that provides brief, accurate health risk assessments based on blood test values."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=150,
            temperature=0.3,
        )
        remarks = response.choices[0].message.content.strip()
        return remarks

    except Exception as e:
        return f"Unable to generate AI assessment at this time. Error: {str(e)}"