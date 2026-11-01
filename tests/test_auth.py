"""
tests/test_auth.py — Authentication tests.

Covers:
  - Successful registration
  - Duplicate email rejection
  - Login success and wrong-password failure
  - Protected routes redirect to login when not authenticated
"""
import pytest


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

def test_register_success(client):
    """A new user can register and is redirected to the login page."""
    resp = client.post(
        "/auth/register",
        data={
            "name": "Test Student",
            "email": "newstudent@test.com",
            "password": "Password1!",
            "confirm_password": "Password1!",
        },
        follow_redirects=False,
    )
    # Should redirect (302) after successful registration.
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_register_duplicate_email(client):
    """Registering with an already-used email shows a validation error."""
    data = {
        "name": "First Student",
        "email": "duplicate@test.com",
        "password": "Password1!",
        "confirm_password": "Password1!",
    }
    # First registration — must succeed.
    resp1 = client.post("/auth/register", data=data, follow_redirects=False)
    assert resp1.status_code == 302

    # Second registration with the same email — must fail.
    data["name"] = "Second Student"
    resp2 = client.post("/auth/register", data=data, follow_redirects=True)
    assert resp2.status_code == 200
    assert b"already exists" in resp2.data


def test_register_mismatched_passwords(client):
    """Mismatched confirmation password fails validation."""
    resp = client.post(
        "/auth/register",
        data={
            "name": "Alice",
            "email": "alice@test.com",
            "password": "Password1!",
            "confirm_password": "WrongPass!",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    # The form is re-rendered (not redirected).
    assert b"Password" in resp.data


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def test_login_success(client):
    """Valid credentials redirect to the dashboard."""
    # Register first.
    client.post(
        "/auth/register",
        data={
            "name": "Login User",
            "email": "loginuser@test.com",
            "password": "Password1!",
            "confirm_password": "Password1!",
        },
    )
    resp = client.post(
        "/auth/login",
        data={"email": "loginuser@test.com", "password": "Password1!"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert "/dashboard" in resp.headers["Location"]


def test_login_wrong_password(client):
    """Wrong password shows an error and stays on the login page."""
    client.post(
        "/auth/register",
        data={
            "name": "Wrong Pass User",
            "email": "wrongpass@test.com",
            "password": "Password1!",
            "confirm_password": "Password1!",
        },
    )
    resp = client.post(
        "/auth/login",
        data={"email": "wrongpass@test.com", "password": "BadPassword!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Invalid" in resp.data


def test_login_unknown_email(client):
    """Unknown email shows the same generic error (no info leak)."""
    resp = client.post(
        "/auth/login",
        data={"email": "nobody@test.com", "password": "Password1!"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Invalid" in resp.data


# ---------------------------------------------------------------------------
# Protected-route redirect
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", [
    "/dashboard",
    "/profile/",
    "/resume/",
    "/resume/preview",
    "/resume/download",
    "/share",
])
def test_protected_routes_redirect_when_logged_out(client, path):
    """Unauthenticated requests to protected routes redirect to login."""
    resp = client.get(path, follow_redirects=False)
    assert resp.status_code == 302
    location = resp.headers["Location"]
    assert "/auth/login" in location
