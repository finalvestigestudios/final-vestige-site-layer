"""Browser and static-server helpers for the Experience 2.0 tests.

A missing browser is an error, never a skip: tests that cannot run must not be reported as passing.
Set FVX_BROWSER_CHANNEL (msedge, chrome) or FVX_BROWSER_EXECUTABLE to choose a browser explicitly.
"""
from __future__ import annotations

import contextlib
import functools
import http.server
import os
import threading
from pathlib import Path

from playwright.sync_api import Browser, Playwright


class BrowserUnavailable(RuntimeError):
    pass


def launch(pw: Playwright) -> Browser:
    exe = os.environ.get("FVX_BROWSER_EXECUTABLE")
    channel = os.environ.get("FVX_BROWSER_CHANNEL")
    attempts = [{"executable_path": exe}] if exe else [{"channel": channel}] if channel else [
        {"channel": "msedge"}, {"channel": "chrome"}, {}]
    errors = []
    for kwargs in attempts:
        try:
            return pw.chromium.launch(headless=True, **kwargs)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{kwargs or 'bundled chromium'}: {str(exc).splitlines()[0]}")
    raise BrowserUnavailable("No Chromium-family browser could be launched:\n  " + "\n  ".join(errors))


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D401
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


@contextlib.contextmanager
def serve(directory: Path):
    """Serve `directory` on a free localhost port; yields the base URL."""
    handler = functools.partial(_Quiet, directory=str(directory))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()
        httpd.server_close()
