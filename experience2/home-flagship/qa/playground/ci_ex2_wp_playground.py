#!/usr/bin/env python3
"""Ephemeral, localhost-only WordPress/Assembler smoke for the existing preview kit.

Never touches WP.com production, user data, Jetpack configuration or navigation.
The established verify_exact_staging.py remains the authority on browser acceptance.
"""
from __future__ import annotations
import argparse
import json
import os
import re
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
import http.cookiejar
import urllib.parse
import urllib.error

BASE = 'http://127.0.0.1:9400/'
PAGE = BASE + '?pagename=fv-ex2-playground-review'


def receipt(out: Path, status: str, error: str = '') -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / 'EPHEMERAL_WP_CI.json').write_text(json.dumps({
        'status': status, 'error': error[:350], 'wordpress_environment': 'ISOLATED_EPHEMERAL_PLAYGROUND',
        'public_wordpress_writes': False, 'wordpress_com_host_parity': 'NOT_ESTABLISHED',
        'jetpack_subscriptions': 'NOT_TESTED', 'real_user_CWV': 'NOT_MEASURED',
        'release': 'HOLD_PENDING_RIGHTS_QD_AND_FOUNDER_APPROVAL',
    }, indent=2) + '\n')


def diagnose_private_cli_log(logpath: Path) -> str:
    """Only publish an allowlisted failure category; NEVER echo raw CLI output."""
    if not logpath.is_file():
        return 'CLI_LOG_NOT_CREATED'
    data = logpath.read_text(errors='replace')[-12000:].lower()
    patterns = (
        ('refused: local template readback differs', 'WP_SAVED_TEMPLATE_BYTES_CHANGED'),
        ('existing non-fv local override', 'WP_PARITY_EXISTING_CONTENT_CONFLICT'),
        ('local theme taxonomy assignment failed', 'WP_THEME_TAXONOMY_FAILURE'),
        ('local template area assignment failed', 'WP_TEMPLATE_AREA_FAILURE'),
        ('refused: staging parity contract mismatch', 'WP_PARITY_CONTRACT_FAILURE'),
        ('could not activate', 'WP_BLUEPRINT_ACTIVATION_FAILURE'),
        ('npm error canceled', 'NPM_INTERACTIVE_INSTALL_CANCELLED'),
        ('npm err! canceled', 'NPM_INTERACTIVE_INSTALL_CANCELLED'),
        ('could not determine executable', 'NPM_EXECUTABLE_UNRESOLVED'),
        ('unknown option', 'UNRECOGNIZED_PLAYGROUND_CLI_OPTION'),
        ('invalid option', 'UNRECOGNIZED_PLAYGROUND_CLI_OPTION'),
        ('econnrefused', 'PLAYGROUND_DEPENDENCY_NETWORK_FAILURE'),
        ('enotfound', 'PLAYGROUND_DEPENDENCY_DNS_FAILURE'),
        ('etimedout', 'PLAYGROUND_DEPENDENCY_TIMEOUT'),
        ('enoent', 'PLAYGROUND_MISSING_RUNTIME_FILE'),
        ('error:', 'PLAYGROUND_CLI_RUNTIME_ERROR'),
    )
    return next((code for phrase, code in patterns if phrase in data),
                'PLAYGROUND_CLI_EXIT_REASON_UNCLASSIFIED_PRIVATE_LOG_ONLY')


def safe_cli_failure_excerpt(logpath: Path) -> str:
    """Expose only a tiny redacted error class/phrase, never raw CLI logs.

    The ephemeral runner has no production tokens, but the full Node/Blueprint
    output is still PRIVATE and never copied to an artifact. This deliberately
    destroys URLs, filesystem paths, emails, long IDs and credential-bearing
    lines before selecting a diagnostic fragment.
    """
    if not logpath.is_file():
        return 'NO_PRIVATE_LOG'
    data = logpath.read_text(errors='replace')[-16000:]
    data = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', data)
    selected = []
    for line in data.splitlines():
        if not re.search(r'(?i)\b(error|exception|fatal|refused|failed|invalid|cannot)\b', line):
            continue
        if re.search(r'(?i)authorization|password|secret|api[_ -]?key|bearer|session|cookie|credential|token', line):
            continue
        # Do not surface execution environment paths or external URLs.
        line = re.sub(r'https?://\S+', '[URL]', line)
        line = re.sub(r'(?:/home/|/tmp/|/var/|/opt/|/usr/)\S+', '[LOCAL_PATH]', line)
        line = re.sub(r'\b[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', '[EMAIL]', line)
        line = re.sub(r'\b[A-Za-z0-9+/=_-]{50,}\b', '[LONG_ID]', line)
        line = re.sub(r'[^A-Za-z0-9 .,;:()_\-\[\]]', ' ', line)
        line = ' '.join(line.split())
        if len(line) >= 8:
            selected.append(line[-110:])
    if not selected:
        return 'NO_SAFE_ERROR_LINES'
    # Prefer a final error declaration over a JavaScript stack-frame line.
    return ' ; '.join(selected[-2:])[-180:]


