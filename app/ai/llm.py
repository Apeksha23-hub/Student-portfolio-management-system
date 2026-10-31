"""
The ONLY file that talks to the LLM provider (Google Gemini free tier, REST API).

To swap providers, rewrite _send_to_provider(); the rest of the app only
uses call_llm() and parse_json(). The LLM is used only to improve text;
resumes and portfolios are always built from saved database data.
"""
import json
import re
from dataclasses import dataclass

import requests
from flask import current_app

BUSY_MESSAGE = "AI is busy, please try again later."
NOT_CONFIGURED_MESSAGE = ("AI is not set up on this computer (no GEMINI_API_KEY in .env). "
                          "You can still type the text yourself.")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


@dataclass
class LLMResult:
    ok: bool           # True only when the provider returned text
    text: str          # the model's reply, or the fallback (original) text
    message: str = ""  # message to show the student when ok is False


def _send_to_provider(prompt):
    """Send one prompt to Gemini and return the reply text. Raises on any problem."""
    config = current_app.config
    response = requests.post(
        GEMINI_URL.format(model=config["GEMINI_MODEL"]),
        headers={"x-goog-api-key": config["GEMINI_API_KEY"], "Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            # Low temperature = fewer creative additions; ask for JSON output.
            "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"},
        },
        timeout=config["LLM_TIMEOUT"],  # never let a slow API freeze the page
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def call_llm(prompt, fallback=""):
    """
    Ask the LLM. Never raises: on any failure (no internet, timeout, quota,
    unexpected reply) it returns the fallback text and a friendly message.
    """
    if not current_app.config.get("GEMINI_API_KEY"):
        return LLMResult(False, fallback, NOT_CONFIGURED_MESSAGE)
    try:
        return LLMResult(True, _send_to_provider(prompt))
    except Exception as exc:  # noqa: BLE001 - any failure must fall back gracefully
        # Log only the error type so no prompt text or key ends up in the logs.
        current_app.logger.warning("LLM call failed: %s", type(exc).__name__)
        return LLMResult(False, fallback, BUSY_MESSAGE)


def parse_json(text):
    """Safely turn the model's reply into a dict. Returns None if it is not valid JSON."""
    if not text:
        return None
    # Models sometimes wrap JSON in ```json fences; remove them.
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE)
    try:
        data = json.loads(cleaned)
    except ValueError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)  # JSON object inside extra text
        if not match:
            return None
        try:
            data = json.loads(match.group(0))
        except ValueError:
            return None
    return data if isinstance(data, dict) else None
