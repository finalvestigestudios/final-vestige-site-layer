#!/usr/bin/env python3
"""Caching + gzip front for the local Playground, for front-end performance measurement ONLY.

Playground serves uncompressed responses with a 1-1.6 s PHP-WASM time-to-first-byte; the real site
serves cached, compressed pages. This proxy answers repeated GETs from memory (after one warm-up
fetch per URL) and gzips text responses, so Lighthouse measures the page's own delivery cost
(markup/CSS/JS size, render blocking, layout) instead of the stage's backend. Results through this
proxy must be reported as such, never as production or field numbers.

  python cache_proxy.py --upstream http://127.0.0.1:9400 --port 9401
"""
import argparse, gzip, http.server, socketserver, urllib.request

TEXT = ("text/", "application/javascript", "application/json", "image/svg+xml")
cache = {}


class H(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    upstream = ""

    def do_GET(self):
        key = self.path
        if key not in cache:
            try:
                r = urllib.request.urlopen(urllib.request.Request(self.upstream + self.path, headers={"Accept-Encoding": "identity"}), timeout=60)
                body, ctype, status = r.read(), r.headers.get("Content-Type", "application/octet-stream"), r.status
            except urllib.error.HTTPError as e:
                body, ctype, status = e.read(), e.headers.get("Content-Type", "text/plain"), e.code
            body = body.replace(self.upstream.encode(), b"")  # make absolute URLs host-relative
            gz = gzip.compress(body, 6) if ctype.startswith(TEXT) else None
            cache[key] = (status, ctype, body, gz)
        status, ctype, body, gz = cache[key]
        use_gz = gz is not None and "gzip" in self.headers.get("Accept-Encoding", "")
        data = gz if use_gz else body
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "public, max-age=3600")
        if use_gz:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Vary", "Accept-Encoding")
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--upstream", default="http://127.0.0.1:9400"); ap.add_argument("--port", type=int, default=9401)
    a = ap.parse_args(); H.upstream = a.upstream
    S(("127.0.0.1", a.port), H).serve_forever()
