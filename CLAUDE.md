# CLAUDE.md — django-simple-email

## Project Overview

**django-simple-email** is a simple Django app for sending emails, providing an easy-to-use interface and reusable components. It includes a `demo_project` for local development and testing.

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
├── django_simple_email/    # The library package (published to PyPI)
│   ├── templates/          # HTML templates
│   ├── templatetags/       # Custom template tags
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│   └── apps.py
├── demo_project/           # Local Django project for development/testing
│   ├── kernel/             # Django settings, urls, wsgi/asgi
│   └── manage.py
├── .github/workflows/      # CI pipelines
│   └── ci.yml              # Runs lint + test on push/PR to main
├── template.config.json    # All project-specific values (for fork adaptation)
├── pyproject.toml          # Project config (Poetry + Ruff + Taskipy)
└── poetry.lock
```

## Development Commands (via taskipy)

All commands are run with `poetry run task <name>`:

| Command | Description |
|---|---|
| `task run-demo` | Run the demo project server |
| `task migrate` | Apply database migrations |
| `task setup` | Migrate + create superuser |
| `task test` | Run the test suite |
| `task lint` | Run ruff linter |
| `task lint-fix` | Run ruff linter and auto-fix |

## Toolchain

- **Dependency manager:** Poetry
- **Linter/Formatter:** Ruff (`line-length = 120`, rules: F, E, W, I, N, UP, B)
- **Type checker:** mypy
- **Task runner:** taskipy

## Publishing Workflow

**Manual:**
```bash
poetry version patch   # bump version (e.g. 0.1.0 → 0.1.1)
poetry build
poetry publish
```

## Forking This Template

All project-specific values are centralized in [template.config.json](template.config.json). When forking to create a new library, update that file first, then ask the AI:

> "Adapte este template para um novo app chamado `django-cache-tools`. Leia o `template.config.json`, atualize os valores para o novo projeto e propague as mudanças em todos os arquivos."

Files that reference template values and will need updating:
- `template.config.json`
- `pyproject.toml` (name, description, version, author)
- `django_simple_email/` → rename folder to new package name
- `django_simple_email/apps.py` (class name, app name)
- `demo_project/kernel/settings.py` (INSTALLED_APPS, URL_PYPI, URL_GITHUB)
- `demo_project/kernel/tests/` (app_name references)
- `django_simple_email/templates/django_simple_email/` → rename folder
- `django_simple_email/urls.py` (app_name)
- `README.md`
- `.github/workflows/` (se quiser CI no novo repositório)

## Language Convention

- **Communication & internal Claude files:** Portuguese is allowed
- **Code, variable names, comments:** English only
