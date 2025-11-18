import base64
import urllib.parse

from .base import Handler, HandlerError, Response
from .registry import register


@register("data")
class DataHandler(Handler):
    """Handler for RFC2397 data URLs: data:[<mediatype>][;base64],<data>

    This implementation supports optional `;base64` and simple media types.
    """

    def fetch(self) -> Response:
        assert self.url.startswith("data:")
        payload = self.url[len("data:") :]
        try:
            meta, data = payload.split(",", 1)
        except ValueError:
            raise HandlerError("malformed data URL")

        is_base64 = False
        content_type = None
        if ";base64" in meta:
            is_base64 = True
            content_type = meta.replace(";base64", "") or None
        elif meta:
            content_type = meta

        if is_base64:
            try:
                raw = base64.b64decode(data)
            except Exception as e:
                raise HandlerError(f"base64 decode error: {e}") from e
        else:
            # percent-decoded
            raw = urllib.parse.unquote_to_bytes(data)

        return Response(status=200, headers={}, body=raw, content_type=content_type)
