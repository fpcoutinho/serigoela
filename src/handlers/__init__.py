"""Handlers package for serigoela-browser.
This package contains scheme-specific handlers and a small registry.

Importing this package will import built-in handlers so they register
themselves with the registry.
"""

# import submodules to ensure registration decorators run at import time
from . import (
    base,  # noqa: F401
    data,  # noqa: F401
    file,  # noqa: F401
    http,  # noqa: F401
    registry,  # noqa: F401
    renderers,  # noqa: F401
    view_source,  # noqa: F401
)

__all__ = ["base", "registry", "file", "data", "http", "view_source", "renderers"]
