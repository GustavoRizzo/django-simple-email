from django.core.mail import EmailMultiAlternatives

from .models import EmailTemplate


def send_template_mail(
    template_name: str,
    recipient_list: list[str],
    context: dict | None = None,
    subject: str | None = None,
    from_email: str | None = None,
) -> int:
    """Sends an email using a stored EmailTemplate. Returns number of messages sent."""
    template = EmailTemplate.objects.get(name=template_name)
    default_subject, html, text = template.render(context)

    msg = EmailMultiAlternatives(
        subject=subject if subject is not None else default_subject,
        body=text or html,
        to=recipient_list,
        from_email=from_email,
    )
    if html:
        msg.attach_alternative(html, "text/html")
    return msg.send()
