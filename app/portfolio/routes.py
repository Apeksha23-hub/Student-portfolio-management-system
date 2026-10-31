"""
Public portfolio page (no login needed) and the owner's share settings.

The URL uses the random public_slug (e.g. asha-rao-3f9c2a), never the user
ID, so portfolios cannot be guessed by counting. Private ones return 404.
"""
from datetime import date

import segno
from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import SKILL_CATEGORIES, ShareForm
from app.models import Profile
from app.utils import date_range, month_year, newest_first

bp = Blueprint("portfolio", __name__)

# Width of the skill bar for each proficiency level.
PROFICIENCY_PERCENT = {"Beginner": 30, "Intermediate": 55, "Advanced": 80, "Expert": 100}


def _timeline(user):
    """Education and internships merged into one list, newest first."""
    items = []
    for e in user.education.all():
        year = e.end_year or e.start_year or 0
        items.append({
            "kind": "Education", "sort": (year, 6),
            "title": e.level, "org": e.institution, "dates": date_range(e.start_year, e.end_year),
            "details": [x for x in [e.board_university, e.score and f"Score: {e.score}"] if x],
        })
    for i in user.internships.all():
        when = i.end_date or (date.today() if i.start_date else None)
        items.append({
            "kind": "Internship", "sort": (when.year, when.month) if when else (0, 0),
            "title": i.role, "org": i.company, "dates": date_range(i.start_date, i.end_date),
            "details": i.get_bullets() or ([i.description] if i.description else []),
        })
    return sorted(items, key=lambda x: x["sort"], reverse=True)


def build_portfolio(user):
    groups = {}
    for s in user.skills.all():
        groups.setdefault(s.category or "Other", []).append(
            {"name": s.name, "level": s.proficiency, "percent": PROFICIENCY_PERCENT.get(s.proficiency, 50)})
    order = {name: i for i, name in enumerate(SKILL_CATEGORIES)}

    projects = [{
        "title": p.title, "tech": p.tech_list(), "dates": date_range(p.start_date, p.end_date),
        "bullets": p.get_bullets(), "description": p.description,
        "github": p.github_link, "demo": p.demo_link,
    } for p in newest_first(user.projects.all(), "end_date", "start_date")]

    certifications = [{
        "title": c.title, "issuer": c.issuer, "date": month_year(c.date),
        "url": c.credential_url, "file": c.file_path,
    } for c in newest_first(user.certifications.all(), "date")]

    achievements = [{"title": a.title, "description": a.description, "date": month_year(a.date)}
                    for a in newest_first(user.achievements.all(), "date")]

    return {
        "skill_groups": [(cat, groups[cat]) for cat in sorted(groups, key=lambda c: order.get(c, 99))],
        "projects": projects,
        "timeline": _timeline(user),
        "certifications": certifications,
        "achievements": achievements,
        "stats": [("Projects", len(projects)), ("Skills", user.skills.count()),
                  ("Internships", user.internships.count()), ("Certifications", len(certifications))],
    }


@bp.route("/portfolio/<slug>")
def public(slug):
    profile = Profile.query.filter_by(public_slug=slug).first()
    if profile is None or not profile.is_public:
        abort(404)  # private and missing look the same to visitors
    return render_template("portfolio/public.html", user=profile.user, profile=profile,
                           **build_portfolio(profile.user))


@bp.route("/share", methods=["GET", "POST"])
@login_required
def share():
    profile = current_user.profile
    form = ShareForm(obj=profile)
    if form.validate_on_submit():
        profile.is_public = form.is_public.data
        db.session.commit()
        flash("Your portfolio is now " + ("public." if profile.is_public else "private."), "success")
        return redirect(url_for("portfolio.share"))

    link = url_for("portfolio.public", slug=profile.public_slug, _external=True)
    # segno builds the QR code as an inline SVG: no image files, works offline.
    qr_svg = segno.make(link, error="m").svg_inline(scale=6, dark="#0f172a", light="#ffffff")
    return render_template("portfolio/share.html", form=form, profile=profile, link=link, qr_svg=qr_svg)
