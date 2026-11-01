"""
tests/test_resume.py — Resume generator tests.

Verifies:
  - Preview returns 200 for both themes
  - Download returns 200 for both themes (browser-print fallback in tests)
  - A user with no data still gets a 200 (empty sections are skipped)
  - call_llm is NOT called during preview or download
"""
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_and_login(client, email="resume_user@test.com", name="Resume User"):
    client.post(
        "/auth/register",
        data={"name": name, "email": email,
              "password": "Password1!", "confirm_password": "Password1!"},
    )
    client.post(
        "/auth/login",
        data={"email": email, "password": "Password1!"},
        follow_redirects=False,
    )


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------

class TestResumePreview:

    def test_preview_it_theme_returns_200(self, auth_client_a, user_a):
        resp = auth_client_a.get("/resume/preview?theme=it")
        assert resp.status_code == 200

    def test_preview_college_theme_returns_200(self, auth_client_a, user_a):
        resp = auth_client_a.get("/resume/preview?theme=college")
        assert resp.status_code == 200

    def test_preview_contains_user_name(self, auth_client_a, user_a):
        resp = auth_client_a.get("/resume/preview?theme=it")
        assert b"User A" in resp.data

    def test_preview_unknown_theme_falls_back_to_it(self, auth_client_a, user_a):
        """An unknown theme key should silently fall back to the IT theme."""
        resp = auth_client_a.get("/resume/preview?theme=nonexistent")
        assert resp.status_code == 200

    def test_preview_empty_profile_skips_sections_no_error(self, client):
        """A user with no projects/skills/etc should still get a 200."""
        _register_and_login(client, "empty_user@test.com", "Empty User")
        resp = client.get("/resume/preview?theme=it")
        assert resp.status_code == 200

    def test_call_llm_not_called_during_preview(self, auth_client_a, user_a):
        """The LLM must never be called while generating a preview."""
        with patch("app.ai.llm.call_llm") as mock_llm:
            auth_client_a.get("/resume/preview?theme=it")
            mock_llm.assert_not_called()

        with patch("app.ai.llm.call_llm") as mock_llm:
            auth_client_a.get("/resume/preview?theme=college")
            mock_llm.assert_not_called()


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

class TestResumeDownload:

    def test_download_it_theme_returns_200(self, auth_client_a, user_a):
        resp = auth_client_a.get("/resume/download?theme=it")
        # Accepts either PDF bytes or browser-print HTML fallback.
        assert resp.status_code == 200

    def test_download_college_theme_returns_200(self, auth_client_a, user_a):
        resp = auth_client_a.get("/resume/download?theme=college")
        assert resp.status_code == 200

    def test_call_llm_not_called_during_download(self, auth_client_a, user_a):
        """The LLM must never be called while generating a PDF download."""
        with patch("app.ai.llm.call_llm") as mock_llm:
            auth_client_a.get("/resume/download?theme=it")
            mock_llm.assert_not_called()

        with patch("app.ai.llm.call_llm") as mock_llm:
            auth_client_a.get("/resume/download?theme=college")
            mock_llm.assert_not_called()