def build_local_debug_blueprint_argv(stage: Path, argv: list[str], secret_dir: Path) -> list[str]:
    """Construct a localhost-only FORENSIC blueprint, never an acceptance input.

    This runs only after canonical staging fails. No mutation of the reviewed
    Blueprint, site database, source assets, or production service is permitted.
    """
    if argv[:3] != ['npx', '@wp-playground/cli@3.1.61', 'server']:
        raise ValueError('Refuse diagnostic on unknown CLI')
    expected = '--blueprint=' + str(stage / 'playground-blueprint.json')
    if argv.count(expected) != 1 or argv.count('--port=9400') != 1:
        raise ValueError('Refuse diagnostic on unknown Blueprint or port')
    if len([x for x in argv if x.startswith('--mount=')]) != 3:
        raise ValueError('Refuse diagnostic on unknown mount topology')
    data = json.loads((stage / 'playground-blueprint.json').read_text())
    first = data.get('steps', [None])[0]
    if not isinstance(first, dict) or first.get('step') != 'defineWpConfigConsts':
        raise ValueError('Refuse diagnostic without local environment declaration')
    consts = first.get('consts')
    if not isinstance(consts, dict) or consts.get('WP_ENVIRONMENT_TYPE') != 'local' or consts.get('FV_EX2_ALLOW_PREVIEW') is not True:
        raise ValueError('Refuse diagnostic outside isolated local preview')
    first['consts'] = {**consts, 'WP_DEBUG': True, 'WP_DEBUG_LOG': True,
                       'WP_DEBUG_DISPLAY': True, 'WP_DISABLE_FATAL_ERROR_HANDLER': True}
    file = secret_dir / 'local-debug-blueprint.json'
    file.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    return ['--blueprint=' + str(file) if a == expected
            else '--port=9401' if a == '--port=9400' else a for a in argv]


def local_debug_error_category(repo: Path, stage: Path, argv: list[str], secret_dir: Path) -> str:
    """Retry once on private loopback 9401 solely to diagnose PHP startup failure.

    Exposed diagnostic is sanitized text only. Raw WP/CLI output is never sent
    to Actions logs or uploaded artifacts. Retry cannot change release status.
    """
    logpath = secret_dir / 'local-debug-private.log'
    try:
        command = build_local_debug_blueprint_argv(stage, argv, secret_dir)
    except (ValueError, OSError, KeyError, TypeError):
        return 'DIAGNOSTIC_PRECONDITION_REJECTED'
    child = None
    try:
        with logpath.open('w', encoding='utf-8') as private_log:
            child = subprocess.Popen(command, cwd=repo, stdout=private_log, stderr=subprocess.STDOUT,
                                     start_new_session=True, env={**os.environ,
                                         'npm_config_yes':'true', 'npm_config_audit':'false', 'CI':'true'})
            deadline = time.monotonic() + 75
            while time.monotonic() < deadline and child.poll() is None:
                time.sleep(0.5)
        if child.poll() is None:
            return 'DIAGNOSTIC_WORDPRESS_REMAINED_ALIVE_NOT_RELEASE'
        return diagnose_private_cli_log(logpath) + ': ' + safe_cli_failure_excerpt(logpath)
    except (OSError, subprocess.SubprocessError):
        return 'DIAGNOSTIC_PROCESS_LAUNCH_FAILED'
    finally:
        if child is not None and child.poll() is None:
            try: os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            try: child.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(child.pid, signal.SIGKILL)


