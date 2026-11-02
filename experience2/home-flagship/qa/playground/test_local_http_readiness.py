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
        with self.assertRaisesRegex(RuntimeError, r"probe_states=REDIRECT_PORT_MISMATCH:[1-9]"):
            self.probe(302, body=b"", redirect="http://127.0.0.1:1/never-follow")

    def test_private_preview_redirect_uses_fixed_local_login_probe(self):
        class LoginHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(302)
                    self.send_header('Location', '/?pagename=fv-ex2-playground-review')
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

    def test_blueprint_landing_redirect_with_live_rest_is_ready(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(302)
                    self.send_header('Location', '/?pagename=fv-ex2-playground-review')
                    self.end_headers()
                elif self.path == '/wp-json/':
                    body = b'{"namespaces":["wp/v2"],"routes":{"/":{}}}'
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=UTF-8')
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(302)
                    self.send_header('Location', '/wp-admin/')
                    self.end_headers()
            def log_message(self, *_args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(ci, 'BASE', 'http://127.0.0.1:%d/' % server.server_port):
                self.assertIsNone(ci.ready(Alive(), seconds=2))
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_external_redirect_is_not_laundered_by_valid_local_rest(self):
        requests = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append(self.path)
                if self.path == '/':
                    self.send_response(302)
                    self.send_header('Location', 'https://finalvestige.com/')
                    self.end_headers()
                else:
                    body = b'{"namespaces":["wp/v2"],"routes":{"/":{}}}'
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(body)
            def log_message(self, *_args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(ci, 'BASE', 'http://127.0.0.1:%d/' % server.server_port):
                with patch.object(ci.time, 'sleep', lambda _: None):
                    with self.assertRaisesRegex(RuntimeError, 'REDIRECT_SCHEME_OTHER'):
                        ci.ready(Alive(), seconds=0.08)
            self.assertEqual(set(requests), {'/'})
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_local_session_cookie_handshake_recovers_302_to_200(self):
        seen = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                seen.append(self.headers.get('Cookie', ''))
                if 'fv_ready=1' not in seen[-1]:
                    self.send_response(302)
                    self.send_header('Location', '/')
                    self.send_header('Set-Cookie', 'fv_ready=1; Path=/; HttpOnly; SameSite=Lax')
                    self.end_headers()
                else:
                    body = b'<html><body>isolated WordPress ready</body></html>'
                    self.send_response(200)
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
            def log_message(self, *_args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(ci, 'BASE', 'http://127.0.0.1:%d/' % server.server_port):
                self.assertIsNone(ci.ready(Alive(), seconds=2))
            self.assertGreaterEqual(len(seen), 2)
            self.assertTrue(any('fv_ready=1' in request for request in seen[1:]))
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_external_redirect_with_cookie_still_fails_closed(self):
        requests = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                requests.append(self.path)
                self.send_response(302)
                self.send_header('Location', 'https://finalvestige.com/')
                self.send_header('Set-Cookie', 'fv_ready=1; Path=/; HttpOnly')
                self.end_headers()
            def log_message(self, *_args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(ci, 'BASE', 'http://127.0.0.1:%d/' % server.server_port):
                with patch.object(ci.time, 'sleep', lambda _: None):
                    with self.assertRaisesRegex(RuntimeError, 'REDIRECT_SCHEME_OTHER'):
                        ci.ready(Alive(), seconds=0.08)
            self.assertEqual(set(requests), {'/'})
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_wordpress_install_redirect_is_classified_without_url_disclosure(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header('Location', '/wp-admin/install.php')
                self.end_headers()
            def log_message(self, *_args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(ci, 'BASE', 'http://127.0.0.1:%d/' % server.server_port):
                with patch.object(ci.time, 'sleep', lambda _: None):
                    with self.assertRaisesRegex(RuntimeError,
                                                'REST_REDIRECT_WP_INSTALL_NOT_FINISHED') as failure:
                        ci.ready(Alive(), seconds=0.08)
            self.assertIn('LOGIN_REDIRECT_WP_INSTALL_NOT_FINISHED', str(failure.exception))
            self.assertIn('ADMIN_REDIRECT_WP_INSTALL_NOT_FINISHED', str(failure.exception))
            self.assertNotIn('/wp-admin/install.php', str(failure.exception))
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_all_endpoints_private_landing_redirect_is_not_ready(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header('Location', '/?pagename=fv-ex2-playground-review')
                self.end_headers()
            def log_message(self, *_args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(ci, 'BASE', 'http://127.0.0.1:%d/' % server.server_port):
                with patch.object(ci.time, 'sleep', lambda _: None):
                    with self.assertRaisesRegex(RuntimeError,
                                                'REDIRECT_BLUEPRINT_PRIVATE_LANDING') as failure:
                        ci.ready(Alive(), seconds=0.08)
            self.assertIn('REST_REDIRECT_BLUEPRINT_PRIVATE_LANDING', str(failure.exception))
            self.assertNotIn('?pagename=', str(failure.exception))
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_fake_rest_schema_cannot_admit_redirect(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(302)
                    self.send_header('Location', '/?pagename=review')
                    self.end_headers()
                elif self.path == '/wp-json/':
                    body = b'{"status":"ok"}'
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(body)
                else:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'<html>generic landing page</html>')
            def log_message(self, *_args): pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            with patch.object(ci, 'BASE', 'http://127.0.0.1:%d/' % server.server_port):
                with patch.object(ci.time, 'sleep', lambda _: None):
                    with self.assertRaisesRegex(RuntimeError, 'REST_NO_WORDPRESS_SCHEMA'):
                        ci.ready(Alive(), seconds=0.08)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)

    def test_external_redirect_still_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, 'REDIRECT_SCHEME_OTHER'):
            self.probe(302, body=b'', redirect='https://finalvestige.com/wp-login.php')

    def test_unexpected_path_is_sanitized_class_only(self):
        with self.assertRaisesRegex(RuntimeError, 'REDIRECT_PATH_NOT_ALLOWLISTED'):
            self.probe(302, body=b'', redirect='/private-secret?token=hidden')

    def test_missing_location_is_classified(self):
        with self.assertRaisesRegex(RuntimeError, 'REDIRECT_LOCATION_MISSING'):
            self.probe(302, body=b'')

    def test_empty_200_is_not_a_false_acceptance(self):
        with self.assertRaisesRegex(RuntimeError, r"probe_states=HTTP_200_EMPTY_OR_UNREADY:[1-9]"):
            self.probe(200, body=b"")

    def test_exited_process_fails_without_http_request(self):
        with self.assertRaisesRegex(RuntimeError, r"CLI exited before localhost readiness"):
            ci.ready(Exited(), seconds=1)


if __name__ == "__main__":
    main()
