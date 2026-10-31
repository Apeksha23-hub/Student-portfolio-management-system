"""
Central configuration for the app.

All secret or machine-specific values are read from the .env file
(loaded by python-dotenv) so nothing sensitive is hardcoded.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Read key=value pairs from .env into os.environ (if the file exists).
load_dotenv(BASE_DIR / ".env")


class Config:
    """Default settings used when running the app normally."""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-only-insecure-key-change-me"

    # SQLite by default. Setting DATABASE_URL in .env swaps in MySQL etc.
    # as_posix() keeps the path valid on Windows (forward slashes).
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "sqlite:///" + (BASE_DIR / "instance" / "app.db").as_posix()
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads: 2 MB max request size, only these extensions allowed.
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    UPLOAD_FOLDER = str(BASE_DIR / "static" / "uploads")
    ALLOWED_PHOTO_EXTENSIONS = {"jpg", "jpeg", "png"}
    ALLOWED_CERT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}

    # "auto" = use WeasyPrint if it loads, else browser print. "browser" = always fallback.
    PDF_ENGINE = os.environ.get("PDF_ENGINE", "auto")

    # AI (Google Gemini free tier). Empty key = AI disabled, app still works.
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    LLM_TIMEOUT = int(os.environ.get("LLM_TIMEOUT", "15"))
    AI_DAILY_LIMIT = int(os.environ.get("AI_DAILY_LIMIT", "20"))


class TestConfig(Config):
    """Settings for automated tests: in-memory database, no CSRF tokens."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    WTF_CSRF_ENABLED = False
    GEMINI_API_KEY = ""
