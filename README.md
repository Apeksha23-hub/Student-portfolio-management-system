# Student Portfolio Management System

A Flask web app where students store their academic and professional details once,
then generate a professional PDF resume (two themes) and a shareable public portfolio page.
An LLM (Google Gemini free tier) is used **only** to improve text, never to generate documents,
and the app works fully without it.

> Status: Phase 1 (setup, models, home page, auth, dashboard shell). Later phases add the
> profile modules, resume engine, AI features, portfolio, seed data and tests.

## Setup (Windows)

Requires Python 3.10 to 3.12 ("Add Python to PATH" ticked during install).

```bat
cd student-portfolio
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set `SECRET_KEY` to a random value:

```bat
python -c "import secrets; print(secrets.token_hex(32))"
```

Run the app:

```bat
python run.py
```

Open http://127.0.0.1:5000. The SQLite database is created automatically at `instance/app.db`.

To wipe and recreate all tables:

```bat
flask --app run init-db --reset
```

macOS / Linux: use `source .venv/bin/activate` and `cp .env.example .env` instead.

## Database design (ER diagram description)

```
users 1 ─── 1 profiles
users 1 ─── * education
users 1 ─── * skills
users 1 ─── * certifications
users 1 ─── * projects
users 1 ─── * internships
users 1 ─── * achievements
users 1 ─── * extracurriculars
users 1 ─── * ai_usage        (one row per user per day)
```

- **users** (`id` PK, `name`, `email` UNIQUE, `password_hash`, `created_at`) is the parent of every other table.
- **profiles** uses `user_id` as both primary key and foreign key, so each user has exactly one profile.
  `public_slug` is UNIQUE and random (e.g. `asha-rao-3f9a1c`); `is_public` controls portfolio visibility.
- Every child table has `user_id` → `users.id` with **ON DELETE CASCADE**: deleting a user deletes all their rows.
  SQLite only enforces this when `PRAGMA foreign_keys=ON`, which the app turns on for every connection.
- `projects.bullets` and `internships.bullets` hold a JSON list of accepted resume bullet points.
- `ai_usage` has a UNIQUE (`user_id`, `date`) pair and a `count` column for the daily AI limit.
- Only portable column types are used, so switching `DATABASE_URL` to MySQL needs no model changes.

## Project structure

```
app/            application package (factory, models, forms, blueprints)
templates/      Jinja2 templates
static/         CSS, JS (Tailwind is stored locally so the app works offline), uploads
config.py       settings loaded from .env
run.py          entry point
```
