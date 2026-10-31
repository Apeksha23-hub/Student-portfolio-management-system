"""Resume generator page, live HTML preview, and PDF download."""
from pathlib import Path

from flask import Blueprint, Response, current_app, render_template, request, url_for
from flask_login import current_user, login_required

from app.resume.engine import available_sections, build_resume
from app.resume.pdf import html_to_pdf, weasyprint_available
from app.resume.themes import THEMES, get_theme
from app.utils import newest_first, slugify

bp = Blueprint("resume", __name__)


def _read_selection():
    """
    Read theme / sections / projects from the query string.
    'customized' is a hidden field: when present, an empty list really
    means "nothing ticked" instead of "use the defaults".
    """
    theme_key, _ = get_theme(request.args.get("theme"))
    if request.args.get("customized"):
        sections = request.args.getlist("sections")
        project_ids = {int(pid) for pid in request.args.getlist("projects") if pid.isdigit()}
    else:
        sections, project_ids = None, None
    return theme_key, sections, project_ids


def _render_resume(for_pdf=False, print_mode=False):
    theme_key, sections, project_ids = _read_selection()
    context = build_resume(current_user, theme_key, sections, project_ids)
    if context["show_photo"]:
        photo = Path(current_app.static_folder, *context["profile"].photo_path.split("/"))
        # WeasyPrint reads the photo from disk; the browser loads it over HTTP.
        context["photo_src"] = photo.as_uri() if for_pdf else url_for("static", filename=context["profile"].photo_path)
    return render_template(context["theme"]["template"], print_mode=print_mode, **context)


@bp.route("/")
@login_required
def generator():
    theme_key, sections, project_ids = _read_selection()
    projects = newest_first(current_user.projects.all(), "end_date", "start_date")
    return render_template(
        "resume/generator.html",
        themes=THEMES,
        theme_key=theme_key,
        section_options=available_sections(current_user, theme_key),
        selected_sections=sections,
        projects=projects,
        selected_projects=project_ids,
        max_projects=THEMES[theme_key]["max_projects"],
        pdf_engine="WeasyPrint" if weasyprint_available() else "Browser print",
        query=request.query_string.decode(),
    )


@bp.route("/preview")
@login_required
def preview():
    """The resume as HTML, shown inside an iframe on the generator page."""
    return _render_resume()


@bp.route("/download")
@login_required
def download():
    filename = f"{slugify(current_user.name, 40).replace('-', '_')}_resume.pdf"
    if weasyprint_available():
        html = _render_resume(for_pdf=True)
        pdf = html_to_pdf(html, base_url=current_app.static_folder)
        return Response(pdf, mimetype="application/pdf",
                        headers={"Content-Disposition": f'attachment; filename="{filename}"'})
    # Fallback: print-ready page that opens the browser's print dialog.
    return _render_resume(print_mode=True)
