"""
tests/conftest.py — Shared test fixtures.

The app is created fresh for each test session using TestConfig:
  - in-memory SQLite with StaticPool so the same connection is reused
    across threads/calls (avoids "no such table" errors)
  - CSRF disabled so test POSTs don't need tokens
  - GEMINI_API_KEY empty so no network calls happen
"""
import pytest
from sqlalchemy import StaticPool
from sqlalchemy.pool import StaticPool as SAStaticPool

from app import create_app, db as _db
from app.models import (
    Achievement, Certification, Education, Extracurricular,
    Internship, Profile, Project, Skill, User,
)
from config import TestConfig


# ---------------------------------------------------------------------------
# App / DB fixtures
# ---------------------------------------------------------------------------

class _TestConfig(TestConfig):
    """Extend TestConfig with StaticPool so in-memory SQLite works in tests."""
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }


@pytest.fixture(scope="session")
def app():
    """One Flask app for the whole test session."""
    application = create_app(_TestConfig)
    return application


@pytest.fixture()
def db(app):
    """Fresh database for each test: create tables, yield, then drop all."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app, db):
    """Test client with a clean DB for every test."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Helper: register + login a user
# ---------------------------------------------------------------------------

def register_user(client, name, email, password="Password1!"):
    return client.post(
        "/auth/register",
        data={"name": name, "email": email,
              "password": password, "confirm_password": password},
        follow_redirects=False,
    )


def login_user(client, email, password="Password1!"):
    return client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=False,
    )


# ---------------------------------------------------------------------------
# Pre-built user fixtures
# ---------------------------------------------------------------------------

def _create_user_with_data(app, db_session, name, email, password="Password1!",
                            is_public=False):
    """
    Create a user with a profile row and one record in each module.
    Returns the User object.
    """
    from datetime import date
    from app.utils import generate_unique_slug

    user = User(name=name, email=email)
    user.set_password(password)
    db_session.add(user)
    db_session.flush()

    profile = Profile(
        user_id=user.id,
        public_slug=generate_unique_slug(name),
        headline="Test headline",
        is_public=is_public,
    )
    db_session.add(profile)

    db_session.add(Education(
        user_id=user.id, level="B.E. CS", institution="Test University",
        start_year=2021, end_year=2025, score="8.0 CGPA",
    ))
    db_session.add(Skill(
        user_id=user.id, name="Python", category="Programming Languages",
        proficiency="Advanced",
    ))
    db_session.add(Certification(
        user_id=user.id, title="Test Cert", issuer="Test Issuer",
        date=date(2024, 1, 1),
    ))

    proj = Project(
        user_id=user.id, title="Test Project",
        tech_stack="Flask", include_in_resume=True,
        description="A test project description.",
        start_date=date(2024, 1, 1), end_date=date(2024, 6, 1),
    )
    proj.set_bullets(["Built the backend.", "Wrote unit tests."])
    db_session.add(proj)

    intern_ = Internship(
        user_id=user.id, company="Test Corp", role="Dev Intern",
        start_date=date(2024, 5, 1), end_date=date(2024, 7, 31),
        description="Worked on APIs.",
    )
    intern_.set_bullets(["Developed 10 REST endpoints."])
    db_session.add(intern_)

    db_session.add(Achievement(
        user_id=user.id, title="Test Award",
        description="Won the test hackathon.", date=date(2024, 3, 1),
    ))
    db_session.add(Extracurricular(
        user_id=user.id, activity="Coding Club", role="Member",
        description="Attended weekly meetups.",
    ))

    db_session.commit()
    return user


@pytest.fixture()
def user_a(app, db):
    """A fully set-up user (User A)."""
    with app.app_context():
        return _create_user_with_data(app, db.session, "User A", "usera@test.com")


@pytest.fixture()
def user_b(app, db):
    """A second user (User B) — used to test ownership enforcement."""
    with app.app_context():
        return _create_user_with_data(app, db.session, "User B", "userb@test.com")


@pytest.fixture()
def auth_client_a(client, user_a):
    """A test client already logged in as User A."""
    login_user(client, "usera@test.com")
    return client


@pytest.fixture()
def auth_client_b(app, client, user_a, user_b):
    """
    A test client already logged in as User B.
    user_a is requested so both users exist in the DB before login.
    """
    login_user(client, "userb@test.com")
    return client
