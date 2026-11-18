#!/usr/bin/env python3
"""R465 original Shelter body/metadata pair custody. Read-only, never QD approval.

Uses frozen R464 body Git blobs and new independently fetched metadata Git blobs.
Checks actual literal citation tokens against every variant's authored source_use,
retains original reading scopes, and stops if the candidate drops/rewrites one.
R465 does not select a version or decide if source-backed advice is safe.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

HOLD = 'DRAFT_HARD_HOLD'
SLUGS = ('family-communication-plan', 'home-fire-escape-plan',
         'outage-heat-cold-generators', 'shelter-or-evacuate')
VARIANTS = ('original', 'continuation', 'followup', 'candidate')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
SHA = re.compile(r'[0-9a-f]{40}\Z')

class PairHold(ValueError):
    pass

def check(ok, msg):
    if not ok:
        raise PairHold(msg)

def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        check(key not in result, 'duplicate JSON property: ' + key)
        result[key] = value
    return result

def decode_metadata(raw):
    check(isinstance(raw, bytes) and 0 < len(raw) < 150000, 'missing/oversized metadata')
    try:
        return json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs)
    except (UnicodeError, json.JSONDecodeError) as ex:
        raise PairHold('invalid UTF8/JSON metadata') from ex

def inspect_pair(slug, variant, body, metadata, body_sha, meta_sha):
    check(slug in SLUGS and variant in VARIANTS, 'unrecognized article or version')
    check(isinstance(body, bytes) and 0 < len(body) < 250000, 'missing/oversized body')
    for label, raw, pin in (('body', body, body_sha), ('metadata', metadata, meta_sha)):
        check(isinstance(pin, str) and SHA.fullmatch(pin), label + ' SHA malformed')
        check(git_blob(raw) == pin, label + ' Git blob mismatch')
    try:
        html = body.decode('utf-8')
    except UnicodeError as ex:
        raise PairHold('article body non-UTF8') from ex
    m = decode_metadata(metadata)
    check(isinstance(m, dict) and m.get('slug') == slug, 'metadata slug mismatch')
    check(isinstance(m.get('n'), int) and not isinstance(m['n'], bool) and m['n'] > 0,
          'invalid original article number')
    check(isinstance(m.get('status'), dict) and m['status'].get('publish') == 'draft',
          'non-draft published/unknown article')
    safety = m.get('safety_review')
    check(isinstance(safety, dict) and safety.get('state') == 'pending' and
          safety.get('reviewer') is None and safety.get('date') is None,
          'unreviewed safety state cannot become approved')
    scope = m.get('source_use')
    check(isinstance(scope, dict) and bool(scope), 'missing author source_use map')
    check(all(isinstance(k, str) and ID.fullmatch(k) and isinstance(v, str) and v.strip()
              for k, v in scope.items()), 'malformed/empty source_use')
    cited = CITE.findall(html)
    check(cited and len(cited) == html.count('{{cite:'), 'malformed citation token')
    check(set(cited) == set(scope), 'source_use and literal citation identities differ')
    return {'slug': slug, 'variant': variant, 'n': m['n'], 'source_use': scope,
            'citation_count': len(cited), 'source_count': len(scope),
            'body_git_blob': body_sha, 'metadata_git_blob': meta_sha}

def audit(meta_pins, body_pins, evidence):
    """Sixteen body/meta pairs; no source-use scope may disappear or be overwritten."""
    check(isinstance(meta_pins, dict) and meta_pins.get('schema') == 1 and
          meta_pins.get('state') == HOLD and meta_pins.get('qd_pass') is False and
          meta_pins.get('publication_authorized') is False, 'meta pin ledger not held')
    check(isinstance(body_pins, dict) and body_pins.get('schema') == 1 and
          body_pins.get('state') == HOLD and body_pins.get('qd_pass') is False,
          'R464 original body pins absent/altered')
    check(set(meta_pins.get('articles', {})) == set(SLUGS) and
          set(body_pins.get('articles', {})) == set(SLUGS), 'Shelter inventory incomplete')
    check(meta_pins.get('source_commit_sha') == body_pins.get('origin_commit_sha'),
          'metadata origins retargeted from frozen R464 Git commits')
    expected = {(s, v) for s in SLUGS for v in VARIANTS}
    check(isinstance(evidence, dict) and set(evidence) == expected,
          'missing, duplicate or unexpected original-body/metadata witness')
    rows = {}
    for slug in SLUGS:
        check(set(meta_pins['articles'][slug]) == set(VARIANTS) and
              set(body_pins['articles'][slug]) == set(VARIANTS), 'variant pin missing')
        for variant in VARIANTS:
            pair = evidence[(slug, variant)]
            check(isinstance(pair, tuple) and len(pair) == 2,
                  'body and metadata must be separate raw byte streams')
            rows[(slug, variant)] = inspect_pair(slug, variant, pair[0], pair[1],
                body_pins['articles'][slug][variant], meta_pins['articles'][slug][variant])
        check(len({rows[(slug, v)]['n'] for v in VARIANTS}) == 1,
              'original article number changed across witnesses')
    deltas = []
    for slug in SLUGS:
        candidate = rows[(slug, 'candidate')]['source_use']
        for v in VARIANTS[:-1]:
            older = rows[(slug, v)]['source_use']
            removed = sorted(set(older) - set(candidate))
            changed = sorted(k for k in older if k in candidate and older[k] != candidate[k])
            check(not removed, slug + '/' + v + ': candidate dropped cited source IDs ' + ','.join(removed))
            check(not changed, slug + '/' + v + ': candidate overwrote authored reading scopes ' + ','.join(changed))
            deltas.append({'slug': slug, 'witness': v,
                           'source_ids_added': sorted(set(candidate) - set(older)),
                           'source_ids_removed': removed,
                           'reading_scopes_rewritten': changed,
                           'candidate_citation_count': rows[(slug, 'candidate')]['citation_count'],
                           'witness_citation_count': rows[(slug, v)]['citation_count'],
                           'review_required': True, 'qualified_qd_pass': False})
    return {'state': 'SHELTER_SOURCE_USE_CUSTODY_INTACT_REVIEW_REQUIRED',
            'release_state': HOLD, 'qualified_qd_pass': False,
            'publication_authorized': False, 'version_winner_selected': False,
            'claim_to_source_verified': False, 'paid_offer_verified': False,
            'pair_count': len(rows), 'comparison_count': len(deltas), 'deltas': deltas}

def raw_file(root, part):
    check(isinstance(part, Path) and not part.is_absolute() and '..' not in part.parts,
          'unsafe evidence path')
    path = root / part
    check(path.is_file() and not path.is_symlink() and not path.parent.is_symlink() and
          0 < path.stat().st_size < 250000, 'missing/linked/oversized evidence: ' + str(part))
    return path.read_bytes()

def native(root, witness_root):
    # All paths are read-only, caller never writes into canonical checkout.
    mp = decode_metadata(raw_file(root, Path('audits/R465_SHELTER_META_PINS.json')))
    bp = decode_metadata(raw_file(root, Path('audits/R464_SHELTER_WITNESS_PINS.json')))
    values = {}
    for slug in SLUGS:
        for variant in VARIANTS:
            folder = root if variant == 'candidate' else witness_root / variant
            prefix = Path('content/articles') if variant == 'candidate' else Path('.')
            values[(slug, variant)] = (
                raw_file(folder, prefix / (slug + '.body.html')),
                raw_file(folder, prefix / (slug + '.meta.json')))
    return audit(mp, bp, values)

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument('--witness-root', type=Path, default=Path(__file__).resolve().parents[1] / 'audits/r465_witnesses')
    a = p.parse_args(argv)
    try:
        output = native(a.root, a.witness_root)
    except (OSError, ValueError, UnicodeError, TypeError, KeyError) as ex:
        output = {'state': 'SHELTER_METADATA_EVIDENCE_HARD_HOLD', 'error': str(ex),
                  'release_state': HOLD, 'qualified_qd_pass': False,
                  'publication_authorized': False}
    print(json.dumps(output, sort_keys=True, indent=2))
    return 2  # Custody intact means review is possible, NEVER publication approval.

if __name__ == '__main__':
    sys.exit(main())
