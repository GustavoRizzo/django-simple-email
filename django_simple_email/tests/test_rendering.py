from django.test import TestCase

from django_simple_email.models import EmailLayout, EmailTemplate


def make_template(**kwargs) -> EmailTemplate:
    defaults = {
        "name": "test",
        "subject": "Hello {{ name }}",
        "html_body": "<p>Hi {{ name }}</p>",
        "text_body": "Hi {{ name }}",
        "sample_context": {"name": "World"},
    }
    defaults.update(kwargs)
    return EmailTemplate.objects.create(**defaults)


def make_layout(**kwargs) -> EmailLayout:
    defaults = {"name": "test-layout", "header_html": "<header>", "footer_html": "<footer>"}
    defaults.update(kwargs)
    return EmailLayout.objects.create(**defaults)


class SubjectRenderingTests(TestCase):
    def test_renders_subject_variables(self):
        subject, _, _ = make_template().render()
        self.assertEqual(subject, "Hello World")

    def test_subject_uses_passed_context(self):
        subject, _, _ = make_template().render(context={"name": "Ana"})
        self.assertEqual(subject, "Hello Ana")

    def test_passed_context_merges_with_sample_context(self):
        template = make_template(
            subject="{{ greeting }}, {{ name }}!",
            sample_context={"greeting": "Olá", "name": "World"},
        )
        subject, _, _ = template.render(context={"name": "Ana"})
        self.assertEqual(subject, "Olá, Ana!")


class HtmlBodyRenderingTests(TestCase):
    def test_renders_html_variables(self):
        _, html, _ = make_template().render()
        self.assertEqual(html, "<p>Hi World</p>")

    def test_template_without_layout_renders_body_only(self):
        template = make_template(html_body="<p>standalone</p>", sample_context={})
        _, html, _ = template.render()
        self.assertEqual(html, "<p>standalone</p>")

    def test_layout_header_and_footer_wrap_body(self):
        layout = make_layout(header_html="<HEADER>", footer_html="<FOOTER>")
        template = make_template(html_body="<BODY>", layout=layout, sample_context={})
        _, html, _ = template.render()
        self.assertEqual(html, "<HEADER><BODY><FOOTER>")

    def test_layout_variables_are_rendered_with_context(self):
        layout = make_layout(
            header_html="<h1>{{ company }}</h1>",
            footer_html="<footer>{{ company }}</footer>",
        )
        template = make_template(html_body="<p>body</p>", layout=layout, sample_context={"company": "Acme"})
        _, html, _ = template.render()
        self.assertEqual(html, "<h1>Acme</h1><p>body</p><footer>Acme</footer>")


class TextBodyRenderingTests(TestCase):
    def test_renders_text_variables(self):
        _, _, text = make_template().render()
        self.assertEqual(text, "Hi World")

    def test_empty_text_body_returns_empty_string(self):
        _, _, text = make_template(text_body="").render()
        self.assertEqual(text, "")
