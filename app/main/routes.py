"""Public home page, the dashboard, and error pages."""
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.utils import profile_completeness

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    # Number of saved entries in each profile section.
    from app.profile.routes import MODULES

    # Number of saved entries in each profile section.
    counts = [
        (name, module["title"], getattr(current_user, module["relation"]).count())
        for name, module in MODULES.items()
    ]
    percent, missing = profile_completeness(current_user)
    return render_template("dashboard.html", counts=counts, percent=percent, missing=missing)


@bp.app_errorhandler(403)
def forbidden(error):
    return render_template(
        "error.html", code=403, title="Not allowed",
        message="You can only view or change your own records.",
    ), 403


@bp.app_errorhandler(404)
def not_found(error):
    return render_template(
        "error.html", code=404, title="Page not found",
        message="The page you are looking for does not exist or is private.",
    ), 404


@bp.app_errorhandler(413)
def too_large(error):
    return render_template(
        "error.html", code=413, title="File too large",
        message="Uploads must be 2 MB or smaller.",
    ), 413
