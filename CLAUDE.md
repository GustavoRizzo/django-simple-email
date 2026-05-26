# CLAUDE.md — django-simple-email

## Project Overview

**django-simple-email** is a reusable Django app for managing transactional email templates directly from the Django admin — no deploys needed to change content. It provides editable templates with Django template syntax, reusable layout components (header/footer), HTML preview, and a test-send button.

- **Package:** `django_simple_email`
- **Current version:** 0.1.0
- **Python:** >=3.14
- **Django:** >=5.2
- **License:** MIT
- **PyPI:** https://pypi.org/project/django-simple-email/
- **GitHub:** https://github.com/GustavoRizzo/django-simple-email

## Project Structure

```
django-simple-email/
├── django_simple_email/        # The library package (published to PyPI)
│   ├── migrations/             # Django migrations for EmailLayout and EmailTemplate
│   ├── fixtures/               # Sample data for local development
│   │   ├── sample_data.json    # Default layout + welcome, password-reset, notification templates
│   │   └── seasonal_data.json  # Halloween, Christmas, New Year layouts + welcome variations
│   ├── tests/                  # Unit tests for the library
│   │   ├── test_rendering.py   # Tests for render_template()
│   │   ├── test_sending.py     # Tests for send_email()
│   │   └── test_admin.py       # Tests for preview and send-test admin views
│   ├── templates/              # HTML templates (home page)
│   ├── templatetags/           # Custom template tags
│   ├── admin.py                # EmailLayoutAdmin, EmailTemplateAdmin (with preview + send test)
│   ├── apps.py
│   ├── models.py               # EmailLayout, EmailTemplate
│   ├── rendering.py            # render_template() → (subject, html, text)
│   ├── sending.py              # send_email(template_name, to, context, from_email)
│   ├── urls.py
│   └── views.py
├── demo_project/               # Local Django project for development/testing
│   ├── kernel/                 # Django settings, urls, wsgi/asgi, tests
│   └── manage.py
├── docker/
│   └── compose.yml             # Mailpit for local email catching (not published to PyPI)
├── .github/workflows/
│   └── ci.yml                  # Runs lint + test on push/PR to main
├── pyproject.toml              # Project config (Poetry + Ruff + Taskipy)
└── poetry.lock
```

## Core Models

### EmailLayout
Reusable header/footer that wraps multiple templates. Fields: `name`, `header_html`, `footer_html`.

### EmailTemplate
The email itself. Fields: `name` (slug, used in code), `subject`, `html_body`, `text_body`, `layout` (FK, optional), `sample_context` (JSON used for preview and test send).

Both `subject` and `html_body` support Django template syntax (`{{ var }}`, `{% if %}`, etc.).

## Public API

```python
from django_simple_email.sending import send_email

send_email(
    template_name="welcome",       # EmailTemplate.name
    to=["user@example.com"],
    context={"name": "Ana"},       # merged on top of sample_context
    from_email="sender@example.com",  # optional
)
```

## Development Commands (via taskipy)

All commands are run with `poetry run task <name>` from the project root:

| Command | Description |
|---|---|
| `task mailpit` | Start Mailpit SMTP catcher (UI at localhost:8025) |
| `task run-demo` | Run the demo project server at localhost:8000 |
| `task migrate` | Apply database migrations |
| `task setup` | Migrate + create superuser |
| `task load-fixtures` | Load sample and seasonal fixtures into the demo DB |
| `task test` | Run the full test suite (32 tests) |
| `task lint` | Run ruff linter |
| `task lint-fix` | Run ruff linter and auto-fix |

## Settings

| Setting | Default | Description |
|---|---|---|
| `DJANGO_SIMPLE_EMAIL_TEST_RECIPIENT` | `"test@test.com"` | Address used by the admin test-send button |

## Demo Setup (first time)

```bash
docker compose -f docker/compose.yml up -d   # start Mailpit
poetry install
poetry run task setup           # migrate + create superuser (admin/admin)
poetry run task load-fixtures   # load sample templates and layouts
poetry run task run-demo        # http://localhost:8000/admin
```

## Toolchain

- **Dependency manager:** Poetry
- **Linter/Formatter:** Ruff (`line-length = 120`, rules: F, E, W, I, N, UP, B)
- **Type checker:** mypy
- **Task runner:** taskipy
- **Local email catcher:** Mailpit (via Docker, port 1025 SMTP / 8025 UI)

## Publishing Workflow

```bash
poetry version patch   # bump version (e.g. 0.1.0 → 0.1.1)
poetry build
poetry publish
```

## Language Convention

- **Communication & internal Claude files:** Portuguese is allowed
- **Code, variable names, comments:** English only

## Out of Scope

- Email queuing, retry, scheduling (post-office covers this)
- Bulk email / newsletters
- Allauth templates (those live in `templates/account/`)
