"""
Resume engine: turns the student's SAVED database rows into a clean,
ready-to-render structure. All data logic lives here (sorting, limits,
truncation, skipping empty sections), so templates stay simple.

This module never calls the LLM: resumes only use text already saved.
"""
from pathlib import Path

from flask import current_app

from app.forms import SKILL_CATEGORIES
from app.resume.themes import SECTION_TITLES, get_theme
from app.utils import date_range, month_year, newest_first


def truncate(text, limit):
    """Shorten text to `limit` characters at a word boundary, adding an ellipsis."""
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(",.;:-")
    return cut + "..."


def _entry_bullets(entry, theme):
    """Saved bullets if any, otherwise the (shortened) description as one bullet."""
    bullets = entry.get_bullets()[: theme["max_bullets"]]
    if not bullets and entry.description:
        bullets = [truncate(entry.description, theme["max_description_chars"])]
    return bullets


def _build_section(key, user, profile, theme, project_ids):
    """Return the data for one section, or None/empty when there is nothing to show."""
    limit = theme["max_description_chars"]

    if key == "summary":
        return truncate(profile.summary, 450) if profile.summary else None

    if key == "skills":
        groups = {}
        for skill in user.skills.all():
            groups.setdefault(skill.category or "Other", []).append(skill.name)
        order = {name: i for i, name in enumerate(SKILL_CATEGORIES)}
        return [(cat, groups[cat]) for cat in sorted(groups, key=lambda c: order.get(c, 99))]

    if key == "projects":
        projects = user.projects.all()
        if project_ids is None:
            projects = [p for p in projects if p.include_in_resume]
        else:
            projects = [p for p in projects if p.id in project_ids]
        projects = newest_first(projects, "end_date", "start_date")[: theme["max_projects"]]
        return [{
            "title": p.title,
            "tech": p.tech_list(),
            "dates": date_range(p.start_date, p.end_date),
            "github": p.github_link,
            "demo": p.demo_link,
            "bullets": _entry_bullets(p, theme),
        } for p in projects]

    if key == "internships":
        items = newest_first(user.internships.all(), "end_date", "start_date")
        return [{
            "role": i.role,
            "company": i.company,
            "dates": date_range(i.start_date, i.end_date),
            "bullets": _entry_bullets(i, theme),
        } for i in items[: theme["max_internships"]]]

    if key == "education":
        items = newest_first(user.education.all(), "end_year", "start_year")
        return [{
            "level": e.level,
            "institution": e.institution,
            "board": e.board_university,
            "years": date_range(e.start_year, e.end_year),
            "end_year": e.end_year,
            "score": e.score,
        } for e in items]

    if key == "certifications":
        items = newest_first(user.certifications.all(), "date")
        return [{
            "title": c.title,
            "issuer": c.issuer,
            "date": month_year(c.date),
            "url": c.credential_url,
        } for c in items[: theme["max_certifications"]]]

    if key == "achievements":
        items = newest_first(user.achievements.all(), "date")
        return [{
            "title": a.title,
            "description": truncate(a.description, limit // 2) if a.description else "",
            "date": month_year(a.date),
        } for a in items[: theme["max_achievements"]]]

    if key == "extracurriculars":
        return [{
            "activity": x.activity,
            "role": x.role,
            "description": truncate(x.description, limit // 2) if x.description else "",
        } for x in user.extracurriculars.all()[: theme["max_extracurriculars"]]]

    if key == "personal_details":
        rows = [
            ("Email", user.email),
            ("Phone", profile.phone),
            ("Location", profile.location),
            ("LinkedIn", profile.linkedin),
            ("GitHub", profile.github),
            ("Website", profile.website),
        ]
        return [(label, value) for label, value in rows if value]

    return None


def available_sections(user, theme_key):
    """For the generator page: [(key, title, has_data)] in theme order."""
    _, theme = get_theme(theme_key)
    result = []
    for key in theme["sections"]:
        data = _build_section(key, user, user.profile, theme, project_ids=[p.id for p in user.projects])
        title = theme["titles"].get(key, SECTION_TITLES[key])
        result.append((key, title, bool(data)))
    return result


def build_resume(user, theme_key, sections=None, project_ids=None):
    """
    Build everything a resume template needs.
      sections    - list of section keys to include (None = all of the theme's)
      project_ids - set of project ids to include (None = those marked include_in_resume)
    """
    theme_key, theme = get_theme(theme_key)
    profile = user.profile

    chosen = []
    for key in theme["sections"]:
        if sections is not None and key not in sections:
            continue
        data = _build_section(key, user, profile, theme, project_ids)
        if data:  # empty sections are skipped automatically
            chosen.append({
                "key": key,
                "title": theme["titles"].get(key, SECTION_TITLES[key]),
                "data": data,
            })

    css_path = Path(current_app.static_folder) / theme["css"]
    return {
        "theme_key": theme_key,
        "theme": theme,
        "theme_css": css_path.read_text(encoding="utf-8"),
        "user": user,
        "profile": profile,
        "sections": chosen,
        "show_photo": theme["show_photo"] and bool(profile.photo_path),
    }
