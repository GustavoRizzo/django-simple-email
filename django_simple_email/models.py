from django.db import models
from django.template import Context, Template

from .validation import validate_template_syntax


def _render_part(source: str, context: dict) -> str:
    return Template(source).render(Context(context))


class EmailLayout(models.Model):
    name = models.CharField(max_length=100, unique=True)
    header_html = models.TextField(blank=True)
    footer_html = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        validate_template_syntax({"header_html": self.header_html, "footer_html": self.footer_html})

    _PREVIEW_PLACEHOLDER = (
        "<div style='padding:20px;font-family:sans-serif'>"
        "<p>Your email content will appear here.</p>"
        "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>"
        "</div>"
    )

    def preview_render(self, context: dict | None = None) -> str:
        ctx = context or {}
        header = _render_part(self.header_html, ctx)
        footer = _render_part(self.footer_html, ctx)
        return header + self._PREVIEW_PLACEHOLDER + footer


class EmailTemplate(models.Model):
    name = models.SlugField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255)
    html_body = models.TextField()
    text_body = models.TextField(blank=True)
    layout = models.ForeignKey(
        EmailLayout,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="templates",
    )
    sample_context = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        validate_template_syntax({"subject": self.subject, "html_body": self.html_body, "text_body": self.text_body})

    def render(self, context: dict | None = None) -> tuple[str, str, str]:
        """Returns (subject, html, text) with Django template syntax resolved."""
        ctx = {**self.sample_context, **(context or {})}

        subject = _render_part(self.subject, ctx)
        html = _render_part(self.html_body, ctx)
        text = _render_part(self.text_body, ctx) if self.text_body else ""

        if self.layout:
            header = _render_part(self.layout.header_html, ctx)
            footer = _render_part(self.layout.footer_html, ctx)
            html = header + html + footer

        return subject, html, text
