#!/usr/bin/env python3
"""R163 quarantined Family Card source-scope correction; never grants publication.

Review-only. An intact corpus, cited official text and human approval are separate
requirements; this script cannot establish any of them by mere wording checks.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = 'fv-preparedness-r163-family-scope-v1'
PRIOR = 'preparedness/review/r159/family-reunification-card.body.html'
PRIOR_SHA = '7a7b6cffbc75cb6c9a0c13ad5002ccf0f5d22ef0'
META = 'preparedness/review/r159/family-reunification-card.meta.json'
META_SHA = '2bafef03a375b0156e2dcd7f1b913d119becad61'
EVIDENCE = 'preparedness/docs/r155/family-source-observations.json'
EVIDENCE_SHA = '9e689fde7e2913340c89886a7fb02994245b60eb'
STAGED = 'preparedness/review/r163/family-reunification-card.body.html'
CITES = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
TAGS = re.compile(r'<(/?)([a-z][\w:-]*)(?=[\s/>])', re.I)
BLOCKS = re.compile(r'<(?:script|style)\b[^>]*>.*?</(?:script|style)>', re.I | re.S)
CHANGES = (
    (
        'The out-of-area contact comes first because networks jam. Ready.gov says text messages require less bandwidth and can be transmitted more reliably when many people are using their phones, and the FCC\'s older guide advises designating someone out of the area as a central contact.',
        'An out-of-area contact may help household members coordinate if that person is reachable, but calls and texts can fail or be delayed. This draft has not independently verified the cited Ready.gov and older FCC wording; check current guidance from local officials.'
    ),
    (
        'If a child is missing after a disaster, the CDC lists NCMEC\'s 24-hour hotline, 1-800-THE-LOST, and NCMEC\'s own site shows the same number as 1-800-843-5678.',
        'For a missing child, the CDC\'s reunification guidance references NCMEC. Its website lists 1-800-843-5678 (1-800-THE-LOST), but the linked CyberTipline page primarily addresses online exploitation reports; it is not a general disaster-reunification service.'
    ),
    (
        'FEMA\'s fact sheet describes national reunification support, which is activated only in some Presidentially declared disasters, and FEMA marks it as archived content, so do not rely on it being available.',
        'An older FEMA reunification fact sheet is cited for context; its current scope and availability have not been independently verified here. Do not assume that a national reunification service is available; follow official local instructions.'
    ),
)
EXPECTED_SCOPE = {
    'shelter-co-oss-reunification': 'SCOPE_REVIEW_REQUIRED',
    'shelter-ncmec-hotline': 'CONTEXT_REVIEW_REQUIRED',
}
EXPECTED_BLOCKED = frozenset({
    'shelter-fema-reunification', 'shelter-fcc-comms',
    'shelter-ready-evacuation', 'shelter-ready-plan',
    'shelter-ready-plan-form', 'shelter-ready-tech',
})
EXPECTED_SUPPORT = frozenset({
    'shelter-ca-cde-safety-plans', 'shelter-cdc-chemical-evac',
    'shelter-cdc-reunification',
})


def need(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def read_pinned(root: Path, name: str, sha: str) -> bytes:
    path = root / name
    need(path.is_file() and not path.is_symlink(), 'missing/linked evidence: ' + name)
    data = path.read_bytes()
    need(blob(data) == sha, 'original Git evidence drift: ' + name)
    return data


def verify_observations(record: dict) -> dict[str, dict]:
    need(record.get('schema') == 'fv-preparedness-r155-family-source-observation-v1', 'source evidence schema drift')
    need(record.get('tool') == 'family-reunification-card', 'wrong reviewed tool')
    for f in ('independent_review', 'source_approval', 'publication_authorized', 'commercial_offer_verified'):
        need(record.get(f) is False, 'forged approval: ' + f)
    rows = record.get('observations')
    need(isinstance(rows, list) and len(rows) == 11, 'eleven observations required')
    by_id = {}
    for item in rows:
        sid = item.get('source_id')
        need(sid not in by_id and isinstance(sid, str), 'missing/duplicate source identity')
        url = item.get('source_url')
        need(isinstance(url, str) and url.startswith('https://') and '?' not in url and '#' not in url, 'unexpected source URL')
        need(item.get('review_state') == 'PENDING' and item.get('human_link_checked') is False
             and item.get('qualified_safety_review') is False, 'human source review forged')
        need(isinstance(item.get('observation'), str) and len(item['observation']) >= 50, 'missing source explanation')
        by_id[sid] = item
    need(set(by_id) == set(EXPECTED_SCOPE) | EXPECTED_BLOCKED | EXPECTED_SUPPORT, 'source crosswalk changed')
    for sid, scope in EXPECTED_SCOPE.items():
        need(by_id[sid].get('scope') == scope and by_id[sid].get('access') == 'RETRIEVED_TEXT', 'disputed scope reclassified: '+sid)
    for sid in EXPECTED_BLOCKED:
        need(by_id[sid].get('scope') == 'NOT_OBSERVABLE' and by_id[sid].get('access') == 'RETRIEVAL_BLOCKED', '403 reclassified: '+sid)
    for sid in EXPECTED_SUPPORT:
        need(by_id[sid].get('scope') == 'CLAIM_MATCH_OBSERVED' and by_id[sid].get('access') == 'RETRIEVED_TEXT', 'source result changed: '+sid)
    return by_id


def propose(html: str, meta: dict, record: dict) -> tuple[str, dict]:
    by_id = verify_observations(record)
    need(meta.get('slug') == 'family-reunification-card' and meta.get('kind') == 'tool', 'wrong article')
    need(meta.get('status', {}).get('publish') == 'draft' and meta.get('safety_review', {}).get('state') == 'pending', 'release/safety hold violated')
    uses = meta.get('source_use')
    need(isinstance(uses, dict) and set(uses) == set(by_id) and len(uses) == 11, 'author source interpretations missing')
    original_cites = CITES.findall(html)
    need(len(original_cites) == 16 and set(original_cites) == set(by_id), 'original source occurrence census changed')
    before_tags = TAGS.findall(html)
    before_blocks = BLOCKS.findall(html)
    updated = html
    for old, new in CHANGES:
        need(updated.count(old) == 1 and old != new, 'ambiguous source correction')
        updated = updated.replace(old, new, 1)
    need(CITES.findall(updated) == original_cites, 'source citations reordered/dropped')
    need(TAGS.findall(updated) == before_tags and BLOCKS.findall(updated) == before_blocks, 'HTML or executable code altered')
    need(len(updated) >= int(0.98 * len(html)), 'reading depth removed')
    for old, _ in CHANGES:
        need(old not in updated, 'unverified original claim remains')
    need('CyberTipline page primarily addresses online exploitation' in updated, 'hotline scope warning missing')
    need('not independently verified' in updated and 'follow official local instructions' in updated, 'unknown availability no longer qualified')
    return updated, {
        'schema': SCHEMA, 'state': 'DRAFT_HARD_HOLD',
        'sources_preserved': 11, 'citations_preserved': 16,
        'scope_disputed': 2, 'retrieval_blocked_not_dead': 6,
        'narrow_text_match_still_pending': 3, 'review_text_changes': len(CHANGES),
        'candidate_sha256': hashlib.sha256(updated.encode('utf-8')).hexdigest(),
        'source_approval': False, 'qualified_safety_review': False,
        'independent_qd_pass': False, 'browser_privacy_verified': False,
        'grok_asset_verified': False, 'paid_sku_verified': False,
        'publication_authorized': False,
    }


def audit(root: Path) -> dict:
    # The R162 chain first verifies all 35 canonical articles plus #157/#169/#973 intents.
    import sys
    sys.path.insert(0, str(root / 'preparedness' / 'tools'))
    import r162_qa_rebase_gate as prior
    upstream = prior.check(root)
    need(upstream.get('state') == 'DRAFT_HARD_HOLD' and upstream.get('original_article_count_from_r161') == 35,
         'upstream QA/35-article custody invalid')
    html = read_pinned(root, PRIOR, PRIOR_SHA).decode('utf-8')
    meta = json.loads(read_pinned(root, META, META_SHA))
    observations = json.loads(read_pinned(root, EVIDENCE, EVIDENCE_SHA))
    candidate, receipt = propose(html, meta, observations)
    staged = root / STAGED
    need(staged.is_file() and not staged.is_symlink(), 'staged review HTML missing')
    need(staged.read_bytes() == candidate.encode('utf-8'), 'quarantined review candidate drift')
    receipt['staged_path'] = STAGED
    receipt['prior_35_article_custody'] = 'CHECKED_DRAFT_HOLD'
    return receipt


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, default=Path('.'))
    opts = ap.parse_args(argv)
    try:
        report = audit(opts.repo.resolve(strict=True))
    except (ValueError, OSError, UnicodeError, TypeError, KeyError, ImportError, json.JSONDecodeError) as error:
        report = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD', 'reason': str(error), 'publication_authorized': False}
    print(json.dumps(report, sort_keys=True))
    return 2  # even authentic validation must never return a release success code


if __name__ == '__main__':
    raise SystemExit(main())
