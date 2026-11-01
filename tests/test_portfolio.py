"""
tests/test_portfolio.py — Public portfolio page tests.

Verifies:
  - /portfolio/<slug> returns 200 when is_public=True
  - /portfolio/<slug> returns 404 when is_public=False
  - The public slug does NOT equal the user's integer id
  - /share toggle switches is_public and redirects
"""
import pytest
from app.models import Profile, User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_slug(app, user):
    with app.app_context():
        profile = Profile.query.filter_by(user_id=user.id).first()
        return profile.public_slug


# ---------------------------------------------------------------------------
# Public access
# ---------------------------------------------------------------------------

class TestPublicPortfolio:

    def test_public_portfolio_returns_200_when_public(self, app, client, user_a,
                                                       auth_client_a):
        # Make it public via the share route.
        auth_client_a.post(
            "/share",
            data={"is_public": "y"},
            follow_redirects=False,
        )
        slug = _get_slug(app, user_a)
        resp = client.get(f"/portfolio/{slug}")
        assert resp.status_code == 200

    def test_private_portfolio_returns_404(self, app, client, user_a,
                                           auth_client_a):
        # Ensure the profile is private.
        auth_client_a.post(
            "/share",
            data={},            # is_public unchecked
            follow_redirects=False,
        )
        slug = _get_slug(app, user_a)
        resp = client.get(f"/portfolio/{slug}")
        assert resp.status_code == 404

    def test_nonexistent_slug_returns_404(self, client):
        resp = client.get("/portfolio/totally-fake-slug-xyz999")
        assert resp.status_code == 404

    def test_slug_is_not_user_id(self, app, user_a):
        """The slug must not be the numeric user id (prevents enumeration)."""
        slug = _get_slug(app, user_a)
        with app.app_context():
            u = User.query.filter_by(email="usera@test.com").first()
            assert slug != str(u.id), "Slug must not be the plain user ID!"

    def test_public_portfolio_contains_user_name(self, app, client, user_a,
                                                  auth_client_a):
        auth_client_a.post("/share", data={"is_public": "y"}, follow_redirects=False)
        slug = _get_slug(app, user_a)
        resp = client.get(f"/portfolio/{slug}")
        assert b"User A" in resp.data


# ---------------------------------------------------------------------------
# Share toggle
# ---------------------------------------------------------------------------

class TestShareToggle:

    def test_share_toggle_makes_portfolio_public(self, app, auth_client_a, user_a):
        resp = auth_client_a.post(
            "/share",
            data={"is_public": "y"},
            follow_redirects=False,
        )
        assert resp.status_code == 302
        with app.app_context():
            profile = Profile.query.filter_by(user_id=user_a.id).first()
            assert profile.is_public is True

    def test_share_toggle_makes_portfolio_private(self, app, auth_client_a, user_a):
        # First make it public.
        auth_client_a.post("/share", data={"is_public": "y"}, follow_redirects=False)
        # Now toggle back to private (unchecked checkbox = field absent).
        resp = auth_client_a.post("/share", data={}, follow_redirects=False)
        assert resp.status_code == 302
        with app.app_context():
            profile = Profile.query.filter_by(user_id=user_a.id).first()
            assert profile.is_public is False

    def test_share_page_requires_login(self, client):
        resp = client.get("/share", follow_redirects=False)
        assert resp.status_code == 302
        assert "/auth/login" in resp.headers["Location"]
