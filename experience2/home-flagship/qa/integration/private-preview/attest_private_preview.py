#!/usr/bin/env python3
"""Bind the unpublished FV Experience 2.0 private-preview ZIP to an actual clean Git HEAD.

No staging installation, WordPress calls, release approval, or network required.
Exit nonzero if the caller-supplied SHA differs from repository HEAD, if a
bundled source/security file is uncommitted or altered, or if output diverges.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

HOME = Path('experience2/home-flagship')
PRIVATE = HOME / 'qa/integration/private-preview'
CONTRACT = HOME / 'qa/integration/check_contract.py'
SOURCE_MANIFEST = HOME / 'source-manifest.json'
EXTRA = [SOURCE_MANIFEST, CONTRACT, PRIVATE/'build_private_preview.py',
         PRIVATE/'fv-ex2-private-preview.php', PRIVATE/'attest_private_preview.py',
         HOME/'qa/release-candidate/source_gate.mjs']
EXPECTED_ASSETS = {'index.html', 'flagship.css', 'chronicle.css',
 'chronicle-lens.css', 'inquiry.css', 'observer-lab.css', 'reading-trail.css',
 'flagship.js', 'observer-lab.js', 'chronicle-lens.js', 'reading-trail.js'}


def git(repo: Path, *args: str) -> bytes:
    p = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if p.returncode: raise ValueError('Git failed: '+ ' '.join(args)+' - '+p.stderr.decode(errors='replace')[:200])
    return p.stdout


def read_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None: raise ValueError('Cannot load '+str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def attest(repo: Path, expected_head: str, output: Path) -> dict:
    repo = repo.resolve(strict=True)
    if not (len(expected_head) == 40 and all(c in '0123456789abcdef' for c in expected_head)):
        raise ValueError('Expected HEAD must be 40 lowercase hexadecimal digits')
    actual = git(repo, 'rev-parse', 'HEAD').decode().strip()
    if actual != expected_head:
        raise ValueError('SHA MISMATCH: actual Git HEAD '+actual+' differs from '+expected_head)
    # Verify scripts before importing/executing any checkout-controlled Python.
    paths = EXTRA + [HOME/a for a in sorted(EXPECTED_ASSETS)]
    verified = {}
    for relative in paths:
        f = repo / relative
        if f.is_symlink() or not f.is_file() or not f.resolve().is_relative_to(repo):
            raise ValueError('Unsafe/missing source file: '+str(relative))
        path = relative.as_posix()
        git(repo, 'ls-files', '--error-unmatch', '--', path)
        committed = git(repo, 'show', expected_head+':'+path)
        current = f.read_bytes()
        if committed != current:
            raise ValueError('DIRTY or mismatched checkout source: '+path)
        verified[path] = hashlib.sha256(current).hexdigest()
    contract = read_module(repo/CONTRACT, 'fv_ex2_attested_contract')
    assets = tuple(contract.ASSETS)
    if len(assets) != len(EXPECTED_ASSETS) or set(assets) != EXPECTED_ASSETS:
        raise ValueError('11-asset staging contract unexpectedly changed')
    # Run the canonical 19-check source/rights gate on the same clean SHA.
    with tempfile.TemporaryDirectory(prefix='fv-source-audit-') as audit_dir:
        audit_file = Path(audit_dir)/'source-gate.json'
        check = subprocess.run(['node', str(repo/HOME/'qa/release-candidate/source_gate.mjs'),
            '--root', str(repo/HOME), '--expected-head', actual, '--report',str(audit_file)],
            cwd=repo,capture_output=True,text=True)
        if check.returncode or not audit_file.is_file():
            raise ValueError('Canonical Node source gate failed: '+(check.stderr or check.stdout)[:300])
        source_report = json.loads(audit_file.read_text())
        if source_report.get('source',{}).get('status') != 'PASS' or source_report.get('release',{}).get('status') != 'HOLD':
            raise ValueError('Canonical Node source gate did not return SOURCE PASS / RELEASE HOLD')
    builder = read_module(repo/PRIVATE/'build_private_preview.py', 'fv_ex2_attested_builder')
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='fv-preview-attested-') as td:
        one = Path(td)/'one.zip'; two = Path(td)/'two.zip'
        for target in (one, two):
            builder.create(repo/HOME, repo/PRIVATE/'fv-ex2-private-preview.php',
                           target, actual, contract)
        data1, data2 = one.read_bytes(), two.read_bytes()
        if data1 != data2: raise ValueError('Build not reproducible byte-for-byte')
        with zipfile.ZipFile(one) as package:
            names = set(package.namelist())
            prefix = 'fv-ex2-private-preview/'
            wanted = {prefix+x for x in ('fv-ex2-private-preview.php',
                'fv-ex2-private-payload.php', 'STAGING_MANIFEST.json',
                'INSTALLATION_HOLD.txt')}
            if names != wanted: raise ValueError('Unexpected ZIP files '+str(names ^ wanted))
            manifest = json.loads(package.read(prefix+'STAGING_MANIFEST.json'))
            if manifest['expected_git_head_given_by_caller'] != actual:
                raise ValueError('Archive claims incorrect HEAD')
            sha = {name: verified[(HOME/name).as_posix()] for name in assets}
            if manifest['source_hashes'] != sha: raise ValueError('ZIP source hashes differ from Git HEAD')
            if package.read(prefix+'fv-ex2-private-preview.php') != (repo/PRIVATE/'fv-ex2-private-preview.php').read_bytes():
                raise ValueError('Plugin source differs')
            if manifest['payload_sha256'] != hashlib.sha256(package.read(prefix+'fv-ex2-private-payload.php')).hexdigest():
                raise ValueError('Payload hash differs')
            if manifest['release_status'] != 'HOLD_UNPUBLISHED_STAGING_ONLY':
                raise ValueError('Release HOLD not maintained')
        output.write_bytes(data1)
    return {'status':'ATTESTED_SOURCE_ONLY_RELEASE_HOLD', 'git_head':actual,
            'source_files_verified':len(paths), 'source_sha256':verified,
            'canonical_source_gate':'PASS', 'canonical_source_gate_release':'HOLD',
            'source_asset_count':len(assets), 'deterministic_rebuild':True,
            'zip_path':str(output), 'zip_bytes':output.stat().st_size,
            'zip_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'staging':'NOT INSTALLED', 'word_press_qa':'NOT PERFORMED',
            'lighthouse_cwv':'NOT MEASURED', 'media_rights':'PENDING',
            'independent_ci_qd':'PENDING', 'production_release':'HOLD'}


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,required=True)
    ap.add_argument('--expected-head',required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    args=ap.parse_args()
    try:
        receipt=attest(args.repo,args.expected_head,args.out)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({k:v for k,v in receipt.items() if k != 'source_sha256'},indent=2))
        return 0
    except Exception as exc:
        print('ATTESTATION FAILED CLOSED: '+str(exc),file=sys.stderr)
        return 2

if __name__=='__main__': sys.exit(main())
