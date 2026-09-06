"""
symptom_engine.py
Core AI logic: sends symptom data to Gemini 3.6 Flash and returns a
structured triage result using the google-genai SDK (v1+).
"""

import json
import re
from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """
You are a highly experienced medical triage assistant AI. Your role is to
analyse the symptoms provided by a user and return a structured clinical
assessment. You are NOT replacing a doctor — you provide guidance only.

RULES:
1. Always respond with a single valid JSON object and NOTHING else.
2. Never add markdown fences, commentary, or prose outside the JSON.
3. Be thorough but concise in every text field.
4. Triage level must be exactly one of: "Self-Care", "See a Doctor", "Emergency".
5. Urgency score must be an integer from 1 (minimal) to 10 (life-threatening).

JSON schema you MUST follow exactly:
{
  "triage_level": "<Self-Care | See a Doctor | Emergency>",
  "urgency_score": <1-10>,
  "summary": "<2-3 sentence plain-English summary of the assessment>",
  "possible_conditions": [
    {
      "name": "<condition name>",
      "likelihood": "<Low | Moderate | High>",
      "description": "<one sentence about this condition>"
    }
  ],
  "red_flags": ["<symptom or sign that needs immediate attention>"],
  "self_care_tips": ["<actionable home-care advice>"],
  "when_to_escalate": "<clear instruction on when the user must seek higher care>",
  "disclaimer": "This assessment is AI-generated and does not constitute medical advice. Always consult a qualified healthcare professional."
}

If any symptom strongly suggests a life-threatening emergency (e.g., chest
pain, difficulty breathing, stroke signs, severe bleeding), set triage_level
to "Emergency" and urgency_score to 9 or 10 regardless of other factors.
""".strip()

USER_PROMPT_TEMPLATE = """
Patient profile:
- Age: {age}
- Biological sex: {sex}
- Current symptoms: {symptoms}
- Symptom duration: {duration}
- Severity (self-reported 1-10): {severity}
- Relevant medical history / chronic conditions: {history}
- Current medications: {medications}
- Additional notes: {notes}

Analyse the above and return the JSON assessment.
""".strip()


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

def analyse_symptoms(
    api_key: str,
    symptoms: str,
    age: str = "Not specified",
    sex: str = "Not specified",
    duration: str = "Not specified",
    severity: int = 5,
    history: str = "None",
    medications: str = "None",
    notes: str = "None",
) -> dict:
    """
    Send symptom data to Gemini 2.5 Flash and return a parsed result dict.

    Returns a dict with keys matching the JSON schema above, plus an optional
    'error' key if something went wrong.
    """
    client = genai.Client(api_key=api_key)

    user_message = USER_PROMPT_TEMPLATE.format(
        age=age,
        sex=sex,
        symptoms=symptoms,
        duration=duration,
        severity=severity,
        history=history,
        medications=medications,
        notes=notes,
    )

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,
        top_p=0.95,
        max_output_tokens=2048,
        response_mime_type="application/json",
    )

    # Model IDs to try in order — the API accepts whichever is live for your key tier
    MODEL_CANDIDATES = [
        "gemini-3.6-flash",
        "gemini-2.5-flash",
        "gemini-2.5-flash-preview-05-20",
    ]

    raw_text = ""
    last_error = ""

    for model_id in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_id,
                contents=user_message,
                config=config,
            )
            raw_text = response.text.strip()

            # Strip any accidental markdown fences
            raw_text = re.sub(r"^```[a-zA-Z]*\n?", "", raw_text)
            raw_text = re.sub(r"\n?```$", "", raw_text)

            result = json.loads(raw_text)
            result["_model_used"] = model_id   # track which model succeeded
            return result

        except json.JSONDecodeError as exc:
            return {
                "error": f"Failed to parse AI response as JSON: {exc}",
                "raw_response": raw_text or "No response",
            }
        except Exception as exc:
            err_str = str(exc)
            # Only retry on 404 / not-found errors
            if "404" in err_str or "not found" in err_str.lower():
                last_error = err_str
                continue
            # Any other error (bad key, quota, network) — fail immediately
            return {"error": err_str}

    return {"error": f"No available Gemini model found. Last error: {last_error}"}


# ---------------------------------------------------------------------------
# Triage level helpers
# ---------------------------------------------------------------------------

TRIAGE_COLOURS = {
    "Self-Care": "#2e7d32",
    "See a Doctor": "#e65100",
    "Emergency": "#b71c1c",
}

TRIAGE_ICONS = {
    "Self-Care": "🟢",
    "See a Doctor": "🟠",
    "Emergency": "🔴",
}

_URGENCY_BANDS = [
    (range(1, 4), "green"),
    (range(4, 7), "orange"),
    (range(7, 11), "red"),
]


def urgency_colour(score: int) -> str:
    for band, colour in _URGENCY_BANDS:
        if score in band:
            return colour
    return "grey"
