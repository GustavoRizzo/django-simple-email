# django-simple-email

[![PyPI](https://img.shields.io/pypi/v/django-simple-email.svg)](https://pypi.org/project/django-simple-email/)
[![Python](https://img.shields.io/pypi/pyversions/django-simple-email.svg)](https://pypi.org/project/django-simple-email/)
[![Django](https://img.shields.io/pypi/djversions/django-simple-email.svg)](https://pypi.org/project/django-simple-email/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Edit your transactional email templates from the Django admin. No redeploy. No template files. Just open the admin, change the copy, and send a test to see it live.

---

## The problem it solves

Normally, changing the text in a transactional email means editing a file, committing, pushing, and waiting for a deploy. With `django-simple-email`, templates live in the database. Anyone with admin access can edit them, and a **Preview** + **Send test** button lets you confirm the result before it ever reaches a real user.

---

## Install

```bash
pip install django-simple-email
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_simple_email",
]
```

Run migrations:

```bash
python manage.py migrate
```

That's it.

---

## Core concepts

### EmailLayout

A layout is a reusable envelope: a **header** and a **footer** that wrap the content of multiple templates. Define your brand header once — logo, colors, top bar — and reuse it across every email.

Layouts are optional. A template without a layout renders its body directly.

### EmailTemplate

A template is the email itself: subject, HTML body, and an optional plain-text fallback. Both `subject` and `html_body` support **Django template syntax**, so you can use `{{ variable }}`, `{% if %}`, `{% for %}`, and everything else Django templates offer.

Each template stores a `sample_context` — a JSON object with example values. This is what **Preview** and **Send test** use, so you always have realistic data to work with.

---

## Sending email from code

```python
from django_simple_email.sending import send_email

send_email(
    template_name="welcome",
    to=["user@example.com"],
    context={"name": "Ana", "cta_url": "https://example.com/dashboard"},
)
```

The `context` you pass is merged on top of the template's `sample_context`. Both `subject` and `html_body` are rendered as Django templates with the merged context before sending.

`send_email` uses whatever `EMAIL_BACKEND` you have configured — no lock-in.

---

## Admin features

### Templates list

The templates list shows a **Preview HTML** link and a **Send test** button per row, so you can check any template without opening it.

### Change page

When editing a template, the **Metadata** section at the bottom has:

- **Preview HTML** — opens the fully rendered email (layout + body) in a new tab
- **Send test** — renders and sends the email to `DJANGO_SIMPLE_EMAIL_TEST_RECIPIENT` immediately, showing a success or error message inline

---

## Settings

| Setting | Default | Description |
|---|---|---|
| `DJANGO_SIMPLE_EMAIL_TEST_RECIPIENT` | `"test@test.com"` | Address used by the admin test-send button |

```python
# settings.py
DJANGO_SIMPLE_EMAIL_TEST_RECIPIENT = "you@yourcompany.com"
```

---

## Local development

### Requirements

- [Poetry](https://python-poetry.org/)
- [Docker](https://docs.docker.com/get-docker/) — for Mailpit (local email catcher)

### First-time setup

```bash
git clone https://github.com/GustavoRizzo/django-simple-email.git
cd django-simple-email
poetry install
poetry run task setup          # migrate + create superuser
poetry run task load-fixtures  # load sample layouts and templates
```

### Running

```bash
poetry run task mailpit    # Mailpit SMTP on :1025, web UI on :8025
poetry run task run-demo   # Django on localhost:8000
```

Go to [localhost:8000/admin](http://localhost:8000/admin) and log in with the superuser you created.

The fixtures include a `default` layout and three templates (`welcome`, `password-reset`, `notification`), plus seasonal layout variants (Halloween, Christmas, New Year) with matching template variations — enough to explore the preview and test-send features right away.

### Tests and linting

```bash
poetry run task test
poetry run task lint
poetry run task lint-fix
```

### Releasing

```bash
poetry version patch   # 0.1.0 → 0.1.1
poetry build
poetry publish
```
