import tkinter

from handlers.registry import get_handler_for
from handlers.renderers import strip_tags_and_unescape

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100


def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Down>", self.scrolldown)

    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c)

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

        self.display_list = layout(out)
        self.draw()

    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()

    def scrollup(self, e):
        self.scroll -= SCROLL_STEP
        if self.scroll < 0:
            self.scroll = 0
        self.draw()


if __name__ == "__main__":
    import sys

    Browser().load(sys.argv[1])
    tkinter.mainloop()
