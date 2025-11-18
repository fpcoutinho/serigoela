import html


def unescape_entities(text: str) -> str:
    """Unescape HTML/XML character references and named entities."""
    return html.unescape(text)


def strip_tags_and_unescape(html_text: str) -> str:
    """Very small renderer: strip tags and unescape entities.

    Not a full HTML renderer — sufficient for simple demo pages.
    """
    out = []
    in_tag = False
    i = 0
    L = len(html_text)
    while i < L:
        c = html_text[i]
        if c == "<":
            in_tag = True
            i += 1
            continue
        if c == ">":
            in_tag = False
            i += 1
            continue
        if in_tag:
            i += 1
            continue
        # handle entities simply by collecting until ';' and unescaping via html.unescape
        if c == "&":
            sem = html_text.find(";", i + 1)
            if sem != -1:
                ent = html_text[i : sem + 1]
                out.append(html.unescape(ent))
                i = sem + 1
                continue
            else:
                out.append(c)
                i += 1
                continue
        out.append(c)
        i += 1
    return "".join(out)
