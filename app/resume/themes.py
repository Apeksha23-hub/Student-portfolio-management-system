"""
Resume themes.

A theme = one entry in THEMES + one Jinja template + one CSS file.
To add a new theme, copy an entry below, create templates/resume/theme_<key>.html
(extending base_resume.html) and static/css/resume_<key>.css. Nothing else changes.

Section keys must match a partial in templates/sections/<key>.html.
"""

# Default heading for each section. A theme can override any of them in "titles".
SECTION_TITLES = {
    "summary": "Professional Summary",
    "skills": "Technical Skills",
    "projects": "Projects",
    "internships": "Internships & Experience",
    "education": "Education",
    "certifications": "Certifications",
    "achievements": "Achievements",
    "extracurriculars": "Extracurricular Activities",
    "personal_details": "Personal Details",
}

THEMES = {
    "it": {
        "name": "IT / Industry",
        "description": "Single column, ATS-friendly, no photo. Skills and projects first.",
        "template": "resume/theme_it.html",
        "css": "css/resume_it.css",
        "sections": ["summary", "skills", "projects", "internships",
                     "education", "certifications", "achievements"],
        "show_photo": False,
        "education_style": "list",
        "titles": {},
        # Limits that keep the resume close to one page.
        "max_projects": 3,
        "max_internships": 2,
        "max_bullets": 3,
        "max_certifications": 4,
        "max_achievements": 4,
        "max_extracurriculars": 3,
        "max_description_chars": 220,
    },
    "college": {
        "name": "College / Campus",
        "description": "Education and CGPA first, with a personal details block for campus placements.",
        "template": "resume/theme_college.html",
        "css": "css/resume_college.css",
        "sections": ["education", "projects", "internships", "skills",
                     "achievements", "extracurriculars", "personal_details"],
        "show_photo": True,
        "education_style": "table",
        "titles": {"skills": "Skills", "education": "Academic Qualifications"},
        "max_projects": 2,
        "max_internships": 2,
        "max_bullets": 2,
        "max_certifications": 3,
        "max_achievements": 4,
        "max_extracurriculars": 3,
        "max_description_chars": 180,
    },
}

DEFAULT_THEME = "it"


def get_theme(key):
    """Return (key, theme) and fall back to the default for unknown keys."""
    if key not in THEMES:
        key = DEFAULT_THEME
    return key, THEMES[key]
