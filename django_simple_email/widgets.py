from django import forms


class CodeTextarea(forms.Textarea):
    """Textarea styled for editing code: monospace font, no spellcheck, no word wrap."""

    def __init__(self, *args, **kwargs):
        attrs = kwargs.pop("attrs", {})
        attrs.setdefault("rows", 20)
        attrs.setdefault("spellcheck", "false")
        attrs.setdefault("wrap", "off")
        attrs.setdefault(
            "style",
            "font-family: 'Courier New', Courier, monospace;"
            " font-size: 13px;"
            " line-height: 1.6;"
            " resize: vertical;",
        )
        super().__init__(*args, attrs=attrs, **kwargs)
