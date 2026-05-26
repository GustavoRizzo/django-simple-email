from django.template import Context, Template


def _render_part(source: str, context: dict) -> str:
    return Template(source).render(Context(context))


def render_template(template, context: dict | None = None) -> tuple[str, str, str]:
    """Renders an EmailTemplate and returns (subject, html, text)."""
    ctx = {**template.sample_context, **(context or {})}

    subject = _render_part(template.subject, ctx)
    html = _render_part(template.html_body, ctx)
    text = _render_part(template.text_body, ctx) if template.text_body else ""

    if template.layout:
        header = _render_part(template.layout.header_html, ctx)
        footer = _render_part(template.layout.footer_html, ctx)
        html = header + html + footer

    return subject, html, text
