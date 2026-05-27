from django.core.mail import EmailMultiAlternatives

from .models import EmailTemplate


def send_email(
    template_name: str,
    to: list[str],
    context: dict | None = None,
    from_email: str | None = None,
) -> int:
    """Sends an email using a stored EmailTemplate. Returns number of messages sent."""
    template = EmailTemplate.objects.get(name=template_name)
    subject, html, text = template.render(context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text or html,
        to=to,
        from_email=from_email,
    )
    if html:
        msg.attach_alternative(html, "text/html")
    return msg.send()
