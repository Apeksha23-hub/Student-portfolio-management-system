"""Public home page, the dashboard, and error pages."""
from flask import Blueprint, render_template
from flask_login import current_user, login_required

bp = Blueprint("main", __name__)


@bp.route("/")
def home():
    return render_template("home.html")


@bp.route("/dashboard")
@login_required
def dashboard():
    # Number of saved entries in each profile section.
    counts = {
        "Education": current_user.education.count(),
        "Skills": current_user.skills.count(),
        "Certifications": current_user.certifications.count(),
        "Projects": current_user.projects.count(),
        "Internships": current_user.internships.count(),
        "Achievements": current_user.achievements.count(),
        "Extracurriculars": current_user.extracurriculars.count(),
    }
    return render_template("dashboard.html", counts=counts)


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
