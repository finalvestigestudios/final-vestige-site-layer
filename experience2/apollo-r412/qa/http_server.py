#!/usr/bin/env python3
"""An exact-source, loopback-only HTTP acceptance fixture. NOT WordPress staging.

Only the signed R411 PHP, fixture and CSS are used. No external network, writes,
marketing/analytics scripts or third-party resources are served. A real navigated
Chromium document enables meaningful HTTP response, CSP, asset and paint checks.
"""
from __future__ import annotations
import hashlib
import subprocess
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
R411 = ROOT / 'apollo-r411'
GIT_SHAS = {
    'staging-source-drawer.php': 'efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1',
    'qa/render_fixture.php': 'bbcea951ad755e62959aa86d48b735c620053162',
    'assets/source-drawer.css': '2ed53b254dd9cfd4b27e56a2ace2c68bf05a8118',
}

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def verified_source() -> tuple[bytes, bytes]:
    for path, sha in GIT_SHAS.items():
        data = (R411 / path).read_bytes()
        actual = git_blob(data)
        if actual != sha:
            raise RuntimeError(f'R411_DEPENDENCY_HASH_MISMATCH {path}: {actual} != {sha}')
    php = subprocess.run(['php', str(R411 / 'qa/render_fixture.php')], check=True,
                         capture_output=True, timeout=10)
    html = php.stdout
    if not html.startswith(b'<!doctype html>') or b'data-fv-r411-sources' not in html:
        raise RuntimeError('R411_PHP_RENDER_INVALID')
    # Source is genuine CLI PHP output. Insert only a same-origin stylesheet link;
    # no HTML evidence record, NASA link or historical statement is modified.
    html = html.replace(b'</head>', b'<link rel="stylesheet" href="/assets/source-drawer.css"></head>', 1)
    return html, (R411 / 'assets/source-drawer.css').read_bytes()

class FixtureHandler(BaseHTTPRequestHandler):
    html: bytes = b''
    css: bytes = b''
    def do_GET(self):
        uri = urlsplit(self.path)
        if uri.path == '/apollo-r411/':
            data, mime, code = self.html, 'text/html; charset=utf-8', 200
        elif uri.path == '/assets/source-drawer.css':
            data, mime, code = self.css, 'text/css; charset=utf-8', 200
        elif uri.path == '/healthz':
            data, mime, code = b'R412_LOOPBACK_ONLY\n', 'text/plain; charset=utf-8', 200
        else:
            data, mime, code = b'Not Found\n', 'text/plain; charset=utf-8', 404
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'self'; img-src 'none'; connect-src 'none'; script-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(data)
    def log_message(self, fmt, *args):
        pass

class LocalFixture:
    def __init__(self):
        html,css = verified_source()
        cls = type('R412Handler',(FixtureHandler,),{'html':html,'css':css})
        self.server = ThreadingHTTPServer(('127.0.0.1',0),cls)
        self.thread = Thread(target=self.server.serve_forever,daemon=True)
    @property
    def base_url(self):
        return f'http://127.0.0.1:{self.server.server_address[1]}'
    def __enter__(self):
        self.thread.start()
        return self
    def __exit__(self,*args):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=5)
