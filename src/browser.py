import tkinter

from handlers.registry import get_handler_for
from handlers.renderers import strip_tags_and_unescape

WIDTH, HEIGHT = 800, 600


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()

    def load(self, url):
        handler = get_handler_for(url)
        resp = handler.fetch()

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

        HSTEP, VSTEP = 13, 18
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in out:
            self.canvas.create_text(cursor_x, cursor_y, text=c)
            cursor_x += HSTEP
            if cursor_x >= WIDTH - HSTEP:
                cursor_y += VSTEP
                cursor_x = HSTEP


if __name__ == "__main__":
    import sys

    Browser().load(sys.argv[1])
    tkinter.mainloop()
