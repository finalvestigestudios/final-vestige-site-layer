#!/usr/bin/env python3
"""Draft-only, byte-pinned family-card claim/HTML correction candidate.

No source changes, approval writes, WordPress calls or publication. An authentic
checkout is required for --repo; synthetic tests do NOT constitute authentic QA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = 'fv-preparedness-r158-family-card-correction-candidate-v1'
BODY = 'preparedness/content/tools/family-reunification-card.body.html'
META = 'preparedness/content/tools/family-reunification-card.meta.json'
BODY_BLOB = 'be8698ac5d020476ff649d85813810e2000c6f98'
META_BLOB = '47da1e7e20e39f0ea85e26d54a8d58301f6e0a15'
CITES = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
ALLOWED_SOURCES = frozenset(('shelter-ca-cde-safety-plans', 'shelter-cdc-chemical-evac',
    'shelter-cdc-reunification', 'shelter-co-oss-reunification', 'shelter-ncmec-hotline',
    'shelter-fema-reunification', 'shelter-fcc-comms', 'shelter-ready-evacuation',
    'shelter-ready-plan', 'shelter-ready-plan-form', 'shelter-ready-tech'))
TAGS = re.compile(r'<(/?)([a-z][\w:-]*)(?=[\s/>])', re.I)
REPLACEMENTS = (
    ('and use text messages rather than calls for everything else when networks are busy.',
     'and follow local emergency instructions; text may be an option when voice calls are congested, but delivery is not guaranteed.'),
    ('<strong>Private by design:</strong> what you type stays on this page. It is not sent or saved. Closing the tab clears it.',
     '<strong>Privacy note:</strong> The card script is designed to display your entries on this page, not upload them. The website, browser, extensions, printing and shared devices may handle or retain data differently. Use minimal details. Independent browser privacy checks remain pending.'),
    ('A blank fold-over card is shown below. Print it and fill it in by hand. The form below still works and prints. Only the automatic reminders and the text download need JavaScript.',
     'A blank fold-over card is shown below. Print it and fill it in by hand. The interactive preview and clear button require JavaScript.'),
    ('and says the information entered is not saved, stored or shared by any government agency.',
     'but this draft does not independently verify that site\'s data handling or what a browser or device may retain.'),
    ("tells parents to wait for the school's notification, to bring photo ID, and not to rush to the school;",
     "discusses waiting for school instructions; confirm identification and pickup requirements with your child's own school;"),
)
META_REPLACEMENTS = (
    ('Free, local-only, prints at true size.',
     'Free printable draft; privacy and print layout need independent browser testing.'),
    ('Minimal privacy version. Nothing is stored.',
     'Optional minimal version; browser privacy and print behavior remain unverified.'),
)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def replace_once(source: str, needle: str, replacement: str) -> str:
    need(source.count(needle) == 1, 'missing or ambiguous correction anchor: ' + needle[:75])
    need(needle != replacement and needle and replacement, 'empty or no-op correction')
    return source.replace(needle, replacement, 1)


def tag_sequence(s: str) -> list[tuple[str, str]]:
    return [(m.group(1), m.group(2).lower()) for m in TAGS.finditer(s)]


def script_style_blocks(s: str) -> list[str]:
    return re.findall(r'<(?:script|style)\b[^>]*>.*?</(?:script|style)>', s, flags=re.I|re.S)


def correction(body: str, meta_raw: str) -> tuple[str, str, dict]:
    """Creates a reviewable proposal. DOES NOT approve the changed citations."""
    before = json.loads(meta_raw)
    need(type(before) is dict and before.get('slug') == 'family-reunification-card'
         and before.get('status', {}).get('publish') == 'draft'
         and before.get('safety_review', {}).get('state') == 'pending',
         'family card is not the expected unapproved draft')
    need(type(before.get('source_use')) is dict and len(before['source_use']) == 11,
         'eleven original source-use relationships not preserved')
    need(len(CITES.findall(body)) == 16 and set(CITES.findall(body)).issubset(ALLOWED_SOURCES),
         'original 16 citation occurrences or source identities changed')
    amended = body
    for old, new in REPLACEMENTS:
        amended = replace_once(amended, old, new)
    need(CITES.findall(body) == CITES.findall(amended), 'citation IDs or ordering altered')
    need(script_style_blocks(body) == script_style_blocks(amended),
         'original JavaScript/CSS altered')
    need(tag_sequence(body) == tag_sequence(amended), 'original HTML element structure altered')
    need(len(amended) >= int(len(body) * 0.98), 'loss of instructional reading depth')
    revised = json.loads(meta_raw)
    for key, old, new in (('dek', *META_REPLACEMENTS[0]), ('description', *META_REPLACEMENTS[1])):
        revised[key] = replace_once(revised[key], old, new)
    for key in ('source_use', 'status', 'safety_review', 'slug', 'kind', 'related', 'recheck'):
        need(before.get(key) == revised.get(key), 'source or review metadata altered: ' + key)
    need(revised['status']['publish'] == 'draft' and revised['safety_review']['state'] == 'pending',
         'unsafe publication/safety state')
    # JSON rendering is an output-only candidate; original file stays byte-identical.
    report = {'schema': SCHEMA, 'state': 'DRAFT_HARD_HOLD',
        'html_correction_anchors': len(REPLACEMENTS),
        'metadata_correction_anchors': len(META_REPLACEMENTS),
        'citation_occurrences': len(CITES.findall(amended)),
        'source_relationships': len(revised['source_use']),
        'script_and_style_unchanged': True,
        'article_or_tool_source_modified': False,
        'independent_source_review_approved': False,
        'independent_safety_qd_approved': False,
        'browser_privacy_print_verified': False,
        'founder_release_authorized': False,
        'public_publishing_allowed': False,
        'paid_offer_active': False}
    return amended, json.dumps(revised, ensure_ascii=False, indent=2) + '\n', report


def pinned(root: Path, path: str, blob: str) -> bytes:
    root = root.resolve(strict=True)
    f = root / path
    need(f.is_file() and not f.is_symlink(), 'missing or symlink original: ' + path)
    raw = f.read_bytes()
    need(git_blob(raw) == blob, 'authentic source Git blob mismatch: ' + path)
    return raw


def authentic(root: Path) -> dict:
    body = pinned(root, BODY, BODY_BLOB).decode('utf-8')
    meta = pinned(root, META, META_BLOB).decode('utf-8')
    _, _, report = correction(body, meta)
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    try:
        print(json.dumps(authentic(args.repo), sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({'state':'INVALID_HARD_HOLD', 'reason': str(exc),
                          'public_publishing_allowed':False}))
    return 2  # structural success is still HOLD, never an approval.


if __name__ == '__main__':
    raise SystemExit(main())
