from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoSimpleEmail(AppConfig):
    name = 'django_simple_email'

    verbose_name = _('Django Simple Email')
