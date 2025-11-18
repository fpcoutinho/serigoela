import socket
import ssl
from typing import Dict

from .base import Handler, HandlerError, Response
from .registry import register


@register("http")
class HTTPHandler(Handler):
    """Simple HTTP/HTTPS handler using sockets.

    Supports Content-Length and chunked transfer decoding.
    """

    def __init__(self, url: str):
        super().__init__(url)
        # parse minimal URL: scheme://host[:port]/path
        rest = url.split("://", 1)[1]
        if "/" in rest:
            hostport, path = rest.split("/", 1)
            self.path = "/" + path
        else:
            hostport = rest
            self.path = "/"
        if ":" in hostport:
            host, port = hostport.split(":", 1)
            self.host = host
            try:
                self.port = int(port)
            except ValueError:
                raise HandlerError("invalid port")
        else:
            self.host = hostport
            self.port = 80
        self.scheme = url.split(":", 1)[0].lower()
        if self.scheme == "https" and self.port == 80:
            self.port = 443
        self.headers = {
            "Host": self.host,
            "Connection": "close",
            "User-Agent": "Serigoela",
        }

    def fetch(self) -> Response:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10.0)
            s.connect((self.host, self.port))
            if self.scheme == "https":
                ctx = ssl.create_default_context()
                s = ctx.wrap_socket(s, server_hostname=self.host)

            rfile = s.makefile("rb")

            # build and send request
            req = f"GET {self.path} HTTP/1.1\r\n"
            for k, v in self.headers.items():
                req += f"{k}: {v}\r\n"
            req += "\r\n"
            s.send(req.encode("utf8"))

            # status line
            statusline = rfile.readline().decode("iso-8859-1")
            if not statusline:
                raise HandlerError("no response from server")
            parts = statusline.split(" ", 2)
            if len(parts) < 2:
                raise HandlerError(f"malformed status line: {statusline.strip()}")
            status = int(parts[1])

            # headers
            headers: Dict[str, str] = {}
            while True:
                line = rfile.readline().decode("iso-8859-1")
                if line in ("\r\n", "\n", ""):
                    break
                if ":" not in line:
                    continue
                name, value = line.split(":", 1)
                headers[name.strip().lower()] = value.strip()

            # body
            te = headers.get("transfer-encoding")
            if te and "chunked" in te.lower():
                body = self._read_chunked(rfile)
            elif "content-length" in headers:
                length = int(headers["content-length"])
                body = rfile.read(length)
            else:
                # read until socket close
                body = rfile.read()

            content_type = headers.get("content-type")
            rfile.close()
            s.close()
            return Response(
                status=status, headers=headers, body=body, content_type=content_type
            )
        except HandlerError:
            raise
        except Exception as e:
            raise HandlerError(str(e)) from e

    def _read_chunked(self, rfile):
        parts = []
        while True:
            line = rfile.readline().decode("iso-8859-1")
            if not line:
                raise HandlerError("chunked encoding truncated")
            chunk_size_str = line.strip().split(";", 1)[0]
            try:
                size = int(chunk_size_str, 16)
            except ValueError:
                raise HandlerError(f"invalid chunk size: {chunk_size_str}")
            if size == 0:
                # consume trailer headers until blank line
                while True:
                    l = rfile.readline().decode("iso-8859-1")
                    if l in ("\r\n", "\n", ""):
                        break
                break
            data = rfile.read(size)
            parts.append(data)
            # consume CRLF
            _ = rfile.read(2)
        return b"".join(parts)


# also register for https using same class
register("https")(HTTPHandler)
