from django.test import TestCase

from django_simple_email.models import EmailLayout, EmailTemplate


def make_template(**kwargs) -> EmailTemplate:
    defaults = {
        "name": "test",
        "subject_default": "Hello {{ name }}",
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
            subject_default="{{ greeting }}, {{ name }}!",
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


class LayoutPreviewRenderTests(TestCase):
    def test_includes_header_and_footer(self):
        layout = make_layout(header_html="<HEADER>", footer_html="<FOOTER>")
        html = layout.preview_render()
        self.assertIn("<HEADER>", html)
        self.assertIn("<FOOTER>", html)

    def test_placeholder_is_between_header_and_footer(self):
        layout = make_layout(header_html="<HEADER>", footer_html="<FOOTER>")
        html = layout.preview_render()
        header_pos = html.index("<HEADER>")
        footer_pos = html.index("<FOOTER>")
        placeholder_pos = html.index("Your email content will appear here.")
        self.assertLess(header_pos, placeholder_pos)
        self.assertLess(placeholder_pos, footer_pos)

    def test_variables_are_resolved_with_context(self):
        layout = make_layout(header_html="<h1>{{ company }}</h1>", footer_html="<footer>{{ company }}</footer>")
        html = layout.preview_render(context={"company": "Acme"})
        self.assertIn("<h1>Acme</h1>", html)
        self.assertIn("<footer>Acme</footer>", html)
        self.assertNotIn("{{ company }}", html)

    def test_empty_header_and_footer_renders_only_placeholder(self):
        layout = make_layout(header_html="", footer_html="")
        html = layout.preview_render()
        self.assertIn("Your email content will appear here.", html)

    def test_returns_string(self):
        layout = make_layout()
        self.assertIsInstance(layout.preview_render(), str)
