#!/usr/bin/env python3
"""Fail-closed one-command admission of the seven-chapter Final Vestige homepage.

This is a LOCAL DEVELOPER TOOL. It does not write WordPress.com, deploy, or merge.
The only network destination this program probes is the 127.0.0.1/localhost
Playground server intentionally launched by the operator. No cookies or
browser storage-state contents are recorded in receipts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import urlsplit
import urllib.error
import urllib.request

REPO_HOME = Path('experience2/home-flagship')
PREP = REPO_HOME / 'qa/playground/prepare_isolated_stage.py'
BINDER = REPO_HOME / 'qa/playground/parity/prepare_unified_playground.py'
CSP_GATE = REPO_HOME / 'qa/release-candidate/verify_csp_exact_browser.py'
STAGE_GATE = REPO_HOME / 'qa/release-candidate/verify_exact_staging.py'
ENTRY = REPO_HOME / 'qa/playground/parity/run_local_staging_admission.py'
ENTRY_TEST = REPO_HOME / 'qa/playground/parity/test_run_local_staging_admission.py'
ASSET_NAMES = ('index.html', 'flagship.css', 'chronicle.css','chronicle-lens.css',
               'inquiry.css', 'observer-lab.css', 'reading-trail.css',
               'flagship.js','observer-lab.js','chronicle-lens.js','reading-trail.js')
MAX_READY_SECONDS = 90

class GateError(RuntimeError):
    """Expected blocked or safety-gated result."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n', encoding='utf8')
    temp.replace(path)


def valid_local_url(url: str) -> str:
    p = urlsplit(url)
    if (p.scheme != 'http' or p.hostname not in ('localhost','127.0.0.1')
        or p.username or p.password or p.fragment or p.query
        or p.path not in ('', '/') or p.port != 9400):
        raise GateError('REFUSED: admission may contact only http://127.0.0.1:9400/')
    return 'http://127.0.0.1:9400/'


def ensure_safe_paths(repo: Path, stage: Path, theme: Path, out: Path, storage: Path | None) -> tuple[Path,Path,Path,Path]:
    repo = repo.resolve(strict=True)
    if not (repo / '.git').exists():
        raise GateError('REFUSED: exact complete Git checkout required')
    if theme.is_symlink():
        raise GateError('REFUSED: official Assembler archive path may not be a symlink')
    theme = theme.resolve(strict=True)
    if not theme.is_file():
        raise GateError('REFUSED: pinned official Assembler ZIP must be a regular file')
    if stage.is_symlink() or out.is_symlink():
        raise GateError('REFUSED: staging or receipt root may not be a symlink')
    stage = stage.resolve(strict=False)
    out = out.resolve(strict=False)
    for name,p in [('stage',stage),('receipts',out)]:
        if p == repo or repo in p.parents or p in repo.parents or p.is_symlink():
            raise GateError(f'REFUSED: {name} must be a distinct directory outside the checkout')
    if stage == out or stage in out.parents or out in stage.parents:
        raise GateError('REFUSED: staging and receipt directories must be independent')
    if storage is not None:
        storage = storage.resolve(strict=True)
        if not storage.is_file() or storage == out or out in storage.parents or repo in storage.parents:
            raise GateError('REFUSED: credentials must live in a separate private local file outside checkout/receipts')
        if os.name != 'nt' and storage.stat().st_mode & 0o077:
            raise GateError('REFUSED: browser storage state needs chmod 600')
    return repo,stage,theme,out


def exact_source(repo: Path, expected: str, theme: Path, theme_sha256: str) -> dict:
    if not re.fullmatch('[0-9a-f]{40}', expected):
        raise GateError('REFUSED: expected Git HEAD must be exactly 40 hexadecimal characters')
    if not re.fullmatch('[0-9a-f]{64}', theme_sha256):
        raise GateError('REFUSED: official theme archive needs independently recorded SHA-256')
    if digest(theme) != theme_sha256:
        raise GateError('REFUSED: Assembler archive checksum differs from independent pin')
    try:
        actual = subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    except subprocess.CalledProcessError as e:
        raise GateError('REFUSED: not a valid complete Git checkout') from e
    if actual != expected:
        raise GateError('REFUSED: checked-out HEAD does not equal exact expected Git commit')
    assets = {}
    for rel in [REPO_HOME / x for x in ASSET_NAMES] + [PREP,BINDER,CSP_GATE,STAGE_GATE,ENTRY,ENTRY_TEST]:
        p = repo / rel
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(repo):
            raise GateError('REFUSED: canonical source unavailable or symlink: '+str(rel))
        recorded = subprocess.run(['git','-C',str(repo),'show',expected+':'+rel.as_posix()],
                                  capture_output=True)
        if recorded.returncode or recorded.stdout != p.read_bytes():
            raise GateError('REFUSED: exact committed bytes differ for '+str(rel))
        assets[str(rel)] = digest(p)
    return assets


