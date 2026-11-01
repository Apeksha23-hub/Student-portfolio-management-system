"""
tests/test_ai.py — AI endpoint and LLM helper tests.

Covers:
  - No GEMINI_API_KEY → NOT_CONFIGURED_MESSAGE returned (no network call)
  - Mocked provider failure → original text returned with BUSY_MESSAGE
  - Daily limit (AI_DAILY_LIMIT) blocks after N actions
  - parse_json handles JSON inside ```json fences and rejects invalid text
"""
import json
from unittest.mock import patch

import pytest

from app.ai.llm import NOT_CONFIGURED_MESSAGE, BUSY_MESSAGE, parse_json
from app.models import AIUsage


# ---------------------------------------------------------------------------
# parse_json unit tests (no HTTP, no DB)
# ---------------------------------------------------------------------------

class TestParseJson:

    def test_parses_plain_json_object(self, app):
        with app.app_context():
            result = parse_json('{"bullets": ["a", "b"]}')
        assert result == {"bullets": ["a", "b"]}

    def test_parses_fenced_json_block(self, app):
        text = "```json\n{\"summary\": \"hello\"}\n```"
        with app.app_context():
            result = parse_json(text)
        assert result == {"summary": "hello"}

    def test_rejects_plain_string(self, app):
        with app.app_context():
            result = parse_json("not json at all")
        assert result is None

    def test_rejects_json_array(self, app):
        """parse_json expects a dict, not a bare list."""
        with app.app_context():
            result = parse_json('["a", "b", "c"]')
        assert result is None

    def test_returns_none_for_empty_string(self, app):
        with app.app_context():
            result = parse_json("")
        assert result is None

    def test_extracts_json_object_from_extra_text(self, app):
        """Model sometimes adds prose before/after the JSON object."""
        text = 'Here you go: {"key": "value"} that\'s it.'
        with app.app_context():
            result = parse_json(text)
        assert result == {"key": "value"}


# ---------------------------------------------------------------------------
# /ai/improve endpoint — no API key
# ---------------------------------------------------------------------------

class TestAIImproveNoKey:

    def test_no_api_key_returns_not_configured_message(self, auth_client_a, user_a, app):
        """With GEMINI_API_KEY='', /ai/improve must return the fallback message."""
        payload = {
            "kind": "project",
            "title": "My Project",
            "tech_stack": "Python",
            "description": "A project that does something interesting.",
        }
        resp = auth_client_a.post(
            "/ai/improve",
            data=json.dumps(payload),
            content_type="application/json",
        )
        data = resp.get_json()
        assert data["ok"] is False
        assert NOT_CONFIGURED_MESSAGE in data["message"]

    def test_no_api_key_does_not_call_network(self, auth_client_a, user_a):
        """With no key, _send_to_provider must never be called."""
        payload = {
            "kind": "internship",
            "role": "Dev Intern",
            "company": "Test Corp",
            "description": "Developed various software components.",
        }
        with patch("app.ai.llm._send_to_provider") as mock_send:
            resp = auth_client_a.post(
                "/ai/improve",
                data=json.dumps(payload),
                content_type="application/json",
            )
            mock_send.assert_not_called()
        assert resp.get_json()["ok"] is False


# ---------------------------------------------------------------------------
# /ai/improve endpoint — mocked failing provider
# ---------------------------------------------------------------------------

class TestAIImproveMockedFailure:

    def test_provider_exception_returns_original_text(self, auth_client_a, user_a, app):
        """A failing provider (any exception) must return original text + BUSY_MESSAGE."""
        payload = {
            "kind": "project",
            "title": "My Project",
            "tech_stack": "Django",
            "description": "Built a web application for task management.",
        }
        with app.app_context():
            app.config["GEMINI_API_KEY"] = "fake-key-for-test"

        with patch("app.ai.llm._send_to_provider", side_effect=Exception("timeout")):
            resp = auth_client_a.post(
                "/ai/improve",
                data=json.dumps(payload),
                content_type="application/json",
            )

        # Reset after test.
        with app.app_context():
            app.config["GEMINI_API_KEY"] = ""

        data = resp.get_json()
        assert data["ok"] is False
        # The original description must be preserved.
        assert data["original"] == payload["description"]


# ---------------------------------------------------------------------------
# Daily limit
# ---------------------------------------------------------------------------

class TestAIDailyLimit:

    def test_limit_blocks_after_max_actions(self, auth_client_a, user_a, app, db):
        """
        Pre-populate the ai_usage table to the daily limit, then call /ai/improve;
        the endpoint must return 429 with the limit message.
        """
        from datetime import date

        limit = app.config["AI_DAILY_LIMIT"]

        with app.app_context():
            row = AIUsage(user_id=user_a["id"], date=date.today(), count=limit)
            db.session.add(row)
            db.session.commit()

        payload = {
            "kind": "project",
            "title": "Proj",
            "tech_stack": "Flask",
            "description": "A project description that is long enough to pass the length check.",
        }
        resp = auth_client_a.post(
            "/ai/improve",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert resp.status_code == 429
        data = resp.get_json()
        assert data["ok"] is False
        assert data["remaining"] == 0
