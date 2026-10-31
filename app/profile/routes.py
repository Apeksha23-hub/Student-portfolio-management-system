"""
Profile modules: the personal profile page plus seven list modules
(education, skills, certifications, projects, internships, achievements,
extracurriculars).

Instead of writing list/add/edit/delete four times for each module, every
module is described once in the MODULES dictionary and the same four
generic views handle all of them.
"""
from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.forms import (
    AchievementForm, CertificationForm, EducationForm, ExtracurricularForm,
    InternshipForm, PersonalProfileForm, ProjectForm, SkillForm,
)
from app.models import (
    Achievement, Certification, Education, Extracurricular, Internship, Project, Skill,
)
from app.utils import date_range, delete_upload, month_year, newest_first, save_upload

bp = Blueprint("profile", __name__)


# ---------------------------------------------------------------------------
# Module registry: one entry per list module.
#   model     - SQLAlchemy model class
#   form      - Flask-WTF form class
#   relation  - name of the User relationship (current_user.<relation>)
#   sort      - function that orders the user's entries for display
#   display   - function returning (title, subtitle, meta) for the list page
#   upload    - optional file upload settings
# ---------------------------------------------------------------------------

MODULES = {
    "education": {
        "title": "Education",
        "singular": "education entry",
        "model": Education,
        "form": EducationForm,
        "relation": "education",
        "sort": lambda items: newest_first(items, "end_year", "start_year"),
        "display": lambda e: (
            e.level,
            ", ".join(x for x in [e.institution, e.board_university] if x),
            " | ".join(x for x in [date_range(e.start_year, e.end_year), e.score] if x),
        ),
    },
    "skills": {
        "title": "Skills",
        "singular": "skill",
        "model": Skill,
        "form": SkillForm,
        "relation": "skills",
        "sort": lambda items: sorted(items, key=lambda s: ((s.category or ""), s.name.lower())),
        "display": lambda s: (s.name, s.category, s.proficiency),
    },
    "certifications": {
        "title": "Certifications",
        "singular": "certification",
        "model": Certification,
        "form": CertificationForm,
        "relation": "certifications",
        "sort": lambda items: newest_first(items, "date"),
        "display": lambda c: (c.title, c.issuer, month_year(c.date)),
        "upload": {
            "field": "certificate_file",
            "column": "file_path",
            "folder": "certificates",
            "allowed": "ALLOWED_CERT_EXTENSIONS",
        },
    },
    "projects": {
        "title": "Projects",
        "singular": "project",
        "model": Project,
        "form": ProjectForm,
        "relation": "projects",
        "sort": lambda items: newest_first(items, "end_date", "start_date"),
        "display": lambda p: (p.title, p.tech_stack, date_range(p.start_date, p.end_date)),
    },
    "internships": {
        "title": "Internships",
        "singular": "internship",
        "model": Internship,
        "form": InternshipForm,
        "relation": "internships",
        "sort": lambda items: newest_first(items, "end_date", "start_date"),
        "display": lambda i: (i.role, i.company, date_range(i.start_date, i.end_date)),
    },
    "achievements": {
        "title": "Achievements",
        "singular": "achievement",
        "model": Achievement,
        "form": AchievementForm,
        "relation": "achievements",
        "sort": lambda items: newest_first(items, "date"),
        "display": lambda a: (a.title, a.description, month_year(a.date)),
    },
    "extracurriculars": {
        "title": "Extracurriculars",
        "singular": "activity",
        "model": Extracurricular,
        "form": ExtracurricularForm,
        "relation": "extracurriculars",
        "sort": lambda items: list(items),
        "display": lambda x: (x.activity, x.role, x.description),
    },
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_module_or_404(module_name):
    module = MODULES.get(module_name)
    if module is None:
        abort(404)
    return module


def get_owned_item_or_403(model, item_id):
    """Load a record and make sure it belongs to the logged-in user."""
    item = db.session.get(model, item_id)
    if item is None:
        abort(404)
    if item.user_id != current_user.id:
        abort(403)  # someone else's record: forbidden
    return item


def copy_form_to_item(form, item):
    """Copy every form field whose name matches a table column onto the record."""
    columns = item.__table__.columns.keys()
    for field in form:
        if field.name in columns and field.name not in ("id", "user_id"):
            setattr(item, field.name, field.data)
    # Bullets are edited as one-per-line text but stored as a JSON list.
    if "bullets_text" in form:
        item.set_bullets((form.bullets_text.data or "").splitlines())


def handle_module_upload(module, form, item):
    """Save a new uploaded file for this record. Returns False if it was rejected."""
    upload = module.get("upload")
    if not upload:
        return True
    file_data = form[upload["field"]].data
    if not file_data or not getattr(file_data, "filename", ""):
        return True  # no new file chosen: keep the existing one

    allowed = current_app.config[upload["allowed"]]
    new_path = save_upload(file_data, upload["folder"], allowed)
    if new_path is None:
        form[upload["field"]].errors.append("This file type is not allowed or the file is damaged.")
        return False
    delete_upload(getattr(item, upload["column"]))
    setattr(item, upload["column"], new_path)
    return True


# ---------------------------------------------------------------------------
# Personal profile (one row per user, so no list page)
# ---------------------------------------------------------------------------

@bp.route("/", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile
    form = PersonalProfileForm(obj=profile)
    if request.method == "GET":
        form.name.data = current_user.name

    if form.validate_on_submit():
        current_user.name = form.name.data
        for field in ("headline", "phone", "location", "linkedin", "github",
                      "website", "bio", "summary"):
            setattr(profile, field, form[field].data)

        photo = form.photo.data
        if photo and getattr(photo, "filename", ""):
            new_path = save_upload(photo, "photos", current_app.config["ALLOWED_PHOTO_EXTENSIONS"])
            if new_path is None:
                form.photo.errors.append("Only valid JPG or PNG images are allowed.")
                return render_template("modules/profile_form.html", form=form, profile=profile,
                                       modules=MODULES, active="personal")
            delete_upload(profile.photo_path)
            profile.photo_path = new_path
        elif form.remove_photo.data:
            delete_upload(profile.photo_path)
            profile.photo_path = None

        db.session.commit()
        flash("Profile saved.", "success")
        return redirect(url_for("profile.edit_profile"))

    return render_template("modules/profile_form.html", form=form, profile=profile,
                           modules=MODULES, active="personal")


# ---------------------------------------------------------------------------
# Generic list / add / edit / delete for every module in MODULES
# ---------------------------------------------------------------------------

@bp.route("/<module_name>/")
@login_required
def list_items(module_name):
    module = get_module_or_404(module_name)
    items = module["sort"](getattr(current_user, module["relation"]).all())
    rows = [(item, module["display"](item)) for item in items]
    return render_template("modules/list.html", module=module, module_name=module_name,
                           rows=rows, modules=MODULES, active=module_name)


@bp.route("/<module_name>/add", methods=["GET", "POST"])
@login_required
def add_item(module_name):
    module = get_module_or_404(module_name)
    form = module["form"]()

    if form.validate_on_submit():
        item = module["model"](user_id=current_user.id)
        copy_form_to_item(form, item)
        if handle_module_upload(module, form, item):
            db.session.add(item)
            db.session.commit()
            flash(f"{module['singular'].capitalize()} added.", "success")
            return redirect(url_for("profile.list_items", module_name=module_name))

    return render_template("modules/form.html", form=form, module=module, module_name=module_name,
                           item=None, modules=MODULES, active=module_name)


@bp.route("/<module_name>/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def edit_item(module_name, item_id):
    module = get_module_or_404(module_name)
    item = get_owned_item_or_403(module["model"], item_id)
    form = module["form"](obj=item)
    if request.method == "GET" and "bullets_text" in form:
        form.bullets_text.data = "\n".join(item.get_bullets())

    if form.validate_on_submit():
        copy_form_to_item(form, item)
        if handle_module_upload(module, form, item):
            db.session.commit()
            flash(f"{module['singular'].capitalize()} updated.", "success")
            return redirect(url_for("profile.list_items", module_name=module_name))
        db.session.rollback()

    return render_template("modules/form.html", form=form, module=module, module_name=module_name,
                           item=item, modules=MODULES, active=module_name)


@bp.route("/<module_name>/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(module_name, item_id):
    module = get_module_or_404(module_name)
    item = get_owned_item_or_403(module["model"], item_id)
    if module.get("upload"):
        delete_upload(getattr(item, module["upload"]["column"]))
    db.session.delete(item)
    db.session.commit()
    flash(f"{module['singular'].capitalize()} deleted.", "info")
    return redirect(url_for("profile.list_items", module_name=module_name))
