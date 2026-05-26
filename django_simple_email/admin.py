from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from .models import EmailLayout, EmailTemplate
from .rendering import render_template
from .sending import send_email

_DEFAULT_TEST_RECIPIENT = "test@test.com"


@admin.register(EmailLayout)
class EmailLayoutAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "layout", "updated_at", "preview_link", "send_test_link"]
    list_select_related = ["layout"]
    search_fields = ["name", "description", "subject"]
    readonly_fields = ["preview_link", "send_test_link", "created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["name", "description", "layout", "sample_context"]}),
        ("Content", {"fields": ["subject", "html_body", "text_body"]}),
        ("Metadata", {"fields": ["preview_link", "send_test_link", "created_at", "updated_at"]}),
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:pk>/preview/",
                self.admin_site.admin_view(self._preview_view),
                name="django_simple_email_emailtemplate_preview",
            ),
            path(
                "<int:pk>/send-test/",
                self.admin_site.admin_view(self._send_test_view),
                name="django_simple_email_emailtemplate_send_test",
            ),
        ]
        return custom + urls

    def _preview_view(self, request, pk):
        template = get_object_or_404(EmailTemplate, pk=pk)
        _, html, _ = render_template(template)
        return HttpResponse(html)

    def _send_test_view(self, request, pk):
        template = get_object_or_404(EmailTemplate, pk=pk)
        recipient = getattr(settings, "DJANGO_SIMPLE_EMAIL_TEST_RECIPIENT", _DEFAULT_TEST_RECIPIENT)
        try:
            send_email(template.name, to=[recipient])
            self.message_user(request, f'Email "{template.name}" enviado para {recipient}.', messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Erro ao enviar: {e}", messages.ERROR)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", ".."))

    def preview_link(self, obj):
        if obj.pk:
            url = reverse("admin:django_simple_email_emailtemplate_preview", args=[obj.pk])
            return format_html('<a href="{}" target="_blank">Preview HTML</a>', url)
        return "-"

    preview_link.short_description = "Preview"

    def send_test_link(self, obj):
        if obj.pk:
            url = reverse("admin:django_simple_email_emailtemplate_send_test", args=[obj.pk])
            recipient = getattr(settings, "DJANGO_SIMPLE_EMAIL_TEST_RECIPIENT", _DEFAULT_TEST_RECIPIENT)
            return format_html(
                '<a href="{}" style="background:#417690;color:#fff;padding:5px 10px;'
                'border-radius:4px;text-decoration:none;font-size:12px;white-space:nowrap">'
                "Enviar para {}</a>",
                url,
                recipient,
            )
        return "-"

    send_test_link.short_description = "Teste"
