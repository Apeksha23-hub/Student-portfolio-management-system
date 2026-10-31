"""
AI endpoints, called by the "Improve with AI" and "Generate summary" buttons.

They only return a SUGGESTION as JSON. Nothing is saved here: the student
copies the suggestion into the form, edits it if needed, and clicks Save.
Saved text is reused by the resume and portfolio, so it is never regenerated.
"""
from datetime import date

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app import db
from app.ai.llm import BUSY_MESSAGE, call_llm, parse_json
from app.ai.prompts import bullets_prompt, clean_bullets, clean_summary, summary_prompt
from app.models import AIUsage
from app.utils import newest_first

bp = Blueprint("ai", __name__)


# ---------------------------------------------------------------------------
# Daily limit (ai_usage table: one row per user per day)
# ---------------------------------------------------------------------------

def _today_row(user_id):
    return AIUsage.query.filter_by(user_id=user_id, date=date.today()).first()


def remaining_actions(user_id):
    row = _today_row(user_id)
    used = row.count if row else 0
    return max(current_app.config["AI_DAILY_LIMIT"] - used, 0)


def record_action(user_id):
    """Count one successful AI action for today."""
    row = _today_row(user_id)
    if row is None:
        row = AIUsage(user_id=user_id, date=date.today(), count=0)
        db.session.add(row)
    row.count += 1
    db.session.commit()


def _limit_reached_response():
    limit = current_app.config["AI_DAILY_LIMIT"]
    return jsonify(ok=False, remaining=0,
                   message=f"You have used all {limit} AI actions for today. Please try again tomorrow."), 429


def _clip(value, length=300):
    return (value or "").strip()[:length]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route("/improve", methods=["POST"])
@login_required
def improve():
    """Turn a project/internship description into 2-3 resume bullets."""
    payload = request.get_json(silent=True) or {}
    kind = payload.get("kind")
    if kind not in ("project", "internship"):
        return jsonify(ok=False, message="Unknown item type."), 400

    description = _clip(payload.get("description"), 2000)
    if len(description) < 15:
        return jsonify(ok=False, message="Write a short description first (at least one sentence)."), 400

    left = remaining_actions(current_user.id)
    if left <= 0:
        return _limit_reached_response()

    if kind == "project":
        details = {"Project title": _clip(payload.get("title")),
                   "Technologies used": _clip(payload.get("tech_stack")),
                   "Description": description}
    else:
        details = {"Role": _clip(payload.get("role")),
                   "Company": _clip(payload.get("company")),
                   "Description": description}

    result = call_llm(bullets_prompt(kind, details), fallback=description)
    bullets = clean_bullets(parse_json(result.text)) if result.ok else None
    if not bullets:
        # Failure does not use up an AI action; the original text is returned unchanged.
        return jsonify(ok=False, original=description, remaining=left,
                       message=result.message or BUSY_MESSAGE)

    record_action(current_user.id)
    return jsonify(ok=True, suggestion="\n".join(bullets), remaining=left - 1)


@bp.route("/summary", methods=["POST"])
@login_required
def summary():
    """Suggest a professional summary from saved skills, projects and education."""
    user = current_user
    skills = [s.name for s in user.skills.all()][:20]
    projects = newest_first(user.projects.all(), "end_date", "start_date")[:4]
    education = newest_first(user.education.all(), "end_year", "start_year")[:2]
    original = user.profile.summary or ""

    if not (skills or projects or education):
        return jsonify(ok=False, message="Add some skills, projects or education first."), 400

    left = remaining_actions(user.id)
    if left <= 0:
        return _limit_reached_response()

    details = {
        "Headline": _clip(user.profile.headline, 150),
        "Skills": ", ".join(skills),
        "Projects": "; ".join(f"{p.title} ({p.tech_stack})" if p.tech_stack else p.title for p in projects),
        "Education": "; ".join(" ".join(x for x in [e.level, e.score] if x) for e in education),
    }
    result = call_llm(summary_prompt(details), fallback=original)
    text = clean_summary(parse_json(result.text)) if result.ok else None
    if not text:
        return jsonify(ok=False, original=original, remaining=left, message=result.message or BUSY_MESSAGE)

    record_action(user.id)
    return jsonify(ok=True, suggestion=text, remaining=left - 1)