def command(repo: Path, args: list[str], receipt: dict, label: str, timeout: int = 150) -> None:
    run = subprocess.run(args,cwd=repo,text=True,capture_output=True,timeout=timeout)
    # Never dump raw stderr/stdout to shared receipts; CLI tools can log secrets.
    receipt['gates'][label] = {'exit_code':run.returncode, 'result':'PASS' if run.returncode==0 else 'FAIL'}
    if run.returncode:
        raise GateError(f'{label} failed (exit {run.returncode}); inspect local terminal output securely')


def kit_contract(stage: Path) -> list[str]:
    p = stage / 'playground-cli-arguments.json'
    bp = stage / 'playground-blueprint.json'
    receipt_path = stage / 'STAGING_PREP_RECEIPT.json'
    for file in (p,bp,receipt_path):
        if file.is_symlink() or not file.is_file():
            raise GateError('REFUSED: staged kit missing '+file.name)
    args = json.loads(p.read_text())
    receipt = json.loads(receipt_path.read_text())
    blueprint = json.loads(bp.read_text())
    if not isinstance(args,list) or args[:3] != ['npx','@wp-playground/cli@latest','server']:
        raise GateError('REFUSED: unknown Playground program')
    expected = {'--mount='+str(stage/'mounts'/name)+':'+dest for name,dest in (
        ('assembler','/wordpress/wp-content/themes/assembler'),
        ('fv-ex2-private-preview','/wordpress/wp-content/plugins/fv-ex2-private-preview'),
        ('fv-ex2-parity','/wordpress/wp-content/uploads/fv-ex2-parity'))}
    mounts = [x for x in args if isinstance(x,str) and x.startswith('--mount=')]
    if set(mounts)!=expected or len(mounts)!=3:
        raise GateError('REFUSED: unexpected staging mounts')
    flags = set(args[3:]) - set(mounts)
    if flags != {'--port=9400','--blueprint='+str(bp)} or len(args)!=8:
        raise GateError('REFUSED: unapproved WordPress CLI option')
    if receipt.get('release') != 'HOLD':
        raise GateError('REFUSED: release state must remain HOLD')
    steps = blueprint.get('steps')
    if not isinstance(steps,list) or len(steps)!=5 or not all(isinstance(step,dict) for step in steps) or [step.get('step') for step in steps] != [
            'defineWpConfigConsts','activateTheme','runPHP','activatePlugin','runPHP']:
        raise GateError('REFUSED: missing, changed or extra Playground execution steps')
    if (steps[0].get('consts') != {'WP_ENVIRONMENT_TYPE':'local','FV_EX2_ALLOW_PREVIEW':True}
        or steps[1].get('themeFolderName') != 'assembler'
        or steps[3].get('pluginPath') != '/wordpress/wp-content/plugins/fv-ex2-private-preview/fv-ex2-private-preview.php'
        or 'fv-ex2-parity/apply_local_parity.php' not in steps[2].get('code','')
        or 'fv-ex2-playground-review' not in steps[4].get('code','')):
        raise GateError('REFUSED: Blueprint local-only preview contract changed')
    return args


def readonly_probe(url: str, timeout: float = 2) -> dict:
    url = valid_local_url(url)
    class NeverRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise GateError('REFUSED: unexpected local preview redirect')
    opener = urllib.request.build_opener(NeverRedirect, urllib.request.ProxyHandler({}))
    try:
        with opener.open(url, timeout=timeout) as r:
            head = r.read(2048)
            return {'http_status':r.status,'sample_bytes':len(head),'wordpress_html':b'wp-' in head.lower() or b'wordpress' in head.lower()}
    except urllib.error.HTTPError as error:
        return {'http_status':error.code,'wordpress_html':False,'sample_bytes':0}


def wait_local_origin(url: str, process, limit_seconds: int = MAX_READY_SECONDS, now=time.monotonic, sleep=time.sleep) -> dict:
    deadline=now()+limit_seconds
    while now() < deadline:
        if process.poll() is not None:
            raise GateError('REFUSED: local Playground exited before HTTP readiness')
        try:
            found = readonly_probe(url)
            if found['http_status'] == 200:
                return found
        except (OSError,urllib.error.URLError):
            pass
        sleep(1)
    raise GateError('REFUSED: local Playground HTTP readiness timed out')


