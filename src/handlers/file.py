import mimetypes
import os
import urllib.parse

from .base import Handler, HandlerError, Response
from .registry import register


@register("file")
class FileHandler(Handler):
    """Handler for file:// URLs.

    Simple and permissive: converts the file URL to a local path and reads it.
    """

    def __init__(self, url: str):
        super().__init__(url)

    def fetch(self) -> Response:
        # strip scheme
        path = self.url[len("file://") :]
        # On Windows a path may start with /C:/...
        if (
            os.name == "nt"
            and path.startswith("/")
            and len(path) > 2
            and path[1].isalpha()
            and path[2] == ":"
        ):
            path = path[1:]
        path = urllib.parse.unquote(path)
        if not path:
            raise HandlerError("empty file path")
        try:
            # read in binary and let renderer decide decoding
            with open(path, "rb") as f:
                data = f.read()
        except FileNotFoundError as e:
            raise HandlerError(f"file not found: {path}") from e
        except OSError as e:
            raise HandlerError(f"error reading file: {e}") from e

        ctype, _ = mimetypes.guess_type(path)
        return Response(status=200, headers={}, body=data, content_type=ctype)
