#!/usr/bin/env python3
"""Read-only R466: preserve independent QA #157 and fixture #169/#2205 outcomes.

A structural safety regression sentinel, NOT independent medical/emergency/QD approval.
Hard-holds any native checkout divergence; never writes source files or exports.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

# Frozen from GitHub R465 HEAD fdc2bbcd9883e0956679d35537302d46580a756c
# at inspection 2026-11-18. Git blob hashes are SHA1 of 'blob LEN\0' + raw bytes.
PINS = {
    'content/articles/household-emergency-plan.body.html': 'f81cd43516e8295104230412f18776919148f905',
    'content/articles/three-day-kit.body.html': '933f38ff3cd55a241cf9b392014fc52d4961e84f',
    'sources/fragments/start.json': '96140d6d1872588e5d20d9052445c9157e88934d',
    'taxonomy.json': '15c547bb3018ac182b12a51036389cfa39a59168',
    'tests/test_preparedness.py': 'c329f98e051d2aabe31a3343869b0fdac355b315',
}
START_HERE = ('household-emergency-plan', 'three-day-kit', 'go-bags', 'preparedness-real-households')
BAD_MEDICINE = ('discard all refrigerated medicines', 'stop taking', 'ration your medicine', 'medicine is safe')
BAD_POWER = ('switch off the main breaker for', 'switch off the main power', 'turn off the main breaker to')
METHODS = ('test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source',
           'test_register_fragments_cannot_duplicate_ids')


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def strict_json(raw: bytes, path: str, errors: list[str]):
    def unique(pairs):
        obj = {}
        for key, val in pairs:
            if key in obj:
                raise ValueError('duplicate JSON key: ' + key)
            obj[key] = val
        return obj
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
    except (ValueError, UnicodeError) as exc:
        errors.append(f'{path}: invalid or duplicate-key JSON: {exc}')
        return None


def fixture_writes_are_isolated(code: str) -> list[str]:
    errors = []
    try:
        module = ast.parse(code)
    except SyntaxError as exc:
        return [f'fixture: syntax error: {exc}']
    functions = {n.name: n for n in ast.walk(module)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for method in METHODS:
        node = functions.get(method)
        if not node:
            errors.append(f'fixture: missing test method {method}')
            continue
        txt = ast.get_source_segment(code, node) or ''
        if 'TemporaryDirectory(' not in txt or 'copytree(ROOT, sandbox' not in txt:
            errors.append(f'fixture:{method}: no isolated copy of source tree')
        if 'Library(root=sandbox)' not in txt:
            errors.append(f'fixture:{method}: source loader not bound to sandbox')
        sandbox_names = {'sandbox'}
        for n in ast.walk(node):
            if isinstance(n, ast.Assign):
                # Expand only assignments whose full value depends on an existing sandbox path.
                names = {x.id for x in ast.walk(n.value) if isinstance(x, ast.Name)}
                if names & sandbox_names and 'ROOT' not in names:
                    sandbox_names.update(x.id for t in n.targets for x in ast.walk(t)
                                         if isinstance(x, ast.Name))
        for n in ast.walk(node):
            if not isinstance(n, ast.Call) or not isinstance(n.func, ast.Attribute):
                continue
            if n.func.attr not in ('write_text', 'write_bytes', 'unlink', 'rename', 'replace', 'mkdir', 'touch'):
                continue
            receiver_names = {x.id for x in ast.walk(n.func.value) if isinstance(x, ast.Name)}
            if 'ROOT' in receiver_names or not receiver_names & sandbox_names:
                errors.append(f'fixture:{method}:{n.lineno}: write/delete target not proven sandbox-derived')
    return errors


def audit_payloads(files: dict[str, bytes], verify_pins: bool = True) -> list[str]:
    errors: list[str] = []
    for path, pin in PINS.items():
        raw = files.get(path)
        if raw is None:
            errors.append(f'missing original file: {path}')
        elif verify_pins and git_blob(raw) != pin:
            errors.append(f'original blob mismatch: {path}: {git_blob(raw)} != {pin}')
    if any(path not in files for path in PINS):
        return errors
    house = files['content/articles/household-emergency-plan.body.html'].decode('utf-8', 'replace').lower()
    meds = files['content/articles/three-day-kit.body.html'].decode('utf-8', 'replace').lower()
    source = strict_json(files['sources/fragments/start.json'], 'start.json', errors)
    taxonomy = strict_json(files['taxonomy.json'], 'taxonomy.json', errors)
    test_code = files['tests/test_preparedness.py'].decode('utf-8', 'replace')

    for needle in ('do not switch off the main breaker', 'refrigerator and freezer',
                   'smoke and carbon monoxide alarms', 'medical or safety-critical equipment'):
        if needle not in house:
            errors.append('household drill: safety-critical retention missing: ' + needle)
    for needle in BAD_POWER:
        if needle in house:
            errors.append('household drill: unsafe power-off instruction: ' + needle)
    for needle in ('do not stop, throw away or ration', 'prescriber or pharmacist',
                   'refrigerated medicine', 'replacement', 'if you are already in an outage'):
        if needle not in meds:
            errors.append('medication note: qualification missing: ' + needle)
    for needle in BAD_MEDICINE:
        if needle in meds:
            errors.append('medication note: unsafely broad statement: ' + needle)
    if isinstance(source, dict):
        rows = source.get('sources')
        if not isinstance(rows, list):
            errors.append('source fragment: missing sources array')
        else:
            red = [r for r in rows if isinstance(r, dict) and r.get('id') == 'start-redcross-older-adults']
            if len(red) != 1 or red[0].get('kind') != 'nonprofit' or red[0].get('publisher') != 'American Red Cross':
                errors.append('source fragment: Red Cross nonprofit identity and authority drift')
    if isinstance(taxonomy, dict):
        slate = taxonomy.get('slate')
        if not isinstance(slate, list) or len(slate) != 35:
            errors.append('taxonomy: requires exact 35-article slate')
        else:
            seen = [r.get('slug') for r in slate if isinstance(r, dict)]
            if len(set(seen)) != 35 or len(seen) != 35:
                errors.append('taxonomy: duplicate or missing slugs')
            for slug in START_HERE:
                matches = [r for r in slate if isinstance(r, dict) and r.get('slug') == slug]
                if len(matches) != 1 or matches[0].get('gate') is not True:
                    errors.append('taxonomy: Start Here gate missing: ' + slug)
                elif matches[0].get('status') == 'published':
                    errors.append('taxonomy: unreviewed Start Here published: ' + slug)
    errors.extend(fixture_writes_are_isolated(test_code))
    return errors


def audit_native(root: Path) -> dict:
    files = {}
    for rel in PINS:
        path = root / rel
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            continue
        files[rel] = path.read_bytes()
    errors = audit_payloads(files)
    return {'status': 'HARD_HOLD', 'scope': 'independent-QA absorption only',
            'checked': len(files), 'expected': len(PINS), 'errors': errors,
            'release_approval': False, 'human_safety_approved': False}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    report = audit_native(args.root)
    print(json.dumps(report, sort_keys=True, indent=2))
    # This isolated gate must never issue a publication PASS, even for intact drafts.
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
