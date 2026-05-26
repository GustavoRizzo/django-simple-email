from django.core.exceptions import ValidationError
from django.test import TestCase

from django_simple_email.models import EmailLayout, EmailTemplate


class EmailLayoutValidationTests(TestCase):
    def test_valid_layout_passes(self):
        layout = EmailLayout(name="valid", header_html="<h1>{{ company }}</h1>", footer_html="<footer></footer>")
        layout.full_clean()

    def test_invalid_header_syntax_raises(self):
        layout = EmailLayout(name="bad", header_html="{% if %}", footer_html="")
        with self.assertRaises(ValidationError) as ctx:
            layout.full_clean()
        self.assertIn("header_html", ctx.exception.message_dict)

    def test_invalid_footer_syntax_raises(self):
        layout = EmailLayout(name="bad", header_html="", footer_html="{% for %}")
        with self.assertRaises(ValidationError) as ctx:
            layout.full_clean()
        self.assertIn("footer_html", ctx.exception.message_dict)

    def test_empty_fields_pass(self):
        layout = EmailLayout(name="empty", header_html="", footer_html="")
        layout.full_clean()


class EmailTemplateValidationTests(TestCase):
    def _valid_template(self, **kwargs):
        defaults = {"name": "test", "subject": "Hi {{ name }}", "html_body": "<p>{{ name }}</p>"}
        defaults.update(kwargs)
        return EmailTemplate(**defaults)

    def test_valid_template_passes(self):
        self._valid_template().full_clean()

    def test_invalid_subject_syntax_raises(self):
        t = self._valid_template(subject="{% if %}")
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("subject", ctx.exception.message_dict)

    def test_invalid_html_body_syntax_raises(self):
        t = self._valid_template(html_body="{% for x %}")
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("html_body", ctx.exception.message_dict)

    def test_invalid_text_body_syntax_raises(self):
        t = self._valid_template(text_body="{% block %}")
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("text_body", ctx.exception.message_dict)

    def test_multiple_invalid_fields_reported_together(self):
        t = self._valid_template(subject="{% if %}", html_body="{% for x %}")
        with self.assertRaises(ValidationError) as ctx:
            t.full_clean()
        self.assertIn("subject", ctx.exception.message_dict)
        self.assertIn("html_body", ctx.exception.message_dict)
