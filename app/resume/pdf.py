"""
PDF generation with WeasyPrint, when it is available.

On Windows WeasyPrint needs the GTK/Pango libraries. If they are missing,
importing it raises OSError. We detect that once and the app falls back to
a print-optimised HTML page (browser "Save as PDF") instead of crashing.
Set PDF_ENGINE=browser in .env to force the fallback.
"""
from functools import lru_cache

from flask import current_app


@lru_cache(maxsize=1)
def _load_weasyprint():
    try:
        from weasyprint import HTML  # noqa: WPS433 (import inside function on purpose)
        return HTML
    except (ImportError, OSError) as error:  # OSError = missing GTK/Pango DLLs
        print(f"[resume] WeasyPrint not available, using browser print fallback: {error}")
        return None


def weasyprint_available():
    if current_app.config.get("PDF_ENGINE", "auto") == "browser":
        return False
    return _load_weasyprint() is not None


def html_to_pdf(html, base_url):
    """Convert an HTML string to PDF bytes. Call only if weasyprint_available()."""
    html_class = _load_weasyprint()
    return html_class(string=html, base_url=base_url).write_pdf()