def ready(process: subprocess.Popen, seconds: int = 180) -> None:
    """Probe ONLY loopback. Record HTTP status classes, never URLs, bodies, or logs.

    A live CLI with persistent HTTP 500 is different from an unopened port.
    The old probe silently treated both as 'no response', hiding actionable
    WordPress/Blueprint failures in exact-head staging CI.
    """
    class _NeverRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    # Playground/WP may establish a localhost session via Set-Cookie + 302
    # before serving HTML. A stateless urllib opener repeats the same 302
    # forever. Preserve cookies only in this ephemeral loopback probe;
    # NEVER follow Location, allow remote hosts, or persist cookie values.
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        urllib.request.HTTPCookieProcessor(cookies),
        _NeverRedirect(),
    )
    observations: dict[str, int] = {}

    def record(state: str) -> None:
        observations[state] = observations.get(state, 0) + 1

    def summary() -> str:
        return ','.join(f'{key}:{observations[key]}' for key in sorted(observations)) or 'NO_PROBE'

    def redirect_reason(raw: str) -> str:
        # Only report an allowlisted CLASS, never the redirect target.
        if not raw:
            return 'LOCATION_MISSING'
        try:
            dest = urllib.parse.urlsplit(urllib.parse.urljoin(BASE, raw))
            origin = urllib.parse.urlsplit(BASE)
            if dest.username or dest.password:
                return 'USERINFO_PRESENT'
            if dest.scheme != 'http':
                return 'SCHEME_OTHER'
            if dest.hostname != '127.0.0.1':
                return 'HOST_NOT_EXACT_LOOPBACK'
            if dest.port != origin.port:
                return 'PORT_MISMATCH'
            # Only public, fixed WordPress routes are categorized. Never
            # reveal a full Location, arbitrary path, query, host or token.
            if dest.path == '/wp-admin/install.php':
                return 'WP_INSTALL_NOT_FINISHED'
            if dest.path == '/wp-admin/upgrade.php':
                return 'WP_DATABASE_UPGRADE_REQUIRED'
            if dest.path == '/' and dest.query == 'pagename=fv-ex2-playground-review':
                return 'BLUEPRINT_PRIVATE_LANDING'
            if dest.path == '/' and not dest.query:
                return 'ROOT_PATH'
            if dest.path not in ('/wp-login.php', '/wp-admin/'):
                return 'PATH_NOT_ALLOWLISTED'
            return 'ALLOWED_PATH_BUT_LOGIN_UNVERIFIED'
        except (ValueError, TypeError):
            return 'MALFORMED'

    def local_wordpress_positive_probe() -> bool:
        """Check fixed loopback endpoints ONLY; never follow a redirect target.

        A Blueprint landingPage can intentionally redirect / to a private
        preview. Login may also redirect (e.g. Playground auto-login), so
        neither a root 3xx nor a login 3xx proves WordPress is ready.
        Chromium still has to establish the real seven-chapter render.
        """
        try:
            with opener.open(urllib.parse.urljoin(BASE, '/wp-json/'), timeout=3) as response:
                body = response.read(131072)
                ctype = response.headers.get('Content-Type', '').lower()
                if (response.status == 200 and 'application/json' in ctype
                        and b'"namespaces"' in body and b'"routes"' in body
                        and b'wp/v2' in body):
                    return True
                record('REST_NO_WORDPRESS_SCHEMA')
        except urllib.error.HTTPError as exc:
            if exc.code in (301, 302, 303, 307, 308):
                record('REST_REDIRECT_' + redirect_reason(exc.headers.get('Location', '')))
            else:
                record('REST_HTTP_' + str(exc.code))
            exc.close()
        except (OSError, urllib.error.URLError, ValueError):
            record('REST_UNAVAILABLE')
        for endpoint, marker in (('/wp-login.php', b'wp-login'),
                                 ('/wp-admin/', b'id="wpwrap"')):
            label = 'LOGIN' if endpoint == '/wp-login.php' else 'ADMIN'
            try:
                with opener.open(urllib.parse.urljoin(BASE, endpoint), timeout=3) as response:
                    body = response.read(32768).lower()
                    if response.status == 200 and marker in body:
                        return True
                    record(label + '_NOT_WORDPRESS_HTML')
            except urllib.error.HTTPError as exc:
                if exc.code in (301, 302, 303, 307, 308):
                    record(label + '_REDIRECT_' + redirect_reason(exc.headers.get('Location', '')))
                else:
                    record(label + '_HTTP_' + str(exc.code))
                exc.close()
            except (OSError, urllib.error.URLError, ValueError):
                record(label + '_UNAVAILABLE')
        return False

    stop = time.monotonic() + seconds
    while time.monotonic() < stop:
        if process.poll() is not None:
            raise RuntimeError('Isolated WordPress CLI exited before localhost readiness; probe_states=' + summary())
        try:
            with opener.open(BASE, timeout=3) as response:
                if response.status == 200 and len(response.read(256)) > 0:
                    return
                record('HTTP_' + str(response.status) + '_EMPTY_OR_UNREADY')
        except urllib.error.HTTPError as exc:
            location = exc.headers.get('Location', '')
            if exc.code in (301, 302, 303, 307, 308):
                # Never request the redirect Location. Check origin safely, then
                # request ONLY three fixed, known WordPress loopback paths.
                local = False
                try:
                    dest = urllib.parse.urlsplit(urllib.parse.urljoin(BASE, location))
                    origin = urllib.parse.urlsplit(BASE)
                    local = (bool(location) and len(location) < 512
                             and dest.scheme == 'http'
                             and dest.hostname == '127.0.0.1'
                             and dest.port == origin.port
                             and not dest.username and not dest.password)
                except (ValueError, TypeError):
                    pass
                if local and local_wordpress_positive_probe():
                    exc.close()
                    return  # Browser/axe/media verification is still mandatory.
                record('REDIRECT_' + redirect_reason(location))
            else:
                record('HTTP_' + str(exc.code))
            exc.close()
        except (OSError, urllib.error.URLError):
            record('NO_HTTP_RESPONSE')
        time.sleep(1)
    raise RuntimeError('Isolated WordPress not HTTP 200 on loopback within startup gate; probe_states=' + summary())


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--expected-head', required=True)
    p.add_argument('--stage', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--axe-script', required=True, type=Path)
    p.add_argument('--lighthouse-runner', required=True, type=Path)
    args = p.parse_args()
    process = None
    try:
        repo = args.repo.resolve(strict=True)
        stage = args.stage.resolve(strict=True)
        out = args.out.resolve(strict=False)
        actual = subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'], text=True).strip()
        if actual != args.expected_head or len(actual) != 40:
            raise ValueError('Exact-head mismatch: refuse a synthetic or dirty source checkout')
        if not args.axe_script.is_file() or args.axe_script.stat().st_size < 100000:
            raise ValueError('Missing actual axe-core test library; fail closed')
        argv = json.loads((stage / 'playground-cli-arguments.json').read_text())
        if (not isinstance(argv, list) or argv[:3] != ['npx','@wp-playground/cli@3.1.61','server']
            or '--port=9400' not in argv or len([x for x in argv if x.startswith('--mount=')]) != 3):
            raise ValueError('Unexpected WordPress startup flags or mount topology')
        runtime = subprocess.run(
            [sys.executable, str(Path(__file__).with_name('check_playground_runtime.py'))],
            capture_output=True, text=True, timeout=20)
        if runtime.returncode:
            raise ValueError('Unsupported pinned Playground Node/npm engine; no staging launched')
        if out == stage or repo in out.parents or repo in stage.parents:
            raise ValueError('Artifacts and isolated stage must be outside repository')
        out.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='fv-ex2-wp-auth-private-') as secrets:
            secret_dir = Path(secrets)
            with (secret_dir / 'wp-cli-private.log').open('w', encoding='utf8') as log:
                process = subprocess.Popen(argv, cwd=repo, stdout=log, stderr=subprocess.STDOUT,
                                           start_new_session=True, env={
                                               **os.environ, 'npm_config_yes':'true',
                                               'npm_config_audit':'false', 'CI':'true'})
                try:
                    ready(process)
                except RuntimeError as exc:
                    reason = diagnose_private_cli_log(secret_dir / 'wp-cli-private.log')
                    forensic = local_debug_error_category(repo, stage, argv, secret_dir)
                    detail = safe_cli_failure_excerpt(secret_dir / 'wp-cli-private.log')
                    raise RuntimeError(str(exc) + '; safe_category=' + reason
                                       + '; local_diagnostic=' + forensic
                                       + '; safe_excerpt=' + detail) from None
                from playwright.sync_api import sync_playwright
                storage = secret_dir / 'local-editor-storage.json'
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch(headless=True)
                    context = browser.new_context(viewport={'width': 390, 'height': 844}, service_workers='block')
                    page = context.new_page()
                    page.goto(BASE + 'wp-admin/', wait_until='domcontentloaded', timeout=30000)
                    # Only the fresh local Playground's well-known test login; never user secrets.
                    if page.locator('#user_login').count() and page.locator('#user_pass').count():
                        page.locator('#user_login').fill('admin')
                        page.locator('#user_pass').fill('password')
                        page.locator('#wp-submit').click()
                    page.goto(PAGE, wait_until='domcontentloaded', timeout=30000)
                    frame_element = page.locator('iframe[title="Final Vestige Experience 2.0, unpublished editorial preview"]')
                    frame_element.wait_for(state='attached', timeout=20000)
                    frame_element.scroll_into_view_if_needed()
                    frame = frame_element.element_handle().content_frame()
                    if frame is None:
                        raise RuntimeError('Local WordPress iframe not attached')
                    frame.locator('[data-fv-home-flagship]').wait_for(timeout=25000)
                    # A separate release-critical path: actually SAVE the reviewed
                    # Gutenberg block on a disposable LOCAL WordPress draft, then
                    # read it back and render it as a front-end post. The iframe
                    # preview above does not exercise editor persistence.
                    admission_dir = repo / 'experience2/home-flagship/qa/release-candidate'
                    sys.path.insert(0, str(admission_dir))
                    try:
                        from verify_local_gutenberg_roundtrip import run as verify_gutenberg_saved
                        saved = verify_gutenberg_saved(page, repo, args.expected_head, out, args.axe_script)
                    finally:
                        sys.path.remove(str(admission_dir))
                    if saved.get('status') != 'ISOLATED_GUTENBERG_PERSISTENCE_PASS_NOT_HOSTED_RELEASE':
                        raise ValueError('LOCAL_WORDPRESS_GUTENBERG_PERSISTENCE_HOLD')
                    context.storage_state(path=str(storage))
                    os.chmod(storage, 0o600)
                    context.close()
                    browser.close()
                # Committed verifier owns five widths, axe, no-JS, exact bytes,
                # real media HTTP bodies, and screenshots. Never self-certify release.
                cmd = [sys.executable,
                       str(repo / 'experience2/home-flagship/qa/release-candidate/verify_exact_staging.py'),
                       '--url',PAGE,'--allow-host','127.0.0.1',
                       '--expected-head',args.expected_head,'--repo',str(repo),
                       '--storage-state',str(storage),
                       '--axe-script',str(args.axe_script), '--out',str(out)]
                outcome = subprocess.run(cmd, cwd=repo, check=False, timeout=240,
                                         capture_output=True, text=True)
                if outcome.returncode:
                    receipt(out, 'WORDPRESS_RENDERED_BUT_ADMISSION_HOLD',
                            'exact staging browser audit exited '+str(outcome.returncode))
                    return 2
                # Extra exact-head CDP lab against the SAME authenticated
                # WordPress renderer, while isolated Playground remains alive.
                # Never log storage-state, AJAX nonce or full private URL.
                lab_cmd = [sys.executable, str(repo /
                    'experience2/home-flagship/qa/playground/measure_private_lab.py'),
                    '--repo', str(repo), '--expected-head', args.expected_head,
                    '--storage-state', str(storage), '--out', str(out)]
                lab = subprocess.run(lab_cmd, cwd=repo, check=False,
                                     timeout=240, capture_output=True, text=True)
                if lab.returncode:
                    receipt(out, 'WORDPRESS_RENDERED_BUT_THROTTLED_PERFORMANCE_HOLD',
                            'Private CDP lab failed or exceeded measured LCP/CLS budget')
                    return 2
                # Real Lighthouse measures the SAME nonce-authenticated localhost
                # WordPress renderer. It must never write raw LHR, URLs or cookies
                # into GitHub artifacts, even on failure.
                lighthouse_root = 'experience2/home-flagship/qa/playground/'
                for name in ('measure_private_lighthouse.mjs',
                             'lighthouse_receipt.mjs', 'test_private_lighthouse.mjs'):
                    source = repo / lighthouse_root / name
                    committed = subprocess.check_output(
                        ['git', '-C', str(repo), 'show',
                         args.expected_head + ':' + lighthouse_root + name])
                    if source.is_symlink() or source.read_bytes() != committed:
                        raise ValueError('LIGHTHOUSE_SOURCE_NOT_EXACT_HEAD')
                if (not args.lighthouse_runner.is_file()
                        or args.lighthouse_runner.is_symlink()
                        or args.lighthouse_runner.read_bytes() !=
                            (repo / lighthouse_root / 'measure_private_lighthouse.mjs').read_bytes()):
                    raise ValueError('LIGHTHOUSE_RUNNER_NOT_SOURCE_IDENTICAL')
                lh_cmd = ['node', str(args.lighthouse_runner),
                          '--repo', str(repo),
                          '--expected-head', args.expected_head,
                          '--storage-state', str(storage),
                          '--out', str(out)]
                lh = subprocess.run(lh_cmd, cwd=repo, check=False,
                                    timeout=420, capture_output=True, text=True)
                if lh.returncode:
                    receipt(out, 'WORDPRESS_RENDERED_BUT_LIGHTHOUSE_MEASUREMENT_HOLD',
                            'Authenticated, localhost-only Lighthouse audit failed')
                    return 2
                lh_receipt = out / 'LIGHTHOUSE_PRIVATE_LAB.json'
                if not lh_receipt.is_file():
                    receipt(out, 'WORDPRESS_RENDERED_BUT_LIGHTHOUSE_MEASUREMENT_HOLD',
                            'Lighthouse report missing')
                    return 2
                details = json.loads(lh_receipt.read_text())
                if (details.get('exact_source_commit') != args.expected_head
                        or len(details.get('audit_profiles', [])) != 2
                        or details.get('public_wordpress_writes') is not False):
                    receipt(out, 'WORDPRESS_RENDERED_BUT_LIGHTHOUSE_MEASUREMENT_HOLD',
                            'Lighthouse report custody mismatch')
                    return 2
                # Additional genuine 320px, keyboard and emulated-touch checks
                # against the same authenticated isolated WP render. Distinct
                # from manual AT, real-device testing or 200% browser zoom.
                usability_cmd = [sys.executable,
                    str(repo / 'experience2/home-flagship/qa/playground/verify_private_usability.py'),
                    '--repo', str(repo), '--expected-head', args.expected_head,
                    '--storage-state', str(storage), '--out', str(out)]
                usability = subprocess.run(usability_cmd, cwd=repo, check=False,
                                           timeout=180, capture_output=True, text=True)
                if usability.returncode:
                    receipt(out, 'WORDPRESS_RENDERED_BUT_ACCESSIBILITY_USABILITY_HOLD',
                            '320px reflow, keyboard, touch or reduced-motion gate failed')
                    return 2
                usability_receipt = out / 'PRIVATE_USABILITY.json'
                if not usability_receipt.is_file():
                    receipt(out, 'WORDPRESS_RENDERED_BUT_ACCESSIBILITY_USABILITY_HOLD',
                            'No isolated usability receipt was produced')
                    return 2
                usability_report = json.loads(usability_receipt.read_text())
                if (usability_report.get('exact_source_commit') != args.expected_head
                        or usability_report.get('failure_codes') != []
                        or usability_report.get('production_writes') is not False):
                    receipt(out, 'WORDPRESS_RENDERED_BUT_ACCESSIBILITY_USABILITY_HOLD',
                            'Isolated usability receipt rejected by custody gate')
                    return 2
                receipt(out, 'ISOLATED_BROWSER_AND_LAB_ADMISSION_PASSED_NOT_RELEASE')
                return 0
    except Exception as exc:
        receipt(args.out, 'STAGING_STARTUP_OR_RENDER_BLOCKED', type(exc).__name__+': '+str(exc))
        return 2
    finally:
        if process is not None and process.poll() is None:
            try: os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError: pass
            try: process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)


if __name__ == '__main__':
    raise SystemExit(main())
