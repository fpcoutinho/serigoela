from .base import Handler, HandlerError, Response
from .registry import get_handler_for, register


@register("view-source")
class ViewSourceHandler(Handler):
    """Wrapper handler for view-source: URLs.

    Delegates to the underlying handler and returns its raw source as
    `text/plain` so the CLI prints the source instead of rendering HTML.
    """

    def __init__(self, url: str):
        super().__init__(url)

    def fetch(self) -> Response:
        prefix = "view-source:"
        if not self.url.startswith(prefix):
            raise HandlerError("invalid view-source url")
        inner = self.url[len(prefix) :]
        try:
            underlying = get_handler_for(inner)
        except Exception as e:
            raise HandlerError(f"no underlying handler: {e}") from e

        resp = underlying.fetch()
        body = resp.body
        # ensure we return bytes so CLI can decode consistently
        if isinstance(body, str):
            body = body.encode("utf8")

        # force content-type to text/plain so CLI doesn't strip tags
        return Response(
            status=resp.status,
            headers=resp.headers,
            body=body,
            content_type="text/plain",
        )