def run(args: argparse.Namespace) -> tuple[int,dict]:
    receipt = {'tool':'fv-ex2-one-command-local-admission-v1','expected_head':args.expected_head,
               'release':'HOLD','production_writes':False,'gates':{},
               'word_press_local':'NOT_RUN','archival_bytes':'NOT_MEASURED',
               'axe':'NOT_RUN','lighthouse':'NOT_RUN','word_press_com_atomic_parity':'NOT_VERIFIED',
               'hosted_ci':'NOT_VERIFIED','independent_qd':'NOT_VERIFIED'}
    try:
        origin=valid_local_url(args.local_origin)
        repo,stage,theme,out=ensure_safe_paths(args.repo,args.stage,args.assembler_zip,args.output,args.storage_state)
        if stage.exists() and any(stage.iterdir()):
            raise GateError('REFUSED: stage directory already contains files; use a new empty directory')
        if out.exists() and any(out.iterdir()):
            raise GateError('REFUSED: receipt directory must start empty to avoid overwriting evidence')
        hashes=exact_source(repo,args.expected_head,theme,args.assembler_sha256)
        receipt['source_sha256']=hashes
        receipt['assembler_zip_sha256']=args.assembler_sha256
        receipt['gates']['exact_source']='PASS'
        offline=[sys.executable,str(repo/CSP_GATE),'--root',str(repo/REPO_HOME),
                 '--expected-head',args.expected_head,'--output',str(out/'offline-browser')]
        # Offline runner is the exact committed PR #252 Chromium script; fail closed if missing browser.
        command(repo,offline,receipt,'exact_csp_chromium',timeout=240)
        prep=[sys.executable,str(repo/PREP),'--repo',str(repo),'--expected-head',args.expected_head,
              '--assembler-zip',str(theme),'--expected-theme-sha256',args.assembler_sha256,
              '--out',str(stage)]
        command(repo,prep,receipt,'canonical_private_stage_build',timeout=180)
        bind=[sys.executable,str(repo/BINDER),'--repo',str(repo),'--expected-head',args.expected_head,
              '--prepared-stage',str(stage),'--assembler-zip',str(theme),
              '--assembler-sha256',args.assembler_sha256]
        command(repo,bind,receipt,'assembled_assembler_parity',timeout=180)
        launch_argv=kit_contract(stage)
        receipt['gates']['strict_cli_contract']='PASS'
        if not args.launch:
            receipt['word_press_local']='READY_TO_LAUNCH_NOT_STARTED'
            return 0,receipt
        if args.storage_state is None or args.axe_script is None:
            raise GateError('REFUSED: run with private --storage-state and local --axe-script for actual browser admission')
        # The actual binary is authorized only for localhost and no extra options.
        with (out/'local-playground.stdout.log').open('w') as std, (out/'local-playground.stderr.log').open('w') as err:
            process=subprocess.Popen(launch_argv,cwd=stage,stdout=std,stderr=err)
            try:
                found=wait_local_origin(origin,process,limit_seconds=args.ready_timeout)
                receipt['word_press_local']='HTTP_READY_NOT_CERTIFIED'
                receipt['local_http']=found
                page=origin+'?pagename=fv-ex2-playground-review'
                admit=[sys.executable,str(repo/STAGE_GATE),'--url',page,'--allow-host','127.0.0.1',
                       '--expected-head',args.expected_head,'--repo',str(repo),
                       '--storage-state',str(args.storage_state),'--axe-script',str(args.axe_script),
                       '--out',str(out/'real-wp-browser')]
                command(repo,admit,receipt,'authenticated_real_wordpress_browser',timeout=300)
                receipt['word_press_local']='BROWSER_ADMITTED_PENDING_MANUAL_QD'
            finally:
                process.terminate()
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill();process.wait(timeout=5)
        return 0,receipt
    except (GateError, OSError, ValueError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        receipt['refusal']=str(exc)
        receipt['word_press_local']='HOLD'
        return 2,receipt


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--expected-head',required=True)
    parser.add_argument('--assembler-zip',type=Path,required=True)
    parser.add_argument('--assembler-sha256',required=True)
    parser.add_argument('--stage',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--local-origin',default='http://127.0.0.1:9400/')
    parser.add_argument('--launch',action='store_true',help='Explicitly start local Playground and run private browser checks')
    parser.add_argument('--storage-state',type=Path,help='Local private Playwright editor auth file (never commit)')
    parser.add_argument('--axe-script',type=Path,help='Local axe-core script, required for launch admission')
    parser.add_argument('--ready-timeout',type=int,default=90)
    a=parser.parse_args()
    if a.ready_timeout<=0 or a.ready_timeout>300: parser.error('--ready-timeout must be 1..300 seconds')
    code,report=run(a)
    # This report intentionally contains no browser credentials, personal records, or raw response content.
    try:
        # A rejected output path never becomes a writable bypass of the gate.
        checked_out=a.output.resolve(strict=False)
        checked_repo=a.repo.resolve(strict=False)
        if (a.output.is_symlink() or checked_out==checked_repo
            or checked_repo in checked_out.parents or checked_out in checked_repo.parents):
            raise OSError('REFUSED: unsafe receipt destination')
        safe_json(a.output/'LOCAL_STAGE_ADMISSION_RECEIPT.json', report)
    except OSError as exc:
        print('HOLD: receipt not writable: '+str(exc),file=sys.stderr);return 2
    print(json.dumps({'release':'HOLD','state':report['word_press_local'],
                      'gates':report['gates'],'refusal':report.get('refusal'),
                      'receipt':str(a.output/'LOCAL_STAGE_ADMISSION_RECEIPT.json')}))
    return code

if __name__=='__main__':
    raise SystemExit(main())
