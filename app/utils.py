"""Small helper functions shared by several blueprints."""
import os
import re
import secrets
from datetime import date, datetime

from flask import current_app
from werkzeug.utils import secure_filename


# ---------------------------------------------------------------------------
# Public portfolio slug
# ---------------------------------------------------------------------------

def slugify(text, max_length=30):
    """'Asha  Rao!' -> 'asha-rao' (lowercase letters, digits and hyphens only)."""
    text = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return text[:max_length].strip("-") or "student"


def generate_unique_slug(name):
    """
    Public portfolio slug like 'asha-rao-3f9a1c'.
    The 6 hex characters come from the secrets module, so links cannot be
    guessed and never reveal the user's database ID.
    """
    from app.models import Profile  # local import avoids a circular import

    while True:
        slug = f"{slugify(name)}-{secrets.token_hex(3)}"
        if not Profile.query.filter_by(public_slug=slug).first():
            return slug


# ---------------------------------------------------------------------------
# File uploads
# ---------------------------------------------------------------------------

# First bytes ("magic numbers") of each allowed file type. Checking them
# stops someone from uploading e.g. an .exe renamed to .png.
_FILE_SIGNATURES = {
    "pdf": [b"%PDF"],
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
}


def save_upload(file_storage, subfolder, allowed_extensions):
    """
    Validate and save an uploaded file under static/uploads/<subfolder>/.
    Returns the path relative to static/ (for url_for('static', ...)),
    or None if the file is not allowed.
    """
    original = secure_filename(file_storage.filename or "")
    extension = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if extension not in allowed_extensions:
        return None

    header = file_storage.stream.read(8)
    file_storage.stream.seek(0)
    if not any(header.startswith(sig) for sig in _FILE_SIGNATURES.get(extension, [])):
        return None

    # Random stored name: never trust or reuse the user's file name.
    stored_name = f"{secrets.token_hex(16)}.{extension}"
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(folder, exist_ok=True)
    file_storage.save(os.path.join(folder, stored_name))
    return f"uploads/{subfolder}/{stored_name}"


def delete_upload(relative_path):
    """Remove a previously uploaded file (ignores missing files)."""
    if not relative_path or not relative_path.startswith("uploads/"):
        return
    # "uploads/photos/abc.png" -> <UPLOAD_FOLDER>/photos/abc.png
    full_path = os.path.join(current_app.config["UPLOAD_FOLDER"], *relative_path.split("/")[1:])
    if os.path.isfile(full_path):
        os.remove(full_path)


# ---------------------------------------------------------------------------
# Sorting and formatting
# ---------------------------------------------------------------------------

def _sortable(value):
    if value is None:
        return float("-inf")
    if isinstance(value, (date, datetime)):
        return value.toordinal()
    return float(value)


def newest_first(items, end_attr, start_attr=None):
    """
    Sort entries newest first. Ongoing entries (start set, no end) come first,
    then by end (or start) date/year. Done in Python so it works on any database.
    """
    def sort_key(item):
        end = getattr(item, end_attr, None)
        start = getattr(item, start_attr, None) if start_attr else None
        ongoing = end is None and start is not None
        return (ongoing, _sortable(end if end is not None else start), _sortable(start))

    return sorted(items, key=sort_key, reverse=True)


def month_year(value):
    """date(2025, 1, 5) -> 'Jan 2025'. Used as a Jinja filter."""
    return value.strftime("%b %Y") if value else ""


def date_range(start, end):
    """'Jan 2024 - Present', 'Jan 2024 - Jun 2024', or '' when no dates."""
    if isinstance(start, int) or isinstance(end, int):
        left, right = (str(start) if start else ""), (str(end) if end else "")
    else:
        left, right = month_year(start), month_year(end)
    if left and right:
        return left if left == right else f"{left} - {right}"
    if left:
        return f"{left} - Present"
    return right


# ---------------------------------------------------------------------------
# Profile completeness
# ---------------------------------------------------------------------------

def profile_completeness(user):
    """
    Returns (percent, missing) where missing is a list of
    (tip text, module name) for the dashboard. module None = personal profile.
    """
    p = user.profile
    checks = [
        ("Add a headline", bool(p.headline), None),
        ("Write a short bio", bool(p.bio), None),
        ("Add a professional summary", bool(p.summary), None),
        ("Add phone and location", bool(p.phone and p.location), None),
        ("Add your LinkedIn or GitHub", bool(p.linkedin or p.github), None),
        ("Upload a profile photo", bool(p.photo_path), None),
        ("Add your education", user.education.count() > 0, "education"),
        ("Add at least 3 skills", user.skills.count() >= 3, "skills"),
        ("Add a project", user.projects.count() > 0, "projects"),
        ("Add an internship", user.internships.count() > 0, "internships"),
        ("Add a certification", user.certifications.count() > 0, "certifications"),
        ("Add an achievement", user.achievements.count() > 0, "achievements"),
        ("Add an extracurricular activity", user.extracurriculars.count() > 0, "extracurriculars"),
    ]
    done = sum(1 for _, ok, _ in checks if ok)
    percent = round(done * 100 / len(checks))
    missing = [(tip, module) for tip, ok, module in checks if not ok]
    return percent, missing
