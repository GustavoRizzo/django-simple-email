from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from django_simple_email.models import EmailLayout, EmailTemplate

LOCMEM = "django.core.mail.backends.locmem.EmailBackend"
PREVIEW_URL = "admin:django_simple_email_emailtemplate_preview"
SEND_TEST_URL = "admin:django_simple_email_emailtemplate_send_test"
LAYOUT_PREVIEW_URL = "admin:django_simple_email_emaillayout_preview"
LAYOUT_SEND_TEST_URL = "admin:django_simple_email_emaillayout_send_test"


class AdminTestCase(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser("admin", "admin@example.com", "password")
        self.client.login(username="admin", password="password")
        self.layout = EmailLayout.objects.create(
            name="test-layout",
            header_html="<HEADER>",
            footer_html="<FOOTER>",
        )
        self.template = EmailTemplate.objects.create(
            name="test",
            subject_default="Hello {{ name }}",
            html_body="<p>Hi {{ name }}</p>",
            layout=self.layout,
            sample_context={"name": "World"},
        )


class PreviewViewTests(AdminTestCase):
    def test_returns_200(self):
        url = reverse(PREVIEW_URL, args=[self.template.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_renders_layout_and_body(self):
        url = reverse(PREVIEW_URL, args=[self.template.pk])
        content = self.client.get(url).content.decode()
        self.assertIn("<HEADER>", content)
        self.assertIn("<p>Hi World</p>", content)
        self.assertIn("<FOOTER>", content)

    def test_variables_are_resolved_with_sample_context(self):
        url = reverse(PREVIEW_URL, args=[self.template.pk])
        content = self.client.get(url).content.decode()
        self.assertNotIn("{{ name }}", content)
        self.assertIn("World", content)

    def test_returns_404_for_missing_template(self):
        url = reverse(PREVIEW_URL, args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class SendTestViewTests(AdminTestCase):
    def setUp(self):
        super().setUp()
        mail.outbox = []

    @override_settings(EMAIL_BACKEND=LOCMEM)
    def test_sends_one_email(self):
        url = reverse(SEND_TEST_URL, args=[self.template.pk])
        self.client.get(url, HTTP_REFERER="/admin/")
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_BACKEND=LOCMEM, DJANGO_SIMPLE_EMAIL_TEST_RECIPIENT="custom@example.com")
    def test_uses_configured_test_recipient(self):
        url = reverse(SEND_TEST_URL, args=[self.template.pk])
        self.client.get(url, HTTP_REFERER="/admin/")
        self.assertEqual(mail.outbox[0].to, ["custom@example.com"])

    @override_settings(EMAIL_BACKEND=LOCMEM)
    def test_default_recipient_is_test_at_test_dot_com(self):
        url = reverse(SEND_TEST_URL, args=[self.template.pk])
        self.client.get(url, HTTP_REFERER="/admin/")
        self.assertEqual(mail.outbox[0].to, ["test@test.com"])

    @override_settings(EMAIL_BACKEND=LOCMEM)
    def test_redirects_back_to_referer(self):
        url = reverse(SEND_TEST_URL, args=[self.template.pk])
        response = self.client.get(url, HTTP_REFERER="/admin/django_simple_email/emailtemplate/")
        self.assertRedirects(response, "/admin/django_simple_email/emailtemplate/", fetch_redirect_response=False)

    def test_returns_404_for_missing_template(self):
        url = reverse(SEND_TEST_URL, args=[99999])
        response = self.client.get(url, HTTP_REFERER="/admin/")
        self.assertEqual(response.status_code, 404)


class LayoutPreviewViewTests(AdminTestCase):
    def test_returns_200(self):
        url = reverse(LAYOUT_PREVIEW_URL, args=[self.layout.pk])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_renders_header_and_footer(self):
        url = reverse(LAYOUT_PREVIEW_URL, args=[self.layout.pk])
        content = self.client.get(url).content.decode()
        self.assertIn("<HEADER>", content)
        self.assertIn("<FOOTER>", content)

    def test_renders_placeholder_body(self):
        url = reverse(LAYOUT_PREVIEW_URL, args=[self.layout.pk])
        content = self.client.get(url).content.decode()
        self.assertIn("Your email content will appear here.", content)

    def test_returns_404_for_missing_layout(self):
        url = reverse(LAYOUT_PREVIEW_URL, args=[99999])
        self.assertEqual(self.client.get(url).status_code, 404)


class LayoutSendTestViewTests(AdminTestCase):
    def setUp(self):
        super().setUp()
        mail.outbox = []

    @override_settings(EMAIL_BACKEND=LOCMEM)
    def test_sends_one_email(self):
        url = reverse(LAYOUT_SEND_TEST_URL, args=[self.layout.pk])
        self.client.get(url, HTTP_REFERER="/admin/")
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(EMAIL_BACKEND=LOCMEM, DJANGO_SIMPLE_EMAIL_TEST_RECIPIENT="custom@example.com")
    def test_uses_configured_test_recipient(self):
        url = reverse(LAYOUT_SEND_TEST_URL, args=[self.layout.pk])
        self.client.get(url, HTTP_REFERER="/admin/")
        self.assertEqual(mail.outbox[0].to, ["custom@example.com"])

    @override_settings(EMAIL_BACKEND=LOCMEM)
    def test_default_recipient_is_test_at_test_dot_com(self):
        url = reverse(LAYOUT_SEND_TEST_URL, args=[self.layout.pk])
        self.client.get(url, HTTP_REFERER="/admin/")
        self.assertEqual(mail.outbox[0].to, ["test@test.com"])

    @override_settings(EMAIL_BACKEND=LOCMEM)
    def test_subject_contains_layout_name(self):
        url = reverse(LAYOUT_SEND_TEST_URL, args=[self.layout.pk])
        self.client.get(url, HTTP_REFERER="/admin/")
        self.assertIn(self.layout.name, mail.outbox[0].subject)

    @override_settings(EMAIL_BACKEND=LOCMEM)
    def test_html_alternative_contains_header_and_footer(self):
        url = reverse(LAYOUT_SEND_TEST_URL, args=[self.layout.pk])
        self.client.get(url, HTTP_REFERER="/admin/")
        content, mimetype = mail.outbox[0].alternatives[0]
        self.assertEqual(mimetype, "text/html")
        self.assertIn("<HEADER>", content)
        self.assertIn("<FOOTER>", content)

    @override_settings(EMAIL_BACKEND=LOCMEM)
    def test_redirects_back_to_referer(self):
        url = reverse(LAYOUT_SEND_TEST_URL, args=[self.layout.pk])
        response = self.client.get(url, HTTP_REFERER="/admin/django_simple_email/emaillayout/")
        self.assertRedirects(response, "/admin/django_simple_email/emaillayout/", fetch_redirect_response=False)

    def test_returns_404_for_missing_layout(self):
        url = reverse(LAYOUT_SEND_TEST_URL, args=[99999])
        self.assertEqual(self.client.get(url, HTTP_REFERER="/admin/").status_code, 404)


class AdminPagesTests(AdminTestCase):
    def test_template_list_page_loads(self):
        url = reverse("admin:django_simple_email_emailtemplate_changelist")
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_template_change_page_loads(self):
        url = reverse("admin:django_simple_email_emailtemplate_change", args=[self.template.pk])
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_layout_list_page_loads(self):
        url = reverse("admin:django_simple_email_emaillayout_changelist")
        self.assertEqual(self.client.get(url).status_code, 200)

    def test_layout_change_page_loads(self):
        url = reverse("admin:django_simple_email_emaillayout_change", args=[self.layout.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
