#!/usr/bin/env python3
"""One-command local WordPress/Assembler launch + existing exact-page acceptance.

No production requests or CMS writes. Only a verified local ZIP is executed.
A preflight PASS is NOT WordPress acceptance and an audit exit 1 is RELEASE HOLD.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
import socket
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError, HTTPError
from urllib.parse import urlsplit
from urllib.request import build_opener, HTTPRedirectHandler
from zipfile import ZipFile

BUNDLE_SHA256 = '9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d'
SOURCE_BLUEPRINT = '300c79f7936d7fdf58294bb96e7b0cd1ebc0b349cdf4d2c4d13e5ec52000b23f'
ASSEMBLER_COMMIT = '75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f'
# Fixed environment for reproducible source QA; not a claim of WordPress.com host parity.
# Validated against official CLI / core release docs on 2026-11-07.
PLAYGROUND_CLI_VERSION = '3.1.55'
WORDPRESS_CORE_VERSION = '7.1.4'
PLAYGROUND_PHP_VERSION = '8.3'
ALLOW_FILES = {'blueprint.json', 'SOURCE_CUSTODY.json', 'REVIEW.txt',
               'mu-plugins/fv-ex2-playground-review.php',
               'mu-plugins/fv-ex2-private-browser-receipt.php'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def attest(bundle):
    raw = bundle.read_bytes()
    if sha(raw) != BUNDLE_SHA256:
        raise ValueError('ZIP_SHA_DRIFT: refuse unreviewed or outdated executable bundle')
    with ZipFile(bundle) as z:
        if set(z.namelist()) != ALLOW_FILES:
            raise ValueError('BUNDLE_FILES_CHANGED')
        source = json.loads(z.read('SOURCE_CUSTODY.json'))
        bp = json.loads(z.read('blueprint.json'))
        if source.get('exact_source_sha256') != SOURCE_BLUEPRINT or source.get('assembler_commit') != ASSEMBLER_COMMIT:
            raise ValueError('SOURCE_OR_THEME_PIN_CHANGED')
        for path, digest in source.get('files_sha256', {}).items():
            if path not in ALLOW_FILES or sha(z.read(path)) != digest:
                raise ValueError('PHP_PAYLOAD_DRIFT: '+path)
        if len(source.get('files_sha256', {})) != 2:
            raise ValueError('MISSING_ATTESTED_PHP')
        steps = bp.get('steps', [])
        if [s.get('step') for s in steps] != ['runPHP','installTheme','mkdir','writeFile','writeFile','runPHP','runPHP']:
            raise ValueError('UNEXPECTED_WORDPRESS_MUTATIONS')
        if ('FV_EX2_REFUSE_NON_LOOPBACK_BEFORE_ANY_SITE_WRITE' not in steps[0].get('code','') or
                'WP_ENVIRONMENT_TYPE' not in steps[0].get('code','')):
            raise ValueError('LOCAL_ADMISSION_MISSING')
        theme = steps[1]['themeData']
        if (theme.get('resource'), theme.get('ref'), theme.get('path')) != ('git:directory',ASSEMBLER_COMMIT,'assembler'):
            raise ValueError('ASSEMBLER_SOURCE_CHANGED')
        if bp.get('landingPage') != '/':
            raise ValueError('UNEXPECTED_LANDING_PAGE')
    return {'zip_sha256':sha(raw),'source_blueprint_sha256':SOURCE_BLUEPRINT,
            'assembler_commit':ASSEMBLER_COMMIT,'php_payloads_verified':2,
            'scope':'local-only source preflight; NOT a WordPress pass'}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise ValueError('LOOPBACK_REDIRECT_REFUSED')


def refuse_occupied_port(port):
    """Fail closed before spawning npm if another process already owns review port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        if sock.connect_ex(('127.0.0.1', port)) == 0:
            raise RuntimeError('REVIEW_PORT_ALREADY_IN_USE: refuse ambiguous local server')


