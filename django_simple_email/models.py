from django.db import models


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
