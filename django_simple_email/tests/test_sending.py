from django.core import mail
from django.test import TestCase, override_settings

from django_simple_email.models import EmailTemplate
from django_simple_email.sending import send_template_mail

LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


def make_template(**kwargs) -> EmailTemplate:
    defaults = {
        "name": "test",
        "subject_default": "Hello {{ name }}",
        "html_body": "<p>Hi {{ name }}</p>",
        "text_body": "",
        "sample_context": {"name": "World"},
    }
    defaults.update(kwargs)
    return EmailTemplate.objects.create(**defaults)


@override_settings(EMAIL_BACKEND=LOCMEM)
class SendEmailTests(TestCase):
    def setUp(self):
        mail.outbox = []

    def test_sends_one_email(self):
        make_template()
        send_template_mail("test", recipient_list=["recipient@example.com"])
        self.assertEqual(len(mail.outbox), 1)

    def test_sends_to_correct_recipient(self):
        make_template()
        send_template_mail("test", recipient_list=["recipient@example.com"])
        self.assertEqual(mail.outbox[0].to, ["recipient@example.com"])

    def test_subject_is_rendered(self):
        make_template()
        send_template_mail("test", recipient_list=["r@example.com"])
        self.assertEqual(mail.outbox[0].subject, "Hello World")

    def test_context_overrides_sample_context(self):
        make_template()
        send_template_mail("test", recipient_list=["r@example.com"], context={"name": "Ana"})
        self.assertEqual(mail.outbox[0].subject, "Hello Ana")

    def test_subject_override_replaces_template_subject(self):
        make_template()
        send_template_mail("test", recipient_list=["r@example.com"], subject="Custom Subject")
        self.assertEqual(mail.outbox[0].subject, "Custom Subject")

    def test_html_alternative_is_attached(self):
        make_template()
        send_template_mail("test", recipient_list=["r@example.com"])
        alternatives = mail.outbox[0].alternatives
        self.assertEqual(len(alternatives), 1)
        content, mimetype = alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn("Hi World", content)

    def test_text_body_is_used_as_plain_fallback(self):
        make_template(text_body="Plain {{ name }}")
        send_template_mail("test", recipient_list=["r@example.com"])
        self.assertEqual(mail.outbox[0].body, "Plain World")

    def test_from_email_is_passed_through(self):
        make_template()
        send_template_mail("test", recipient_list=["r@example.com"], from_email="sender@example.com")
        self.assertEqual(mail.outbox[0].from_email, "sender@example.com")

    def test_raises_for_unknown_template(self):
        with self.assertRaises(EmailTemplate.DoesNotExist):
            send_template_mail("does-not-exist", recipient_list=["r@example.com"])

    def test_sends_to_multiple_recipients(self):
        make_template()
        send_template_mail("test", recipient_list=["a@example.com", "b@example.com"])
        self.assertEqual(mail.outbox[0].to, ["a@example.com", "b@example.com"])
