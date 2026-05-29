def send_template_mail(*args, **kwargs) -> int:
    from .sending import send_template_mail as _send_template_mail

    return _send_template_mail(*args, **kwargs)


__all__ = ["send_template_mail"]
