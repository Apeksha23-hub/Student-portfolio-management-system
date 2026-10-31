"""
Database models (one class = one table).

Every child table has a user_id foreign key with ON DELETE CASCADE, and
the User relationships use cascade="all, delete-orphan", so deleting a
user removes all of their data both in the database and in the ORM.
Only portable column types are used, so MySQL can replace SQLite.
"""
import json
from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login_manager


def _child_relationship(model_name):
    """Shortcut for a User -> child-table relationship with cascading deletes."""
    return db.relationship(
        model_name,
        backref="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="dynamic",
    )


def _user_fk():
    return db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )


class BulletsMixin:
    """Helpers for the 'bullets' column, stored as a JSON list of strings."""

    def get_bullets(self):
        if not self.bullets:
            return []
        try:
            data = json.loads(self.bullets)
        except (ValueError, TypeError):
            return []
        return [str(b) for b in data if str(b).strip()] if isinstance(data, list) else []

    def set_bullets(self, bullet_list):
        cleaned = [b.strip() for b in bullet_list if b and b.strip()]
        self.bullets = json.dumps(cleaned) if cleaned else None


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # One-to-one: each user has exactly one profile row.
    profile = db.relationship(
        "Profile", backref="user", uselist=False,
        cascade="all, delete-orphan", passive_deletes=True,
    )
    education = _child_relationship("Education")
    skills = _child_relationship("Skill")
    certifications = _child_relationship("Certification")
    projects = _child_relationship("Project")
    internships = _child_relationship("Internship")
    achievements = _child_relationship("Achievement")
    extracurriculars = _child_relationship("Extracurricular")
    ai_usage = _child_relationship("AIUsage")

    def set_password(self, password):
        # werkzeug stores a salted hash, never the plain password.
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login calls this to get the logged-in user from the session."""
    return db.session.get(User, int(user_id))


class Profile(db.Model):
    __tablename__ = "profiles"

    # user_id is also the primary key: one profile per user.
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    headline = db.Column(db.String(150))
    bio = db.Column(db.Text)
    linkedin = db.Column(db.String(255))
    github = db.Column(db.String(255))
    website = db.Column(db.String(255))
    photo_path = db.Column(db.String(255))
    summary = db.Column(db.Text)
    public_slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    is_public = db.Column(db.Boolean, default=False, nullable=False)


class Education(db.Model):
    __tablename__ = "education"

    id = db.Column(db.Integer, primary_key=True)
    user_id = _user_fk()
    level = db.Column(db.String(50), nullable=False)  # e.g. B.E., Class XII
    institution = db.Column(db.String(150), nullable=False)
    board_university = db.Column(db.String(150))
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    score = db.Column(db.String(30))  # "8.6 CGPA" or "91%"


class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = _user_fk()
    name = db.Column(db.String(60), nullable=False)
    category = db.Column(db.String(60))  # e.g. Languages, Frameworks, Tools
    proficiency = db.Column(db.String(20))  # Beginner / Intermediate / Advanced / Expert


class Certification(db.Model):
    __tablename__ = "certifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = _user_fk()
    title = db.Column(db.String(150), nullable=False)
    issuer = db.Column(db.String(150))
    date = db.Column(db.Date)
    credential_url = db.Column(db.String(255))
    file_path = db.Column(db.String(255))  # optional uploaded certificate


class Project(BulletsMixin, db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = _user_fk()
    title = db.Column(db.String(150), nullable=False)
    tech_stack = db.Column(db.String(255))  # comma separated: "Flask, SQLite"
    description = db.Column(db.Text)
    bullets = db.Column(db.Text)  # JSON list, AI-improved and accepted by student
    github_link = db.Column(db.String(255))
    demo_link = db.Column(db.String(255))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    include_in_resume = db.Column(db.Boolean, default=True, nullable=False)

    def tech_list(self):
        return [t.strip() for t in (self.tech_stack or "").split(",") if t.strip()]


class Internship(BulletsMixin, db.Model):
    __tablename__ = "internships"

    id = db.Column(db.Integer, primary_key=True)
    user_id = _user_fk()
    company = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    description = db.Column(db.Text)
    bullets = db.Column(db.Text)


class Achievement(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    user_id = _user_fk()
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date)


class Extracurricular(db.Model):
    __tablename__ = "extracurriculars"

    id = db.Column(db.Integer, primary_key=True)
    user_id = _user_fk()
    activity = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100))
    description = db.Column(db.Text)


class AIUsage(db.Model):
    """One row per user per day, counting AI actions for the daily limit."""

    __tablename__ = "ai_usage"
    __table_args__ = (db.UniqueConstraint("user_id", "date", name="uq_ai_usage_user_date"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = _user_fk()
    date = db.Column(db.Date, default=date.today, nullable=False)
    count = db.Column(db.Integer, default=0, nullable=False)
