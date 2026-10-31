"""Small helper functions shared by several blueprints."""
import re
import secrets


def slugify(text, max_length=30):
    """'Asha  Rao!' -> 'asha-rao' (lowercase letters, digits and hyphens only)."""
    text = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return text[:max_length].strip("-") or "student"


def generate_unique_slug(name):
    """
    Public portfolio slug like 'asha-rao-3f9a1c'.
    The 6 hex characters come from the secrets module, so links cannot be
    guessed and never reveal the user's database ID.
    """
    from app.models import Profile  # local import avoids a circular import

    while True:
        slug = f"{slugify(name)}-{secrets.token_hex(3)}"
        if not Profile.query.filter_by(public_slug=slug).first():
            return slug
