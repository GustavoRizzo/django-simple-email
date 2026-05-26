def send_email(*args, **kwargs) -> int:
    from .sending import send_email as _send_email

    return _send_email(*args, **kwargs)


__all__ = ["send_email"]
