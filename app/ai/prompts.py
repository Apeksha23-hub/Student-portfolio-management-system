"""
Prompt builders and validators for the two AI actions.

Only the minimum data is sent: titles, technologies, descriptions, skill
names and education levels. Never the name, email, phone or address.
"""
import re

RULES = """Rules:
- Use ONLY the facts given below. Do NOT invent facts, numbers, percentages, tools, technologies, companies or results.
- If some information is missing, write less instead of guessing.
- Return JSON only. No markdown, no explanations."""


def _detail_lines(details):
    return "\n".join(f"{label}: {value}" for label, value in details.items() if value)


def bullets_prompt(kind, details):
    """kind is 'project' or 'internship'; details is a {label: value} dict."""
    return f"""You help a college student write resume bullet points for a {kind}.
Write 2 to 3 concise resume bullet points. Each bullet must start with a strong past-tense action verb
(for example Built, Developed, Designed, Implemented), be a single sentence, and have at most 25 words.
{RULES}
Return exactly this JSON shape: {{"bullets": ["first bullet", "second bullet"]}}

{kind.capitalize()} details:
{_detail_lines(details)}"""


def summary_prompt(details):
    return f"""You help a college student write the professional summary at the top of their resume.
Write a 2 to 3 line professional summary (40 to 60 words) in a confident, simple tone.
Do not use "I" or the student's name. Mention only skills, projects and education listed below.
{RULES}
Return exactly this JSON shape: {{"summary": "the summary text"}}

Student details:
{_detail_lines(details)}"""


def clean_bullets(data):
    """Validate {"bullets": [...]} and return 1 to 3 tidy strings, or None."""
    if not data or not isinstance(data.get("bullets"), list):
        return None
    bullets = []
    for item in data["bullets"]:
        if isinstance(item, str):
            text = re.sub(r"^[\s\-\u2022*]+", "", item).strip()  # drop "- " or "• " prefixes
            if text:
                bullets.append(text[:220])
    return bullets[:3] or None


def clean_summary(data, max_length=600):
    """Validate {"summary": "..."} and return the text, or None."""
    if not data or not isinstance(data.get("summary"), str):
        return None
    text = " ".join(data["summary"].split())
    return text[:max_length] or None
