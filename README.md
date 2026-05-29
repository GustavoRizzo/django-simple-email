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

## Getting started

### Step 1 — Create a layout

A layout wraps templates with a shared header and footer. It is **optional** — templates without a layout render their body directly.

**Via the admin**

Go to **Email Layouts → Add**. Write your header and footer as plain HTML. Both fields support Django template syntax.

```html
<!-- header_html -->
<table width="600" style="margin:0 auto;font-family:Arial,sans-serif;">
  <tr><td style="background:#1a1a2e;padding:24px;color:#fff;">
    <strong>{{ company_name }}</strong>
  </td></tr>
  <tr><td style="padding:32px;">
```

```html
<!-- footer_html -->
  </td></tr>
  <tr><td style="background:#f4f4f4;padding:16px;text-align:center;font-size:12px;color:#aaa;">
    © {{ company_name }}
  </td></tr>
</table>
```

**Or using fixture**

```json
[
  {
    "model": "django_simple_email.emaillayout",
    "pk": 1,
    "fields": {
      "name": "default",
      "header_html": "<table width=\"600\" style=\"margin:0 auto\"><tr><td style=\"background:#1a1a2e;padding:24px;color:#fff\"><strong>{{ company_name }}</strong></td></tr><tr><td style=\"padding:32px\">",
      "footer_html": "</td></tr><tr><td style=\"padding:16px;text-align:center;font-size:12px;color:#aaa\">© {{ company_name }}</td></tr></table>"
    }
  }
]
```

---

### Step 2 — Create a template

**Via the admin**

Go to **Email Templates → Add**. The key fields:

| Field | Description |
|---|---|
| **Name** | Slug used in your code — e.g. `welcome`, `password-reset` |
| **Subject default** | Email subject. Supports `{{ variables }}` |
| **HTML body** | Email body. Supports full Django template syntax |
| **Text body** | Plain-text fallback (optional but recommended) |
| **Layout** | Layout to wrap this template (optional) |
| **Sample context** | JSON with example values — used by Preview and Send test |

Example **sample context**:

```json
{
  "name": "Ana Silva",
  "company_name": "My App",
  "cta_url": "https://example.com/dashboard"
}
```

**Via fixture**

```json
[
  {
    "model": "django_simple_email.emailtemplate",
    "pk": 1,
    "fields": {
      "name": "welcome",
      "description": "Sent when a new user signs up",
      "subject_default": "Welcome to {{ company_name }}, {{ name }}!",
      "html_body": "<p>Hi <strong>{{ name }}</strong>, your account is ready.</p><p><a href=\"{{ cta_url }}\">Get started</a></p>",
      "text_body": "Hi {{ name }},\n\nYour account is ready.\n\nGet started: {{ cta_url }}",
      "layout": 1,
      "sample_context": {
        "name": "Ana Silva",
        "company_name": "My App",
        "cta_url": "https://example.com/dashboard"
      }
    }
  }
]
```

Load it with:

```bash
python manage.py loaddata your_fixture.json
```

---

### Step 3 — Send from your code

Call `send_template_mail` anywhere in your Django project — views, signals, Celery tasks, management commands:

```python
from django_simple_email.sending import send_template_mail

send_template_mail(
    template_name="welcome",
    recipient_list=[user.email],
    context={
        "name": user.get_full_name(),
        "company_name": "My App",
        "cta_url": request.build_absolute_uri("/dashboard/"),
    },
)
```

The `context` you pass is merged on top of the template's `sample_context` — you only need to pass the values that change per call.

**Override the subject at call time**

```python
send_template_mail(
    template_name="notification",
    recipient_list=[user.email],
    context={"message": "Your export is ready."},
    subject="[Action required] Your export is ready",
)
```

**Use a custom sender**

```python
send_template_mail(
    template_name="welcome",
    recipient_list=[user.email],
    context={...},
    from_email="onboarding@myapp.com",
)
```

**Or call directly on a template instance**

```python
from django_simple_email.models import EmailTemplate

template = EmailTemplate.objects.get(name="welcome")
template.send_email(recipient_list=[user.email], context={"name": user.get_full_name()})
```

`send_template_mail` uses whatever `EMAIL_BACKEND` you have configured — no lock-in. It integrates natively with [django-anymail](https://anymail.dev): just install anymail, set your `EMAIL_BACKEND`, and emails will go through your chosen ESP (Mailgun, SendGrid, Postmark, Amazon SES, etc.) with no extra configuration.

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
