from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html

from .models import EmailLayout, EmailTemplate
from .rendering import render_template


@admin.register(EmailLayout)
class EmailLayoutAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "layout", "updated_at", "preview_link"]
    list_select_related = ["layout"]
    search_fields = ["name", "description", "subject"]
    readonly_fields = ["preview_link", "created_at", "updated_at"]
    fieldsets = [
        (None, {"fields": ["name", "description", "layout", "sample_context"]}),
        ("Content", {"fields": ["subject", "html_body", "text_body"]}),
        ("Metadata", {"fields": ["preview_link", "created_at", "updated_at"]}),
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:pk>/preview/",
                self.admin_site.admin_view(self._preview_view),
                name="django_simple_email_emailtemplate_preview",
            ),
        ]
        return custom + urls

    def _preview_view(self, request, pk):
        template = get_object_or_404(EmailTemplate, pk=pk)
        _, html, _ = render_template(template)
        return HttpResponse(html)

    def preview_link(self, obj):
        if obj.pk:
            url = reverse("admin:django_simple_email_emailtemplate_preview", args=[obj.pk])
            return format_html('<a href="{}" target="_blank">Preview HTML</a>', url)
        return "-"

    preview_link.short_description = "Preview"
