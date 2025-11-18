import sys
from pathlib import Path

from handlers.registry import get_handler_for
from handlers.renderers import strip_tags_and_unescape


def main(argv=None) -> int:
    argv = argv or sys.argv[1:]
    if argv:
        url = argv[0]
    else:
        # default to ./index.html if present
        p = Path("index.html")
        if p.exists():
            url = p.resolve().as_uri()
        else:
            print("usage: browser.py <url>")
            return 2

    try:
        handler = get_handler_for(url)
    except Exception as e:
        print(f"error: {e}")
        return 1

    try:
        resp = handler.fetch()
    except Exception as e:
        print(f"fetch error: {e}")
        return 1

    body = resp.body
    if isinstance(body, bytes):
        text = body.decode("utf8", errors="replace")
    else:
        text = str(body)

    # simple heuristic: if HTML, strip tags and unescape entities
    ctype = (resp.content_type or "").lower()
    if (
        ctype.startswith("text/html")
        or url.startswith("data:text/html")
        or url.endswith(".html")
    ):
        out = strip_tags_and_unescape(text)
    else:
        out = text

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
