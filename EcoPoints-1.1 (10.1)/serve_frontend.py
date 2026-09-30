"""Serve this project's frontend from a fixed root for local development."""

from functools import partial
from hashlib import sha256
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class FrontendHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        super().end_headers()


if __name__ == "__main__":
    handler = partial(FrontendHandler, directory=str(ROOT))
    with ThreadingHTTPServer(("127.0.0.1", 5500), handler) as server:
        index_hash = sha256((ROOT / "index.html").read_bytes()).hexdigest()[:12]
        print(
            f"Serving {ROOT} at http://127.0.0.1:5500/index.html "
            f"(index sha256: {index_hash})",
            flush=True,
        )
        server.serve_forever()
