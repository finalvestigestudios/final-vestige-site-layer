"""R69 fixed-origin WordPress readiness with zero off-loopback redirects.

A private Playground redirect/cookie handshake is *not* a failed WordPress
startup. Only explicitly named local WordPress markers count as readiness;
Playwright still must verify the real shortcodes, source custody and axe.
Never return raw HTML, URL locations, cookies or CLI output in CI artifacts.
"""
from __future__ import annotations

from collections import Counter
from http.cookiejar import CookieJar
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ORIGIN = 'http://127.0.0.1:9438'
PATHS = ('/', '/wp-json/', '/wp-login.php', '/wp-admin/')
LIMIT = 131072
MAX_STATES = 24

class ReadinessFailure(RuntimeError):
    def __init__(self, reason: str, states: dict[str, int]):
        if reason not in ('PLAYGROUND_EXITED', 'WORDPRESS_LOCAL_READINESS_TIMEOUT'):
            reason = 'READINESS_FAILURE'
        self.reason = reason
        self.states = dict(sorted(states.items())[:MAX_STATES])
        super().__init__(reason)

class NeverRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        return None

def safe_redirect_class(location: str) -> str:
    """Classify only; never visit a Location header or reproduce its content."""
    if not location or len(location) > 512:
        return 'REDIRECT_INVALID'
    try:
        dest = urllib.parse.urlsplit(urllib.parse.urljoin(ORIGIN + '/', location))
        if (dest.scheme != 'http' or dest.hostname != '127.0.0.1'
                or dest.port != 9438 or dest.username or dest.password):
            return 'REDIRECT_NONLOCAL_BLOCKED'
        if dest.path == '/wp-login.php':
            return 'REDIRECT_WP_LOGIN'
        if dest.path == '/wp-admin/':
            return 'REDIRECT_WP_ADMIN'
        if dest.path == '/wp-admin/install.php':
            return 'REDIRECT_WP_INSTALL'
        if dest.path == '/' and dest.query == 'pagename=fv-apollo-review-private':
            return 'REDIRECT_PRIVATE_LANDING'
        return 'REDIRECT_OTHER_LOCAL'
    except (ValueError, TypeError):
        return 'REDIRECT_INVALID'

def positive_wordpress_marker(path: str, content_type: str, body: bytes) -> bool:
    """A generic 200/JSON is not enough: verify a real WordPress signature."""
    low = body.lower()
    if path == '/wp-json/':
        return ('application/json' in content_type.lower()
                and b'"routes"' in low and b'"namespaces"' in low
                and b'wp/v2' in low)
    if path == '/wp-login.php':
        return (b'wp-login' in low and
                (b'id="loginform"' in low or b'name="log"' in low))
    if path == '/wp-admin/':
        return (b'wp-admin' in low and
                (b'id="wpwrap"' in low or b'id="adminmenu"' in low))
    if path == '/':
        return (b'wp-content/' in low and
                (b'wp-site-blocks' in low or b'wp-block-' in low))
    return False

def diagnose_private_cli_log(path: Path) -> str:
    """Read a discarded private log; expose ONLY enumerated error categories."""
    try:
        data = path.read_text(errors='replace')[-16000:].lower()
    except OSError:
        return 'CLI_LOG_UNAVAILABLE'
    signatures = (
        ('could not activate', 'WP_BLUEPRINT_ACTIVATION_FAILURE'),
        ('unknown option', 'PLAYGROUND_UNKNOWN_OPTION'),
        ('invalid option', 'PLAYGROUND_INVALID_OPTION'),
        ('npm error canceled', 'NPM_CANCELED'),
        ('npm err! canceled', 'NPM_CANCELED'),
        ('enotfound', 'DEPENDENCY_DNS_FAILURE'),
        ('econnrefused', 'DEPENDENCY_CONNECTION_FAILURE'),
        ('etimedout', 'DEPENDENCY_TIMEOUT'),
        ('enoent', 'LOCAL_MISSING_FILE'),
        ('fatal error', 'WP_PHP_FATAL'),
        ('uncaught', 'WP_UNCAUGHT_EXCEPTION'),
        ('error:', 'PLAYGROUND_CLI_ERROR'),
    )
    return next((tag for phrase, tag in signatures if phrase in data),
                'CLI_NO_ALLOWLISTED_ERROR')

def wait_for_wordpress(process, seconds: int = 180, clock=time.monotonic,
                       sleep=time.sleep, opener=None):
    """Return (allowlisted positive endpoint, safe probe counts).

    Always sends requests to four fixed loopback routes. Blocks redirects;
    cookies remain process-private and are not serialized. A local redirect
    can establish a session before a positive REST/login/admin response.
    """
    if seconds < 1 or seconds > 240:
        raise ValueError('INVALID_READINESS_BUDGET')
    client = opener or urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPCookieProcessor(CookieJar()),
        NeverRedirect(),
    )
    observed: Counter[str] = Counter()
    deadline = clock() + seconds
    while clock() < deadline:
        if process.poll() is not None:
            raise ReadinessFailure('PLAYGROUND_EXITED', dict(observed))
        for path in PATHS:
            label = ('ROOT' if path == '/' else
                     'REST' if path == '/wp-json/' else
                     'LOGIN' if path == '/wp-login.php' else 'ADMIN')
            # This URL is literal/allowlisted, not derived from response data.
            req = urllib.request.Request(ORIGIN + path, headers={
                'Accept': 'application/json' if label == 'REST' else 'text/html',
            })
            try:
                with client.open(req, timeout=3) as response:
                    ctype = response.headers.get('Content-Type', '')
                    body = response.read(LIMIT)
                    if response.status == 200 and positive_wordpress_marker(path, ctype, body):
                        observed[label + '_WORDPRESS_OK'] += 1
                        return label, dict(sorted(observed.items()))
                    observed[label + '_NOT_WP'] += 1
            except urllib.error.HTTPError as exc:
                if exc.code in (301, 302, 303, 307, 308):
                    cls = safe_redirect_class(exc.headers.get('Location', ''))
                    observed[label + '_' + cls] += 1
                else:
                    observed[label + '_HTTP_' + str(exc.code)[:3]] += 1
                exc.close()
            except (OSError, ValueError, urllib.error.URLError):
                observed[label + '_UNAVAILABLE'] += 1
        sleep(1)
    raise ReadinessFailure('WORDPRESS_LOCAL_READINESS_TIMEOUT', dict(observed))
