"""Register, login and logout."""
from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app import db
from app.forms import LoginForm, RegisterForm
from app.models import Profile, User
from app.utils import generate_unique_slug

bp = Blueprint("auth", __name__)


def _is_safe_next(target):
    """Only allow redirects to pages on this site (prevents open redirects)."""
    if not target:
        return False
    parts = urlsplit(target)
    return not parts.scheme and not parts.netloc and target.startswith("/")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data.strip(), email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        # Every user gets an empty, private profile with a random public slug.
        user.profile = Profile(public_slug=generate_unique_slug(user.name), is_public=False)
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        # Same message for wrong email or wrong password (don't leak which).
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
        else:
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page if _is_safe_next(next_page) else url_for("main.dashboard"))
    return render_template("auth/login.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    # POST + CSRF token so another site cannot log the user out with a link.
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
