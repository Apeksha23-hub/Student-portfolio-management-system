"""
All Flask-WTF forms. Each form automatically includes a CSRF token
and validates input on the server side.
"""
import re

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileSize
from wtforms import (
    BooleanField, DateField, EmailField, IntegerField, PasswordField, SelectField,
    StringField, SubmitField, TextAreaField, URLField,
)
from wtforms.validators import (
    URL, DataRequired, Email, EqualTo, Length, NumberRange, Optional, Regexp, ValidationError,
)

from app.models import User


class RegisterForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")

    def validate_email(self, field):
        """Custom validator: WTForms calls validate_<fieldname> automatically."""
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember me")
    submit = SubmitField("Log in")


# ---------------------------------------------------------------------------
# Shared helpers for profile forms
# ---------------------------------------------------------------------------

def strip_or_none(value):
    """Filter: trim spaces; turn empty strings into None so the DB stores NULL."""
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def normalize_url(value):
    """Filter: 'github.com/asha' -> 'https://github.com/asha'."""
    value = strip_or_none(value)
    if value and not re.match(r"^https?://", value, re.IGNORECASE):
        value = "https://" + value
    return value


def optional_url(label):
    return URLField(label, filters=[normalize_url],
                    validators=[Optional(), URL(message="Enter a valid link."), Length(max=255)])


def optional_text(label, max_length, **kwargs):
    return StringField(label, filters=[strip_or_none],
                       validators=[Optional(), Length(max=max_length)], **kwargs)


def required_text(label, max_length, **kwargs):
    return StringField(label, filters=[strip_or_none],
                       validators=[DataRequired(), Length(max=max_length)], **kwargs)


def long_text(label, max_length=1000, rows=4, **kwargs):
    return TextAreaField(label, filters=[strip_or_none],
                         validators=[Optional(), Length(max=max_length)],
                         render_kw={"rows": rows}, **kwargs)


def optional_date(label):
    return DateField(label, validators=[Optional()])


class DateRangeMixin:
    """Adds a check that the end date is not before the start date."""

    def validate_end_date(self, field):
        if field.data and self.start_date.data and field.data < self.start_date.data:
            raise ValidationError("End date cannot be before the start date.")


BULLETS_HELP = "One bullet per line. These exact lines appear on your resume."
PHOTO_TYPES = ["jpg", "jpeg", "png"]
CERT_TYPES = ["pdf", "jpg", "jpeg", "png"]
MAX_UPLOAD_BYTES = 2 * 1024 * 1024


# ---------------------------------------------------------------------------
# Profile module forms
# ---------------------------------------------------------------------------

class PersonalProfileForm(FlaskForm):
    name = required_text("Full name", 100)
    headline = optional_text("Headline", 150, description="e.g. Final-year Computer Engineering student")
    phone = StringField("Phone", filters=[strip_or_none], validators=[
        Optional(), Regexp(r"^[0-9+\-\s()]{7,20}$", message="Enter a valid phone number.")])
    location = optional_text("Location", 100, description="City, State")
    linkedin = optional_url("LinkedIn URL")
    github = optional_url("GitHub URL")
    website = optional_url("Personal website")
    bio = long_text("About me (portfolio)", 1000, rows=4,
                    description="A friendly paragraph shown on your public portfolio.")
    summary = long_text("Professional summary (resume)", 600, rows=3,
                        description="2-3 lines shown at the top of your resume.")
    photo = FileField("Profile photo", validators=[
        FileAllowed(PHOTO_TYPES, "Only JPG or PNG images are allowed."),
        FileSize(MAX_UPLOAD_BYTES, message="Photo must be 2 MB or smaller.")],
        description="JPG or PNG, max 2 MB. Used on the portfolio and the College theme.")
    remove_photo = BooleanField("Remove current photo")
    submit = SubmitField("Save profile")


class EducationForm(FlaskForm):
    level = required_text("Degree / Level", 50, description="e.g. B.E. Computer Engineering, Class XII")
    institution = required_text("Institution", 150)
    board_university = optional_text("Board / University", 150)
    start_year = IntegerField("Start year", validators=[Optional(), NumberRange(1950, 2100)])
    end_year = IntegerField("End year (or expected)", validators=[Optional(), NumberRange(1950, 2100)])
    score = optional_text("Score", 30, description="e.g. 8.7 CGPA or 91%")
    submit = SubmitField("Save")

    def validate_end_year(self, field):
        if field.data and self.start_year.data and field.data < self.start_year.data:
            raise ValidationError("End year cannot be before the start year.")


SKILL_CATEGORIES = [
    "Programming Languages", "Frameworks & Libraries", "Databases",
    "Tools & Platforms", "Core Subjects", "Soft Skills", "Other",
]
PROFICIENCY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]


class SkillForm(FlaskForm):
    name = required_text("Skill", 60, description="e.g. Python")
    category = SelectField("Category", choices=SKILL_CATEGORIES, validators=[DataRequired()])
    proficiency = SelectField("Proficiency", choices=PROFICIENCY_LEVELS, default="Intermediate",
                              validators=[DataRequired()])
    submit = SubmitField("Save")


class CertificationForm(FlaskForm):
    title = required_text("Certificate title", 150)
    issuer = optional_text("Issued by", 150, description="e.g. NPTEL, Coursera, AWS")
    date = optional_date("Issue date")
    credential_url = optional_url("Credential URL")
    certificate_file = FileField("Certificate file (optional)", validators=[
        FileAllowed(CERT_TYPES, "Only PDF, JPG or PNG files are allowed."),
        FileSize(MAX_UPLOAD_BYTES, message="File must be 2 MB or smaller.")],
        description="PDF, JPG or PNG, max 2 MB. Uploading a new file replaces the old one.")
    submit = SubmitField("Save")


class ProjectForm(DateRangeMixin, FlaskForm):
    title = required_text("Project title", 150)
    tech_stack = optional_text("Tech stack", 255, description="Comma separated, e.g. Python, Flask, SQLite")
    description = long_text("Description", 1000, rows=4,
                            description="What the project does and what you did.")
    bullets_text = long_text("Resume bullet points", 1200, rows=4, description=BULLETS_HELP)
    github_link = optional_url("GitHub link")
    demo_link = optional_url("Live demo link")
    start_date = optional_date("Start date")
    end_date = optional_date("End date (leave empty if ongoing)")
    include_in_resume = BooleanField("Include in resume", default=True)
    submit = SubmitField("Save")


class InternshipForm(DateRangeMixin, FlaskForm):
    company = required_text("Company", 150)
    role = required_text("Role", 150, description="e.g. Web Development Intern")
    start_date = optional_date("Start date")
    end_date = optional_date("End date (leave empty if ongoing)")
    description = long_text("Description", 1000, rows=4, description="What you worked on.")
    bullets_text = long_text("Resume bullet points", 1200, rows=4, description=BULLETS_HELP)
    submit = SubmitField("Save")


class AchievementForm(FlaskForm):
    title = required_text("Achievement", 150, description="e.g. Winner, Smart India Hackathon 2025")
    description = long_text("Details", 500, rows=3)
    date = optional_date("Date")
    submit = SubmitField("Save")


class ExtracurricularForm(FlaskForm):
    activity = required_text("Activity / Club", 150, description="e.g. Coding Club, NSS")
    role = optional_text("Your role", 100, description="e.g. Technical Head")
    description = long_text("Details", 500, rows=3)
    submit = SubmitField("Save")
