#!/usr/bin/env python3
"""R176: isolated native Preparedness checks; a green test run is never a release gate.

Copies only the Preparedness tree into a disposable directory, runs existing
validation, WordPress draft generation, full tests, and R174/R175 structural
review gates. It never invokes WordPress or the network. Report states are
DRAFT_HARD_HOLD or INVALID_HARD_HOLD, and CLI always exits code 2.
This is a diagnostic harness, not a security sandbox against malicious scripts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

SCHEMA = 'fv-preparedness-r176-native-review-preflight-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
COMMANDS = (
    ('validate', ('preparedness/tools/validate.py',)),
    ('build', ('preparedness/tools/build.py',)),
    ('unit_tests', ('-m', 'unittest', 'discover', '-s', 'preparedness/tests', '-v')),
    ('r174_citations', ('preparedness/tools/r174_rendered_citation_gate.py', '--repo', '.', '--check-export')),
    ('r175_links', ('preparedness/tools/r175_link_custody_gate.py', '--repo', '.', '--check-export')),
)
NEEDED = (
    'tools/validate.py', 'tools/build.py',
    'tools/r174_rendered_citation_gate.py', 'tools/r175_link_custody_gate.py',
    'docs/r151/contributor-three-way.json', 'docs/r161/body_custody.json',
    'sources/register.json', 'sources/crosswalk.json',
    'taxonomy.json', 'assets/preparedness.css',
)
TEST_SUMMARY = re.compile(r'^Ran (\d+) tests? in \d+(?:\.\d+)?s?\s*$', re.M)
SKIPPED = re.compile(r'\bskipped=(\d+)\b')


def require(ok: object, message: str) -> None:
    if not ok:
        raise ValueError(message)


def inventory(preparedness: Path) -> dict[str, str]:
    """Snapshot source inputs only, excluding generated and transient caches."""
    require(preparedness.is_dir() and not preparedness.is_symlink(), 'missing or symlinked preparedness directory')
    items: dict[str, str] = {}
    for path in sorted(preparedness.rglob('*')):
        relative = path.relative_to(preparedness)
        if 'build' in relative.parts or '__pycache__' in relative.parts:
            continue
        require(not path.is_symlink(), 'symlinked input: ' + str(relative))
        if path.is_file():
            require(path.stat().st_size <= 8_000_000, 'oversize input: ' + str(relative))
            items[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            require(path.is_dir(), 'unsupported input: ' + str(relative))
    for required in NEEDED:
        require(required in items, 'missing essential input: ' + required)
    metas = sorted(p for p in items if re.fullmatch(r'content/articles/[a-z0-9-]+\.meta\.json',p))
    bodies = sorted(p for p in items if re.fullmatch(r'content/articles/[a-z0-9-]+\.body\.html',p))
    require(len(metas) == len(bodies) == 35, '35-article census not present')
    require({p.removesuffix('.meta.json') for p in metas} ==
            {p.removesuffix('.body.html') for p in bodies}, 'unpaired article input')
    return items


def run_command(label: str, args: tuple[str, ...], root: Path, timeout: int) -> dict:
    env = {key: value for key,value in os.environ.items()
           if key not in ('PYTHONPATH','PYTHONSTARTUP','PYTHONHOME')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['PYTHONNOUSERSITE'] = '1'
    try:
        proc = subprocess.run([sys.executable, '-I', *args], cwd=root,
                              env=env, text=True, encoding='utf-8', errors='replace',
                              capture_output=True, timeout=timeout, check=False)
        return {'step': label, 'returncode': proc.returncode,
                'stdout': proc.stdout, 'stderr': proc.stderr}
    except subprocess.TimeoutExpired:
        return {'step': label, 'returncode': None, 'stdout': '',
                'stderr': 'TIMEOUT'}
    except OSError as exc:
        return {'step': label, 'returncode': None, 'stdout': '',
                'stderr': 'EXECUTION ERROR: ' + type(exc).__name__}


def assess(step: dict, staged: Path) -> dict:
    """Fail closed: expected *exit 2* for review gates, never a publish PASS."""
    label, code = step['step'], step['returncode']
    stdout, stderr = step['stdout'], step['stderr']
    receipt = {'step': label, 'returncode': code,
               'stdout_sha256': hashlib.sha256(stdout.encode()).hexdigest(),
               'stderr_sha256': hashlib.sha256(stderr.encode()).hexdigest(),
               'status': 'FAIL'}
    if label == 'validate':
        if code == 0 and re.search(r'\b0 error\(s\)', stdout):
            receipt['status'] = 'CHECKED'
        else:
            receipt['reason'] = 'validator failed, missing zero-error summary or was interrupted'
    elif label == 'build':
        wp = staged / 'preparedness/build/wp'
        preview = staged / 'preparedness/build/preview'
        wp_count = len(list(wp.glob('*.html'))) if wp.is_dir() else 0
        preview_count = len(list(preview.glob('*.html'))) if preview.is_dir() else 0
        receipt['wp_drafts'] = wp_count
        receipt['preview_drafts'] = preview_count
        if code == 0 and wp_count >= 35 and preview_count >= 35 and all(
                p.is_file() and not p.is_symlink() for p in list(wp.glob('*.html'))+list(preview.glob('*.html'))):
            receipt['status'] = 'CHECKED'
        else:
            receipt['reason'] = 'build missing 35+ WP drafts/previews or failed'
    elif label == 'unit_tests':
        m = TEST_SUMMARY.search(stderr + '\n' + stdout)
        skipped = max([int(x) for x in SKIPPED.findall(stderr + '\n' + stdout)] or [0])
        count = int(m.group(1)) if m else 0
        receipt['tests_reported'] = count
        receipt['skipped_reported'] = skipped
        if code == 0 and count >= 36 and count - skipped >= 36 and 'FAILED (' not in stderr:
            receipt['status'] = 'CHECKED'
        else:
            receipt['reason'] = 'suite failed, missing summary, or fewer than 36 tests actually executed'
    elif label in ('r174_citations', 'r175_links'):
        try:
            document = json.loads(stdout.strip())
            n = document.get('article_count') if label == 'r174_citations' else document.get('articles')
            counts = (document.get('rendered_citations') == 2000 and
                      document.get('rendered_source_uses') == 385) if label == 'r174_citations' else True
            allowed = code == 2 and document.get('state') == HOLD and n == 35 and counts
            # Any positive release/verification flag invalidates the receipt.
            flags = ('publication_authorized', 'independent_qd_pass', 'food_safety_approved',
                     'medical_food_safety_approved', 'qualified_source_review',
                     'independent_source_review', 'commercial_offer_verified')
            allowed = allowed and document.get('publication_authorized') is False
            allowed = allowed and all(document.get(k) is not True for k in flags)
            allowed = allowed and document.get('export_compared' if label == 'r175_links' else
                                               'draft_export_bytes_checked') is True
            if allowed:
                receipt['status'] = 'STRUCTURAL_HOLD'
                receipt['gate_state'] = HOLD
            else:
                receipt['reason'] = 'unexpected exit, corpus mismatch, false approval, or bad structural hold'
        except (ValueError, TypeError, AttributeError):
            receipt['reason'] = 'missing/malformed review gate JSON'
    else:
        receipt['reason'] = 'unknown preflight step'
    return receipt


def preflight(root: Path, *, timeout: int = 300) -> dict:
    """Run against a disposable copy. Never mutate the actual repository."""
    result = {'schema': SCHEMA, 'state': INVALID, 'publication_authorized': False,
              'independent_qd_pass': False, 'human_safety_review_complete': False,
              'merchant_sale_verified': False, 'checks': []}
    try:
        require(10 <= timeout <= 1200, 'timeout must be between 10 and 1200 seconds')
        require(root.is_dir() and not root.is_symlink(), 'missing or symlinked repository')
        source = root / 'preparedness'
        before = inventory(source)
        digest = hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
        result['input_manifest_sha256'] = digest
        result['article_input_pairs'] = 35
        with tempfile.TemporaryDirectory(prefix='fv-prep-r176-') as tmp:
            staged = Path(tmp)
            shutil.copytree(source, staged/'preparedness', ignore=shutil.ignore_patterns(
                'build', '__pycache__', '*.pyc'), symlinks=False)
            require(inventory(staged/'preparedness') == before,
                    'source copy differs from inspected originals')
            for label, args in COMMANDS:
                step = run_command(label, args, staged, timeout)
                result['checks'].append(assess(step, staged))
            require(inventory(staged/'preparedness') == before,
                    'native checks unexpectedly changed staged source inputs')
        require(inventory(source) == before, 'native checks changed source repository inputs')
        result['state'] = HOLD if all(x['status'] in ('CHECKED','STRUCTURAL_HOLD')
                                      for x in result['checks']) else INVALID
        if result['state'] == INVALID:
            result['blocker'] = 'one or more native checks failed; inspect exact checkout locally'
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result['blocker'] = str(exc)
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, default=Path('.'))
    ap.add_argument('--timeout', type=int, default=300)
    args = ap.parse_args(argv)
    print(json.dumps(preflight(args.repo, timeout=args.timeout), sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
