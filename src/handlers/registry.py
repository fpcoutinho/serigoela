"""Simple registry mapping schemes to handler classes."""

from typing import Dict, Type

HANDLERS: Dict[str, Type] = {}


def register(scheme: str):
    scheme = scheme.lower()

    def _decorator(cls):
        HANDLERS[scheme] = cls
        return cls

    return _decorator


def get_handler_for(url: str, **kwargs):
    scheme = url.split(":", 1)[0].lower()
    cls = HANDLERS.get(scheme)
    if cls is None:
        raise ValueError(f"no handler registered for scheme '{scheme}'")
    return cls(url, **kwargs)
