from dataclasses import dataclass
from typing import Dict, Optional


class HandlerError(Exception):
    pass


@dataclass
class Response:
    status: int = 200
    headers: Dict[str, str] = None
    body: bytes | str = b""
    content_type: Optional[str] = None


class Handler:
    """Base handler interface.

    Subclasses should implement `fetch()` and may override `render()`.
    """

    def __init__(self, url: str):
        self.url = url
        self.scheme = url.split(":", 1)[0].lower()

    def fetch(self) -> Response:
        raise NotImplementedError()

    def render(self, response: Response) -> None:
        """Default rendering: print text/html as plain text (caller may decode)."""
        body = response.body
        if isinstance(body, bytes):
            try:
                body = body.decode("utf8", errors="replace")
            except Exception:
                body = str(body)
        print(body)