def wordpress_rest_identity(url, opener):
    """Read-only second origin/WordPress check, not a cryptographic attestation."""
    rest_url = url + 'wp-json/'
    try:
        with opener.open(rest_url, timeout=2) as response:
            if response.status != 200:
                return None
            if 'application/json' not in response.headers.get('Content-Type', '').lower():
                return None
            payload = json.loads(response.read(65537))
    except (URLError, HTTPError, OSError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    namespaces = payload.get('namespaces')
    if not isinstance(namespaces, list) or 'wp/v2' not in namespaces:
        return None
    # An imported production URL must never qualify as isolated WordPress.
    base = url.rstrip('/')
    if not isinstance(payload.get('url'), str) or payload['url'].rstrip('/') != base:
        return None
    return {'wordpress_rest_api': True, 'rest_url': rest_url,
            'wp_v2_namespace': True, 'local_site_url_matched': True}


def ready(url, timeout_seconds, process):
    # Probe loopback only; do not follow redirects to the live site.
    p = urlsplit(url)
    if p.scheme != 'http' or p.hostname != '127.0.0.1' or p.path != '/':
        raise ValueError('REFUSE_NON_LOOPBACK_PROBE')
    opener = build_opener(NoRedirect)
    expiry = time.monotonic() + timeout_seconds
    last = 'NOT_STARTED'
    while time.monotonic() < expiry:
        if process.poll() is not None:
            raise RuntimeError('LOCAL_CLI_EXITED_'+str(process.returncode)+'_'+last)
        try:
            with opener.open(url, timeout=2) as response:
                body = response.read(2000000).decode('utf-8', errors='replace')
                if response.status == 200 and 'data-fv-home-flagship' in body and 'wp-site-blocks' in body:
                    identity = wordpress_rest_identity(url, opener)
                    if identity:
                        return {'http_status':200,'wordpress_shell_detected':True,
                                'flagship_root_detected':True, **identity}
                    last = 'WORDPRESS_REST_IDENTITY_MISSING_OR_MISMATCHED'
                else:
                    last = 'HTTP_'+str(response.status)+'_WP_SHELL_OR_FLAGSHIP_MISSING'
        except (URLError,TimeoutError,OSError,ValueError) as exc:
            last = type(exc).__name__+': '+str(exc)[:90]
        time.sleep(.7)
    raise TimeoutError('LOCAL_WORDPRESS_NOT_READY_'+last)


def playground_launch_command(npx, port, url, bundle):
    """Return immutable, auditable release-pinned CLI invocation.

    Do not silently track latest CLI/core/PHP: a fresh release can modify output
    without any change to the source commit. Distinct host parity is not claimed.
    """
    p = urlsplit(url)
    if p.scheme != 'http' or p.hostname != '127.0.0.1' or p.path != '/' or p.port != port:
        raise ValueError('REFUSE_NON_LOOPBACK_LAUNCH')
    if port not in range(9400, 9500):
        raise ValueError('REFUSE_PORT_OUTSIDE_REVIEW_RANGE')
    return [npx, '--yes', f'@wp-playground/cli@{PLAYGROUND_CLI_VERSION}',
            'server', f'--port={port}', f'--site-url={url}',
            f'--wp={WORDPRESS_CORE_VERSION}', f'--php={PLAYGROUND_PHP_VERSION}',
            f'--blueprint={bundle.resolve()}']


def execute(bundle, output, audit, axe, port, timeout):
    if not (9400 <= port <= 9499):
        raise ValueError('PORT_OUTSIDE_REVIEW_RANGE_9400_TO_9499')
    if not audit.is_file():
        raise ValueError('EXISTING_NATIVE_WORDPRESS_ADMISSION_SCRIPT_MISSING')
    # Avoid accepting somebody else's server as the WordPress we intend to launch.
    refuse_occupied_port(port)
    npx = shutil.which('npx')
    if not npx:
        raise RuntimeError('NPX_NOT_INSTALLED')
    output.mkdir(parents=True,exist_ok=True)
    url = f'http://127.0.0.1:{port}/'
    cmd = playground_launch_command(npx, port, url, bundle)
    result = {'scope':'isolated WordPress CLI; NOT WordPress.com production',
              'generated_utc':datetime.now(timezone.utc).isoformat(),
              'release':'HOLD','url':url,'command':cmd[1:-1]+['--blueprint=[PINNED_ZIP]'],
              'axe':str(axe) if axe else 'ABSENT_REQUIRES_HOLD',
              'wordpress':'NOT_VERIFIED','admission':'NOT_RUN',
              'commercial_outcomes':'NOT_MEASURED', 'host_parity':'NOT_TESTED',
              'runtime_pins':{'playground_cli':PLAYGROUND_CLI_VERSION,
                              'wordpress_core':WORDPRESS_CORE_VERSION,
                              'php':PLAYGROUND_PHP_VERSION}}
    # Keep all writes in a fresh temporary working directory, NOT repository or WP prod.
    with tempfile.TemporaryDirectory(prefix='fv-ex2-wp-local-') as sandbox:
        with (output/'local_cli.log').open('w') as log:
            env=os.environ.copy()
            env.update({'npm_config_fetch_retries':'0','npm_config_fetch_timeout':'9000',
                        'npm_config_audit':'false','npm_config_fund':'false'})
            process=subprocess.Popen(cmd, cwd=sandbox, stdout=log, stderr=subprocess.STDOUT, env=env)
            try:
                result['startup']=ready(url,timeout,process)
                result['wordpress']='SHELL_AND_FLAGSHIP_SEEN_REQUIRES_FULL_ADMISSION'
                check = [sys.executable,str(audit.resolve()),'--url',url,
                         '--output',str((output/'full_admission').resolve())]
                if axe:
                    check += ['--axe',str(axe.resolve())]
                checkrun = subprocess.run(check,cwd=sandbox, capture_output=True, text=True,timeout=210)
                result['admission_exit']=checkrun.returncode
                result['admission_stdout']=checkrun.stdout[-1200:]
                result['admission_stderr']=checkrun.stderr[-1200:]
                result['admission']='PARTIAL_TEST_EXECUTED_RELEASE_HOLD'
            except Exception as exc:
                result['error']=type(exc).__name__+': '+str(exc)[:350]
            finally:
                process.terminate()
                try: process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill();process.wait(timeout=5)
    (output/'local_acceptance.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bundle',type=Path,required=True)
    ap.add_argument('--output',type=Path,default=Path('fv-ex2-local-qa'))
    ap.add_argument('--audit',type=Path,default=Path(__file__).with_name('verify_integrated_playground.py'))
    ap.add_argument('--axe',type=Path,help='Official local axe-core JS; missing blocks WCAG gate')
    ap.add_argument('--port',type=int,default=9400)
    ap.add_argument('--timeout',type=int,default=60)
    ap.add_argument('--preflight-only',action='store_true')
    args=ap.parse_args(argv)
    try:
        pins=attest(args.bundle)
        args.output.mkdir(parents=True,exist_ok=True)
        (args.output/'source_preflight.json').write_text(json.dumps(pins,indent=2)+'\n')
        if args.preflight_only:
            print(json.dumps({'status':'SOURCE_ONLY_PASS','wordpress':'NOT_TESTED','release':'HOLD',**pins}))
            return 0
        report=execute(args.bundle,args.output,args.audit,args.axe,args.port,args.timeout)
        print(json.dumps({'status':report['wordpress'],'error':report.get('error'),
                          'admission':report['admission'],'release':'HOLD'}))
        return 2 if report['wordpress']=='NOT_VERIFIED' else 1
    except Exception as exc:
        print(json.dumps({'status':'BLOCKED','reason':type(exc).__name__+': '+str(exc),'release':'HOLD'}))
        return 2

if __name__=='__main__':
    raise SystemExit(main())
