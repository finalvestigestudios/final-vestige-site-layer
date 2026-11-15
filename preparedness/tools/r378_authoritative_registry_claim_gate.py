"""R378 read-only Article 11 authoritative-registry/source-use review gate.

No check in this module authorizes publication or replaces qualified food-safety QA.
Run with: python -I preparedness/tools/r378_authoritative_registry_claim_gate.py
Always exits 2; never writes to the source checkout or a CMS.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PIN = {
    'content/articles/safe-jerky-dehydration.body.html': '6fa55c397b161437e016d5d4a6c27da7ce3fa6bd',
    'content/articles/safe-jerky-dehydration.meta.json': '50b365e8109c14bdb9ce1a9365db88215a678ec5',
    'sources/register.json': 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
    'sources/fragments/food.json': 'a1f73c8170932d6b3192e9cd506686d516d23d30',
    'tools/build.py': '349173d1e1d735eade218d95c7a0a2649c8cccd9',
    'tools/validate.py': 'a0b6a1c8a63b7502125e5750b0bc1e3cf347620b',
    'sources/crosswalk.json': 'd62e493a67dedd23e04cfdf3cce762ef933c6bf9',
    'audits/r377_jerky_source_conflict_HARD_HOLD.json': '2a2923a27b8ad78281f565de685ff70df56a7168',
}
BASE_ONLY = ('cdc-botulism-prevention', 'fsis-home-cure-qa', 'nchfp-cure-smoke')
CITE_RE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
EXPECTED_COUNT = 71
EXPECTED_DISTINCT = 11


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data, usedforsecurity=False).hexdigest()


def check_pins(root: Path) -> list[str]:
    errors = []
    for rel, sha in sorted(PIN.items()):
        path = root / rel
        try:
            actual = git_blob(path.read_bytes())
        except OSError:
            errors.append(f'missing pinned original: {rel}')
            continue
        if actual != sha:
            errors.append(f'changed pinned original: {rel} ({actual})')
    return errors


def evaluate(base: dict, food: dict, body: str, meta: dict, crosswalk: dict, prior: dict) -> dict:
    """Pure deterministic audit. source_path_resolved is not an approval."""
    errors = []
    try:
        base_rows, own_rows = base['sources'], food['sources']
        if not isinstance(base_rows, list) or not isinstance(own_rows, list):
            raise TypeError('source records must be lists')
    except (KeyError, TypeError) as exc:
        return {'release_state': 'DRAFT_HARD_HOLD', 'source_path_resolved': False,
                'errors': [f'missing/invalid source registry: {exc}'], 'approval': False}
    by_base, by_food = {}, {}
    for group, rows in ((by_base, base_rows), (by_food, own_rows)):
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str):
                errors.append('malformed source row')
                continue
            if row['id'] in group:
                errors.append(f'duplicate source ID inside origin: {row["id"]}')
            group[row['id']] = row

    cited = CITE_RE.findall(body)
    uses = meta.get('source_use', {})
    if not isinstance(uses, dict):
        errors.append('source_use not a dictionary')
        uses = {}
    if meta.get('slug') != 'safe-jerky-dehydration' or meta.get('n') != 11:
        errors.append('article identity drift')
    if meta.get('status', {}).get('publish') != 'draft':
        errors.append('article is not draft')
    if meta.get('safety_review', {}).get('state') != 'pending':
        errors.append('safety review status not pending; human re-adjudication required')
    if len(cited) != EXPECTED_COUNT or len(set(cited)) != EXPECTED_DISTINCT:
        errors.append(f'citation occurrence/census drift: {len(cited)}/{len(set(cited))}')
    if set(cited) != set(uses):
        errors.append(f'citation/source_use drift: missing={sorted(set(cited)-set(uses))} extra={sorted(set(uses)-set(cited))}')
    if any(not isinstance(v, str) or not v.strip() for v in uses.values()):
        errors.append('blank article-specific source reading-scope text')
    if crosswalk.get('article_origins', {}).get('safe-jerky-dehydration') != 'food':
        errors.append('article origin must be the Food cluster, not inferred from shared URL')
    resolved = {}
    for sid in set(cited):
        record = by_food.get(sid) or by_base.get(sid)
        origin = 'food' if sid in by_food else 'base'
        if record is None:
            errors.append(f'citation ID unresolved in own/base origins: {sid}')
            continue
        resolved[sid] = origin
        parsed = urlsplit(str(record.get('url', '')))
        if parsed.scheme != 'https' or not parsed.hostname:
            errors.append(f'citation source URL not HTTPS: {sid}')
        if not str(record.get('supports', '')).strip():
            errors.append(f'citation source reading scope empty: {sid}')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(record.get('verified_on', ''))):
            errors.append(f'citation lacks machine-check date: {sid}')
        if record.get('human_link_check') is not False:
            errors.append(f'citation human-link status drift: {sid}')
    for sid in BASE_ONLY:
        if sid not in cited or sid not in uses:
            errors.append(f'base source missing from body/meta: {sid}')
        if sid in by_food:
            errors.append(f'base-only source shadowed by Food origin: {sid}')
        s = by_base.get(sid)
        if not s:
            errors.append(f'base register lacks citation source: {sid}')
            continue
        parsed = urlsplit(str(s.get('url', '')))
        if parsed.scheme != 'https' or not parsed.hostname or not str(s.get('supports', '')).strip():
            errors.append(f'base source lacks HTTPS URL/reading scope: {sid}')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(s.get('verified_on', ''))):
            errors.append(f'base source has no machine-check date: {sid}')
        if s.get('human_link_check') is not False:
            errors.append(f'human link flag drift; verify independently: {sid}')
    # The Food origin explicitly owns the more recent nchfp-jerky reading scope,
    # despite the same ID existing as a base-register placeholder.
    own = by_food.get('nchfp-jerky', {})
    placeholder = by_base.get('nchfp-jerky', {})
    if (not own.get('verified_on') or placeholder.get('verified_on') or
            own.get('url') != placeholder.get('url') or
            not str(own.get('supports', '')).strip() or
            own.get('human_link_check') is not False):
        errors.append('NCHFP Food-origin upgrade/reading scope drift')
    if set(prior.get('source_use_ids_absent_from_r374_fragment_crosswalk', [])) != set(BASE_ONLY):
        errors.append('prior source-fragment gap docket changed')
    if prior.get('release_state') != 'DRAFT_HARD_HOLD' or prior.get('publication_approved') is not False:
        errors.append('prior release state changed')
    if 'wild game' not in body.lower() or 'freez' not in body.lower():
        errors.append('disputed wild-game freezing claim changed; new safety review required')
    if 'heat' not in body.lower() or '160' not in body:
        errors.append('disputed heating sequence changed; new safety review required')
    return {
        'release_state': 'DRAFT_HARD_HOLD',
        'source_path_resolved': not errors,
        'source_origin_for_three': 'base',
        'human_link_checks_complete': False,
        'qualified_food_safety_review': False,
        'citations': {'occurrences': len(cited), 'unique_ids': len(set(cited)),
                      'base_fallback_ids': list(BASE_ONLY), 'resolved_origin_map': dict(sorted(resolved.items())), 'counts': dict(sorted(Counter(cited).items()))},
        'unresolved_claim_risks': ['wild-game freezing generalization', 'heating sequence equivalence'],
        'errors': sorted(set(errors)),
        'approval': False,
        'public_publish_allowed': False,
        'commercial_offer_allowed': False,
    }


def main() -> int:
    pins = check_pins(ROOT)
    if pins:
        result = {'release_state': 'DRAFT_HARD_HOLD', 'source_path_resolved': False,
                  'errors': pins, 'approval': False}
    else:
        def obj(rel: str) -> dict:
            return json.loads((ROOT / rel).read_text(encoding='utf-8'))
        result = evaluate(obj('sources/register.json'), obj('sources/fragments/food.json'),
                          (ROOT / 'content/articles/safe-jerky-dehydration.body.html').read_text(encoding='utf-8'),
                          obj('content/articles/safe-jerky-dehydration.meta.json'),
                          obj('sources/crosswalk.json'),
                          obj('audits/r377_jerky_source_conflict_HARD_HOLD.json'))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2  # No version of this evidence-only gate is publication permission.


if __name__ == '__main__':
    sys.exit(main())
