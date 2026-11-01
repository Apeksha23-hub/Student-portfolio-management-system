# Student Portfolio Management System

A Flask web app where students store their academic and professional details once,
then generate a professional PDF resume (two themes) and a shareable public portfolio page.
An LLM (Google Gemini free tier) is used **only** to improve text, never to generate documents,
and the app works fully without it.

## Setup (Windows)

Requires Python 3.10 – 3.12 ("Add Python to PATH" ticked during install).

```bat
cd Student-portfolio-management-system
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and set `SECRET_KEY` to a random value:

```bat
python -c "import secrets; print(secrets.token_hex(32))"
```

### Configure Gemini API key (optional — app works without it)

1. Visit https://aistudio.google.com/app/apikey and sign in with your Google account.
2. Click **Create API key** → copy the key.
3. Open `.env` and set:
   ```
   GEMINI_API_KEY=your_key_here
   ```
4. Leave `GEMINI_API_KEY=` blank to disable AI features (the rest of the app still works).

### Seed demo data

```bat
python seed.py
```

Creates two demo users:
- **alice@example.com** / `Demo1234!`
- **bob@example.com** / `Demo1234!`

Each has a complete profile, education, skills, projects, internships, certifications,
achievements and extracurriculars.

### Run the app

```bat
python run.py
```

Open http://127.0.0.1:5000.  The SQLite database is created automatically at `instance/app.db`.

To wipe and recreate all tables:

```bat
flask --app run init-db --reset
```

### Run tests

```bat
.venv\Scripts\python -m pytest tests -q
```

All 53 tests should pass. Tests use an in-memory SQLite database; no network calls are made.

### PDF generation — WeasyPrint / GTK note (Windows)

Resume download uses **WeasyPrint** to produce a PDF.  On Windows, WeasyPrint requires the
GTK3 runtime.  If you see an error like `cannot load library 'libgobject-2.0-0'`, use the
browser-print fallback instead:

```bat
set PDF_ENGINE=browser
python run.py
```

With `PDF_ENGINE=browser` the download route renders the resume as an HTML page and triggers
the browser's built-in print-to-PDF dialog instead.

macOS / Linux: use `source .venv/bin/activate` and `cp .env.example .env` instead.

---

## Database design (ER diagram)

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

- **users** – `id` PK, `name`, `email` UNIQUE, `password_hash`, `created_at`.
- **profiles** – `user_id` is both PK and FK; `public_slug` is random and UNIQUE; `is_public` controls visibility.
- Every child table has `user_id → users.id` with ON DELETE CASCADE.
- `projects.bullets` and `internships.bullets` store JSON bullet lists.
- `ai_usage` tracks daily usage per user; `AI_DAILY_LIMIT` (default 10) caps calls.

---

## Project structure

```
app/            application package (factory, models, forms, blueprints)
  auth/         registration, login, logout
  main/         dashboard, home
  profile/      7 profile-module blueprints (education, skills, …)
  portfolio/    public portfolio + share toggle
  resume/       PDF/HTML resume generator (IT and College themes)
  ai/           Gemini improve-text endpoint
templates/      Jinja2 templates
static/         CSS, JS, uploads/ (photos, certificates)
config.py       settings loaded from .env
seed.py         demo data loader
run.py          entry point
tests/          pytest test suite (53 tests)
```

---

## Manual Test Cases

| ID | Area | Steps | Expected Result |
|----|------|-------|-----------------|
| TC-01 | Auth | Register with valid name / email / password | Redirected to login page; success flash shown |
| TC-02 | Auth | Register with duplicate email | Form re-rendered; "already exists" error shown |
| TC-03 | Auth | Register with mismatched confirm password | Form re-rendered; password mismatch error shown |
| TC-04 | Auth | Log in with correct credentials | Redirected to `/dashboard`; user name shown in nav |
| TC-05 | Auth | Log in with wrong password | Login page re-rendered; "Invalid" error shown |
| TC-06 | Auth | Log out | Session cleared; redirected to home/login |
| TC-07 | Auth | Visit `/dashboard` while logged out | Redirected to `/auth/login` |
| TC-08 | Profile | Add education entry and save | Entry appears in Education list on dashboard |
| TC-09 | Profile | Add skill with proficiency | Skill card appears with correct proficiency level |
| TC-10 | Profile | Edit an existing project | Updated details saved; redirect back to list |
| TC-11 | Profile | Delete a certification | Certification removed from list; DB row gone |
| TC-12 | Security | Log in as User B; try GET `/profile/education/<User A id>/edit` | 403 or 404 returned; no data shown |
| TC-13 | Security | Log in as User B; try POST `/profile/projects/<User A id>/delete` | 403 or 404; project still exists in DB |
| TC-14 | Resume | GET `/resume/preview?theme=it` | 200 response; user name present in HTML body |
| TC-15 | Resume | GET `/resume/preview?theme=college` | 200 response; College theme layout rendered |
| TC-16 | Resume | GET `/resume/preview?theme=unknown` | 200 response; falls back silently to IT theme |
| TC-17 | Resume | GET `/resume/download?theme=it` | 200; `Content-Type` is `application/pdf` (or browser-print HTML if `PDF_ENGINE=browser`) |
| TC-18 | Resume | GET `/resume/download?theme=college` | 200; PDF or browser-print HTML returned |
| TC-19 | Portfolio | POST `/share` with `is_public` checked | 302 redirect; `profile.is_public` is True in DB |
| TC-20 | Portfolio | POST `/share` with `is_public` unchecked (+ submit key) | 302 redirect; `profile.is_public` is False in DB |
| TC-21 | Portfolio | GET `/portfolio/<valid-public-slug>` when public | 200; user's name and sections visible |
| TC-22 | Portfolio | GET `/portfolio/<valid-slug>` when private | 404 returned |
| TC-23 | Portfolio | GET `/portfolio/totally-fake-slug` | 404 returned |
| TC-24 | AI | POST `/ai/improve` with no `GEMINI_API_KEY` set | JSON `{ "ok": false, "message": "<not-configured>" }` returned |
| TC-25 | AI | POST `/ai/improve` after daily limit reached | HTTP 429; `{ "ok": false, "remaining": 0 }` |
| TC-26 | Upload | Upload a `.exe` file renamed to `.png` as a photo | Upload rejected; magic-byte check blocks it |
| TC-27 | Upload | Upload a valid `jpg` > 2 MB | Rejected with file-size error |
| TC-28 | CSRF | Forge a POST to `/profile/education/add` without a CSRF token | 400 Bad Request (CSRF validation fails) |
| TC-29 | Seed | Run `python seed.py`; log in as `alice@example.com` / `Demo1234!` | Dashboard shows Alice's complete profile data |
| TC-30 | E2E | Register → fill profile → preview resume → share → visit public URL | Each step succeeds; public URL shows formatted portfolio |

---

## Security notes

- `.env` is listed in `.gitignore` and never committed.
- All forms extend `FlaskForm` (Flask-WTF) — every POST is CSRF-protected automatically.
- Uploaded files are validated by extension **and** magic-byte signature; stored names are 16-byte hex random strings.
- Maximum upload size: **2 MB** (enforced by `FileSize` validator and `MAX_CONTENT_LENGTH`).
- Every edit/delete route queries the record by its primary key, then checks `record.user_id == current_user.id`; mismatches return `abort(403)`.
- Public portfolio URLs use a random 6-hex-char slug, not the user's database ID.
