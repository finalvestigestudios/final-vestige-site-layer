#!/usr/bin/env python3
"""Ephemeral, localhost-only WordPress/Assembler smoke for the existing preview kit.

Never touches WP.com production, user data, Jetpack configuration or navigation.
The established verify_exact_staging.py remains the authority on browser acceptance.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request

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


def ready(process: subprocess.Popen, seconds: int = 180) -> None:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    stop = time.monotonic() + seconds
    while time.monotonic() < stop:
        if process.poll() is not None:
            raise RuntimeError('Isolated WordPress process exited before localhost HTTP readiness')
        try:
            with opener.open(BASE, timeout=3) as response:
                if response.status == 200 and len(response.read(256)) > 0:
                    return
        except (OSError, urllib.error.URLError):
            pass
        time.sleep(1)
    raise RuntimeError('Isolated WordPress did not respond on loopback within startup gate')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', required=True, type=Path)
    p.add_argument('--expected-head', required=True)
    p.add_argument('--stage', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--axe-script', required=True, type=Path)
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
        if (not isinstance(argv, list) or argv[:3] != ['npx','@wp-playground/cli@latest','server']
            or '--port=9400' not in argv or len([x for x in argv if x.startswith('--mount=')]) != 3):
            raise ValueError('Unexpected WordPress startup flags or mount topology')
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
                    raise RuntimeError(str(exc) + '; safe_category=' + reason) from None
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
                receipt(out, 'ISOLATED_BROWSER_ADMISSION_PASSED_NOT_RELEASE')
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
