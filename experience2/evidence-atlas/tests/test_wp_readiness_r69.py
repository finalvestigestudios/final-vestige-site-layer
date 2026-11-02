"""Hostile, offline R69 readiness tests (no network and no WordPress writes)."""
from __future__ import annotations
from email.message import Message
import tempfile
import unittest
import urllib.error
from pathlib import Path
from urllib.parse import urlsplit

from wp_readiness_r69 import (
    ORIGIN, PATHS, ReadinessFailure, diagnose_private_cli_log,
    positive_wordpress_marker, safe_redirect_class, wait_for_wordpress,
)

class Response:
    def __init__(self, body, ctype='text/html', status=200):
        self._body = body
        self.status = status
        self.headers = Message()
        self.headers['Content-Type'] = ctype
    def read(self, limit): return self._body[:limit]
    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): self.close()

class Process:
    def __init__(self, result=None): self.result = result
    def poll(self): return self.result

class FakeOpener:
    def __init__(self, responses):
        self.responses = responses
        self.requests = []
    def open(self, req, timeout=0):
        u = req.full_url
        self.requests.append(u)
        assert urlsplit(u).netloc == '127.0.0.1:9438', 'unexpected outbound request'
        path = urlsplit(u).path
        target = self.responses[path]
        if callable(target): target = target()
        if isinstance(target, Exception): raise target
        return target

def redirect(location):
    headers = Message()
    headers['Location'] = location
    return urllib.error.HTTPError(ORIGIN+'/', 302, 'Moved', headers, None)

def fake_clock():
    ticks=[0]
    def now(): return ticks[0]
    def advance(seconds): ticks[0] += seconds
    return now, advance

class R69ReadinessContracts(unittest.TestCase):
    def test_redirect_destination_is_only_classified_never_followed(self):
        self.assertEqual(safe_redirect_class('/?pagename=fv-apollo-review-private'),
                         'REDIRECT_PRIVATE_LANDING')
        self.assertEqual(safe_redirect_class('/wp-login.php?redirect_to=anything'),
                         'REDIRECT_WP_LOGIN')
        for v in ('https://example.com/', 'http://localhost:9438/',
                  'http://127.0.0.1:9439/', 'http://127.0.0.1@evil.test/',
                  '//evil.test/', 'javascript:alert(1)', '', 'x'*513):
            self.assertIn(safe_redirect_class(v),
                          ('REDIRECT_NONLOCAL_BLOCKED','REDIRECT_INVALID'))
    def test_refuse_generic_200_and_unrelated_json(self):
        self.assertFalse(positive_wordpress_marker('/', 'text/html', b'Hello world'))
        self.assertFalse(positive_wordpress_marker('/wp-json/', 'application/json',
                         b'{"namespaces":["not-wp"],"routes":{}}'))
        self.assertFalse(positive_wordpress_marker('/wp-login.php', 'text/html',
                         b'<html>fake login</html>'))
        self.assertTrue(positive_wordpress_marker(
            '/wp-json/', 'application/json',
            b'{"namespaces":["wp/v2"],"routes":{"/wp/v2/posts":{}}}'))
    def test_cookie_redirect_on_root_but_real_wp_login_succeeds(self):
        opener = FakeOpener({
            '/': redirect('/?pagename=fv-apollo-review-private'),
            '/wp-json/': redirect('/wp-login.php'),
            '/wp-login.php': Response(b'<html class="wp-login"><form id="loginform">'),
            '/wp-admin/': Response(b'not needed'),
        })
        endpoint, states = wait_for_wordpress(Process(),seconds=3,opener=opener)
        self.assertEqual(endpoint, 'LOGIN')
        self.assertEqual(states['ROOT_REDIRECT_PRIVATE_LANDING'],1)
        self.assertIn('REST_REDIRECT_WP_LOGIN',states)
        self.assertEqual(len(opener.requests),3)
        self.assertEqual(set(opener.requests),{ORIGIN+x for x in PATHS[:3]})
    def test_unauthorized_redirect_blocked_with_no_followup_to_location(self):
        opener = FakeOpener({
            '/': redirect('https://evil.test/secret?token=private'),
            '/wp-json/': Response(b'no',status=200),
            '/wp-login.php': Response(b'no',status=200),
            '/wp-admin/': Response(b'no',status=200),
        })
        now,sleep=fake_clock()
        with self.assertRaises(ReadinessFailure) as capture:
            wait_for_wordpress(Process(),seconds=2,clock=now,sleep=sleep,opener=opener)
        self.assertEqual(capture.exception.reason,'WORDPRESS_LOCAL_READINESS_TIMEOUT')
        self.assertIn('ROOT_REDIRECT_NONLOCAL_BLOCKED',capture.exception.states)
        self.assertTrue(all(u.startswith(ORIGIN+'/') for u in opener.requests))
        self.assertNotIn('evil.test',repr(capture.exception.states))
    def test_exited_cli_fails_fast_without_network_or_raw_output(self):
        opener=FakeOpener({})
        with self.assertRaises(ReadinessFailure) as ctx:
            wait_for_wordpress(Process(result=2),seconds=2,opener=opener)
        self.assertEqual(ctx.exception.reason,'PLAYGROUND_EXITED')
        self.assertEqual(opener.requests,[])
    def test_private_cli_classifier_never_reveals_secret(self):
        with tempfile.TemporaryDirectory() as t:
            log=Path(t)/'raw-private.log'
            log.write_text('password=SECRET999 secret-url=https://nonlocal.test/x\n'
                           'Error: Could not activate plugin; opaque_session=abc')
            self.assertEqual(diagnose_private_cli_log(log),
                             'WP_BLUEPRINT_ACTIVATION_FAILURE')
            self.assertNotIn('SECRET999',diagnose_private_cli_log(log))
            self.assertEqual(diagnose_private_cli_log(Path(t)/'absent'),
                             'CLI_LOG_UNAVAILABLE')
    def test_invalid_budget_fail_closed(self):
        with self.assertRaisesRegex(ValueError,'INVALID_READINESS_BUDGET'):
            wait_for_wordpress(Process(),seconds=900,opener=FakeOpener({}))

if __name__=='__main__': unittest.main()
