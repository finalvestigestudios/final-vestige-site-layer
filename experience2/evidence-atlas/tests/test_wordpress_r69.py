"""R69 deterministic regressions for authentic WordPress loopback startup.

No sockets are opened here; factory injection models complete REST indices,
incorrect 8-KiB prefix assumptions, alternate route, and refusals.
"""
import json
import unittest
from wordpress_r68 import probe_local_rest

class Response:
    def __init__(self, status, body, location=None):
        self.status, self.body, self.location = status, body, location
    def getheader(self, name):
        return self.location if name.lower() == 'location' else None
    def read(self, limit):
        return self.body[:limit]

class Factory:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.paths = []
        self.closed = 0
    def __call__(self):
        parent = self
        response = next(self.responses)
        class Connection:
            def request(self, method, path, headers=None):
                assert method == 'GET'
                assert path in ('/wp-json/', '/?rest_route=%2F')
                assert headers.get('Accept') == 'application/json'
                parent.paths.append(path)
            def getresponse(self):
                if isinstance(response, Exception):
                    raise response
                return response
            def close(self):
                parent.closed += 1
        return Connection()

class R69RestProbe(unittest.TestCase):
    def test_complete_large_index_with_routes_after_first_8192_bytes(self):
        body = json.dumps({'namespaces':['wp/v2'], 'filler':'x'*9000,
                           'routes':{'/':{}}}).encode()
        self.assertNotIn(b'"routes"', body[:8192])
        factory = Factory([Response(200, body)])
        self.assertEqual(probe_local_rest(factory),
                         (True, 'REST_INDEX_VERIFIED'))
        self.assertEqual(factory.paths, ['/wp-json/'])
        self.assertEqual(factory.closed, 1)

    def test_wordpress_plain_permalink_rest_route_fallback(self):
        body = json.dumps({'namespaces':[], 'routes':{}}).encode()
        factory = Factory([Response(404, b'not found'), Response(200, body)])
        self.assertEqual(probe_local_rest(factory),
                         (True, 'REST_INDEX_VERIFIED'))
        self.assertEqual(factory.paths,
                         ['/wp-json/', '/?rest_route=%2F'])
        self.assertEqual(factory.closed, 2)

    def test_malformed_rest_index_fail_closed(self):
        factory = Factory([Response(200, b'<html>login</html>'),
                           Response(200, b'{"namespaces":[]}')])
        ok, code = probe_local_rest(factory)
        self.assertFalse(ok)
        self.assertEqual(code, 'REST_NOT_JSON/REST_INDEX_WRONG_SHAPE')
        self.assertEqual(factory.closed, 2)

    def test_remote_redirect_never_followed(self):
        # Direct http.client does not follow Location headers.
        factory = Factory([Response(302,b'',location='https://example.com/secret'),
                           Response(302,b'',location='http://127.0.0.1:9999/')])
        self.assertEqual(probe_local_rest(factory),
                         (False, 'NONLOCAL_REDIRECT_REFUSED/NONLOCAL_REDIRECT_REFUSED'))
        self.assertEqual(factory.closed, 2)

    def test_loopback_redirect_proves_port_only_not_wordpress(self):
        # A redirect does not prove REST, WordPress, plugins, or a11y: those
        # stronger claims are verified by the subsequent real browser gate.
        factory = Factory([
            Response(302,b'',location='http://127.0.0.1:9438/wp-login.php'),
            Response(302,b'',location='/?pagename=fv-apollo-review-private')
        ])
        self.assertEqual(probe_local_rest(factory),
            (True,'LOOPBACK_HTTP_RESPONSIVE_REST_NOT_VERIFIED'))
        self.assertEqual(factory.closed,2)

    def test_oversize_index_fails_closed(self):
        factory = Factory([Response(200, b' ' * 2_000_001),
                           Response(200, b' ' * 2_000_001)])
        self.assertEqual(probe_local_rest(factory),
                         (False, 'REST_INDEX_TOO_LARGE/REST_INDEX_TOO_LARGE'))

    def test_unavailable_port_has_no_secret_response_body(self):
        factory = Factory([ConnectionRefusedError('private localhost socket'),
                           TimeoutError('private localhost socket')])
        ok, code = probe_local_rest(factory)
        self.assertFalse(ok)
        self.assertEqual(code,'PORT_UNAVAILABLE/PORT_UNAVAILABLE')
        self.assertNotIn('private',code)
        self.assertEqual(factory.closed, 2)

if __name__ == '__main__':
    unittest.main()
