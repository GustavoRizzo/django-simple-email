from django.core.exceptions import ValidationError
from django.template import Template, TemplateSyntaxError


def validate_template_syntax(fields: dict[str, str]) -> None:
    errors = {}
    for field, value in fields.items():
        if value:
            try:
                Template(value)
            except TemplateSyntaxError as e:
                errors[field] = str(e)
    if errors:
        raise ValidationError(errors)
