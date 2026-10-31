"""
Application factory.

create_app() builds the Flask app, connects the extensions (database,
login manager, CSRF protection) and registers every blueprint.
Using a factory lets tests create a fresh app with a test config.
"""
import os
import sqlite3
from datetime import date

import click
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config import Config

# Extensions are created here without an app, then bound in create_app().
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """SQLite ignores ON DELETE CASCADE unless foreign keys are switched on."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(config_class=Config):
    # templates/ and static/ live in the project root, next to the app/ package.
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(config_class)

    # Make sure the folders for the SQLite file and uploads exist.
    os.makedirs(app.instance_path, exist_ok=True)
    for sub in ("photos", "certificates"):
        os.makedirs(os.path.join(app.config["UPLOAD_FOLDER"], sub), exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # where @login_required redirects
    login_manager.login_message_category = "info"

    # Import models so SQLAlchemy knows about every table.
    from app import models  # noqa: F401

    # Register blueprints (one per feature area).
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.profile import bp as profile_bp
    from app.resume import bp as resume_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(resume_bp, url_prefix="/resume")

    # Jinja filters used by several templates.
    from app.utils import date_range, month_year, pretty_url

    app.jinja_env.filters["month_year"] = month_year
    app.jinja_env.filters["pretty_url"] = pretty_url
    app.jinja_env.globals["date_range"] = date_range

    # Create any missing tables on startup (existing data is untouched).
    with app.app_context():
        db.create_all()

    @app.context_processor
    def inject_globals():
        # Values available in every template.
        return {"now_year": date.today().year}

    register_cli_commands(app)
    return app


def register_cli_commands(app):
    @app.cli.command("init-db")
    @click.option("--reset", is_flag=True, help="Drop all tables first (deletes data!).")
    def init_db(reset):
        """Create the database tables. Usage: flask --app run init-db [--reset]"""
        if reset:
            db.drop_all()
            click.echo("Dropped all tables.")
        db.create_all()
        click.echo("Database tables are ready.")
