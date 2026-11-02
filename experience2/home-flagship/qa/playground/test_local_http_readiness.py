#!/usr/bin/env python3
"""Real loopback HTTP regression controls for private WordPress CI readiness.

These tests neither install WordPress nor request external URLs. Their purpose
is to distinguish a live but broken local WordPress server from a closed port,
and prevent following redirects away from the isolated review server.
"""
import contextlib
import importlib.util
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from unittest import TestCase, main
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("fv_private_wp_ci", HERE / "ci_ex2_wp_playground.py")
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)


class Alive:
    def poll(self):
        return None


class Exited:
    def poll(self):
        return 1


@contextlib.contextmanager
def serve_local(status=200, body=b"ready", redirect=None):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(status)
            if redirect:
                self.send_header("Location", redirect)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if body:
                self.wfile.write(body)

        def log_message(self, *_args):
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        yield "http://127.0.0.1:%d/" % server.server_port
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=2)


class ReadinessTest(TestCase):
    def probe(self, status, body=b"ready", redirect=None):
        with serve_local(status, body, redirect) as url:
            with patch.object(ci, "BASE", url):
                # A failed readiness result must be fast and deterministic.
                with patch.object(ci.time, "sleep", lambda _: None):
                    return ci.ready(Alive(), seconds=0.08)

    def test_nonempty_http_200_is_ready(self):
        self.assertIsNone(self.probe(200))

    def test_http_503_is_classified_as_a_listening_but_failed_wordpress(self):
        with self.assertRaisesRegex(RuntimeError, r"probe_states=HTTP_503:[1-9]"):
            self.probe(503)

    def test_redirect_is_not_followed_and_is_reported(self):
        # If the no-redirect boundary regresses the destination is loopback,
        # not an external website or any production service.
        with self.assertRaisesRegex(RuntimeError, r"probe_states=UNEXPECTED_HTTP_REDIRECT:[1-9]"):
            self.probe(302, body=b"", redirect="http://127.0.0.1:1/never-follow")

    def test_same_origin_login_redirect_requires_real_login_page(self):
        class LoginHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(302)
                    self.send_header('Location', '/wp-login.php')
                    self.end_headers()
                elif self.path == '/wp-login.php':
                    body = b'<html><body id="wp-login">WordPress Login</body></html>'
                    self.send_response(200)
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_error(404)
            def log_message(self, *_args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), LoginHandler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(ci, 'BASE', 'http://127.0.0.1:%d/' % server.server_port):
                self.assertIsNone(ci.ready(Alive(), seconds=2))
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_external_redirect_still_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, 'UNEXPECTED_HTTP_REDIRECT'):
            self.probe(302, body=b'', redirect='https://finalvestige.com/wp-login.php')

    def test_empty_200_is_not_a_false_acceptance(self):
        with self.assertRaisesRegex(RuntimeError, r"probe_states=HTTP_200_EMPTY_OR_UNREADY:[1-9]"):
            self.probe(200, body=b"")

    def test_exited_process_fails_without_http_request(self):
        with self.assertRaisesRegex(RuntimeError, r"CLI exited before localhost readiness"):
            ci.ready(Exited(), seconds=1)


if __name__ == "__main__":
    main()
