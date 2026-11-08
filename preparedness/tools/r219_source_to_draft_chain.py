#!/usr/bin/env python3
"""R219: read-only, fail-closed integration of the R214 -> R215 -> R216 -> R218
citation-exception WordPress draft guards. This is NOT a release approval.

Only Articles 7 and 20 are covered. This program does not adjudicate citations,
replace native validation/build, or authorize publication or commerce.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r219-source-to-draft-chain-v1'
PINS = {
    'r215_wp_claim_transport_gate.py': '1cd0d239dfcf2b91ff70dca33c3b93cd9a3b55c1',
    'r216_draft_exposure_guard.py': '6918b0ebfd3b73bcf513eb29ab352b4d94ca5060',
    'r217_transport_semantics_guard.py': 'abefe8954e6dcd8f609db4359586120360828acd',
}
ARTICLES = (7, 20)
TRANSPORTS = ((7, 'wp'), (7, 'preview'), (20, 'wp'), (20, 'preview'))


def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def invalid(message: str) -> dict:
    return {'schema': SCHEMA, 'state': INVALID, 'errors': [str(message)],
            'stages': [], 'articles': [], 'transports': [],
            'independent_qd_pass': False, 'publication_authorized': False,
            'medical_safety_verified': False, 'source_claim_review': 'REQUIRED',
            'issue': 136, 'conversion_issue': 820}


def strict_json(raw: bytes) -> dict:
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError('duplicate JSON key: ' + key)
            out[key] = value
        return out
    def nonfinite(value):
        raise ValueError('nonfinite JSON value: ' + value)
    item = json.loads(raw.decode('utf-8', 'strict'), object_pairs_hook=unique,
                      parse_constant=nonfinite)
    if type(item) is not dict:
        raise ValueError('report must be a JSON object')
    return item


def load_stages(directory: Path) -> dict:
    """Load exactly three SHA-pinned local guard modules, never from arbitrary PATH."""
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('unsafe stage source directory')
    stages = {}
    for index, (name, expected) in enumerate(PINS.items()):
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('missing or symlinked stage: ' + name)
        if blob(path.read_bytes()) != expected:
            raise ValueError('unreviewed stage source identity: ' + name)
        spec = importlib.util.spec_from_file_location('fv_r219_stage_' + str(index), path)
        if spec is None or spec.loader is None:
            raise ValueError('cannot load stage ' + name)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        stages[name] = mod
    return stages


def _held(report, schema: str, flags=('independent_qd_pass', 'publication_authorized',
                                     'medical_safety_verified')):
    if (type(report) is not dict or report.get('schema') != schema or
            report.get('state') != HOLD or report.get('errors') != []):
        raise ValueError('incorrect schema, state, or errors: ' + schema)
    for flag in flags:
        if report.get(flag) is not False:
            raise ValueError('non-false or absent release flag: ' + flag)
    if report.get('issue') != 136 or report.get('conversion_issue') != 820:
        raise ValueError('governing issue references changed')


def _inputs(dossier: dict, originals: dict, rendered: dict):
    _held(dossier, 'fv-preparedness-r214-complete-claim-block-v1',
          ('human_claim_verified', 'medical_safety_verified', 'independent_qd_pass',
           'publication_authorized'))
    claims = dossier.get('claims')
    if type(claims) is not list or [c.get('article') for c in claims if type(c) is dict] != [7, 7, 20] or len(claims) != 3:
        raise ValueError('exact three ordered held citation claims required')
    if type(originals) is not dict or set(originals) != set(ARTICLES):
        raise ValueError('exact original bodies 7 and 20 required')
    if type(rendered) is not dict or set(rendered) != set(ARTICLES):
        raise ValueError('exact held render article set required')
    hashes = {}
    for article in ARTICLES:
        original = originals[article]
        if type(original) is not bytes or not original or len(original) > 5_000_000:
            raise ValueError('invalid original body bytes')
        hashes[article] = blob(original)
        if type(rendered[article]) is not dict or set(rendered[article]) != {'wp', 'preview'}:
            raise ValueError('both WP and preview outputs required')
        for mode in ('wp', 'preview'):
            raw = rendered[article][mode]
            if type(raw) is not bytes or not raw or len(raw) > 5_000_000:
                raise ValueError('invalid draft bytes')
    receipts = set()
    for claim in claims:
        n = claim['article']; original = originals[n]
        span = claim.get('citation_span_bytes')
        block_span = claim.get('claim_block_span_bytes')
        if (claim.get('body_git_blob_sha1') != hashes[n] or
                type(span) is not list or len(span) != 2 or
                type(block_span) is not list or len(block_span) != 2 or
                any(type(x) is not int for x in span + block_span)):
            raise ValueError('claim original identity or span mismatch')
        start, stop = span; block_start, block_stop = block_span
        if not 0 <= block_start <= start < stop <= block_stop <= len(original):
            raise ValueError('claim span is outside original body')
        sid = claim.get('source_id')
        if type(sid) is not str or re.fullmatch(r'[a-z0-9-]+', sid) is None:
            raise ValueError('invalid source id')
        if original[start:stop] != ('{{cite:' + sid + '}}').encode('ascii'):
            raise ValueError('original citation bytes changed')
        if digest(original[block_start:block_stop]) != claim.get('raw_claim_block_sha256'):
            raise ValueError('citation claim block digest drift')
        if (type(claim.get('source_url')) is not str or
            not claim['source_url'].startswith('https://') or
            claim.get('human_source_claim_review') != 'REQUIRED' or
            claim.get('editorial_decision') != 'PENDING'):
            raise ValueError('unsupported citation source/review state')
        for field in ('receipt_sha256', 'visible_claim_sha256'):
            if re.fullmatch(r'[0-9a-f]{64}', str(claim.get(field))) is None:
                raise ValueError('invalid claim fingerprint: ' + field)
        if digest(claim.get('visible_claim_text', '').encode('utf-8')) != claim['visible_claim_sha256']:
            raise ValueError('visible claim digest changed')
        receipt = claim['receipt_sha256']
        if receipt in receipts:
            raise ValueError('duplicate citation receipt')
        receipts.add(receipt)
    return hashes


def _stage_rows(report, kind: str, originals: dict, rendered: dict):
    if kind == 'r215':
        rows = report.get('articles')
        if type(rows) is not list or len(rows) != 2 or [x.get('article') for x in rows if type(x) is dict] != [7, 20]:
            raise ValueError('R215 article receipts not in 7,20 order')
        for row in rows:
            n = row['article']
            if row.get('original_blob_sha1') != blob(originals[n]) or row.get('source_review') != 'REQUIRED':
                raise ValueError('R215 original/source identity drift')
            if type(row.get('citation_occurrences')) is not int or row['citation_occurrences'] < 1:
                raise ValueError('R215 citation count invalid')
            if row.get('render_sha256') != {c: digest(rendered[n][c]) for c in ('wp','preview')}:
                raise ValueError('R215 rendered SHA receipt drift')
    else:
        rows = report.get('transports')
        if type(rows) is not list or len(rows) != 4 or [
            (x.get('article'), x.get('channel')) for x in rows if type(x) is dict
        ] != list(TRANSPORTS):
            raise ValueError('R216/R217 four transport receipts reordered or missing')
        for row in rows:
            n, channel = row['article'], row['channel']
            if row.get('sha256') != digest(rendered[n][channel]):
                raise ValueError('rendered transport identity changed: ' + str((n, channel)))
            if kind == 'r216' and row.get('exposure_gate') != HOLD:
                raise ValueError('R216 exposure classification changed')
            if kind == 'r217' and (row.get('gate') != HOLD or row.get('attributes_and_fragments_checked') is not True):
                raise ValueError('R217 semantics classification changed')


def evaluate(dossier: dict, originals: dict, rendered: dict, *, stages=None) -> dict:
    """Unconditionally hold: even every successful stage does not grant release."""
    try:
        hashes = _inputs(dossier, originals, rendered)
        if stages is None:
            stages = load_stages(Path(__file__).resolve().parent)
        if type(stages) is not dict or set(stages) != set(PINS):
            raise ValueError('missing or unauthorized guarded stage')
        p215, p216, p217 = [stages[key] for key in PINS]
        first = p215.evaluate(dossier, originals, rendered)
        _held(first, 'fv-preparedness-r215-wp-draft-transport-v1')
        if first.get('human_source_claim_review') != 'REQUIRED':
            raise ValueError('R215 human review state not REQUIRED')
        _stage_rows(first, 'r215', originals, rendered)
        second = p216.evaluate(first, rendered)
        _held(second, 'fv-preparedness-r216-draft-exposure-v1')
        if second.get('source_claim_review') != 'REQUIRED':
            raise ValueError('R216 review state not REQUIRED')
        _stage_rows(second, 'r216', originals, rendered)
        third = p217.evaluate(second, rendered)
        _held(third, 'fv-preparedness-r217-transport-semantics-v1')
        if third.get('source_claim_review') != 'REQUIRED':
            raise ValueError('R218 underlying R217 review state not REQUIRED')
        _stage_rows(third, 'r217', originals, rendered)
        return {'schema': SCHEMA, 'state': HOLD, 'errors': [],
                'stages': [first['schema'], second['schema'], third['schema']],
                'articles': [{'article': n, 'original_blob_sha1': hashes[n]} for n in ARTICLES],
                'transports': [{'article': n, 'channel': c, 'sha256': digest(rendered[n][c])}
                               for n, c in TRANSPORTS],
                'independent_qd_pass': False, 'publication_authorized': False,
                'medical_safety_verified': False, 'source_claim_review': 'REQUIRED',
                'issue': 136, 'conversion_issue': 820}
    except (ValueError, TypeError, KeyError, AttributeError, UnicodeError, OSError, ImportError) as exc:
        return invalid(str(exc))


def _safe_read(path: Path, root: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing or symlinked input: ' + str(path))
    if root not in path.resolve().parents:
        raise ValueError('input escapes trusted root: ' + str(path))
    if any(parent.is_symlink() for parent in path.parents if parent != root and root in parent.parents):
        raise ValueError('symlinked input ancestor: ' + str(path))
    return path.read_bytes()


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description='R219 READ ONLY WordPress draft safety chain, HOLD/INVALID only')
    p.add_argument('--root', type=Path, required=True, help='absolute trusted root containing the input snapshots')
    for name in ('r214-report', 'original7', 'original20', 'wp7', 'preview7', 'wp20', 'preview20'):
        p.add_argument('--' + name, type=Path, required=True)
    args = p.parse_args(argv)
    try:
        root = args.root
        if root.is_symlink() or not root.is_absolute() or not root.is_dir():
            raise ValueError('trusted root must be an absolute, non-symlink directory')
        base = root.resolve()
        inputs = {name: _safe_read(getattr(args, name.replace('-', '_')), base)
                  for name in ('r214-report', 'original7', 'original20', 'wp7', 'preview7', 'wp20', 'preview20')}
        dossier = strict_json(inputs['r214-report'])
        originals = {n: inputs['original' + str(n)] for n in ARTICLES}
        rendered = {n: {c: inputs[c + str(n)] for c in ('wp', 'preview')} for n in ARTICLES}
        report = evaluate(dossier, originals, rendered)
    except (ValueError, TypeError, KeyError, AttributeError, UnicodeError, OSError, ImportError) as exc:
        report = invalid('read-only input error: ' + str(exc))
    print(json.dumps(report, sort_keys=True, indent=2))
    return 2 if report['state'] == HOLD else 3


if __name__ == '__main__':
    raise SystemExit(main())
