#!/usr/bin/env python3
"""Read-only fail-closed preservation gate for Final Vestige EX2's WordPress Page 6.

Required input is PUBLIC-ONLY page content markup exported by an authorized reviewer.
The source-control baseline contains only hashes/counts, never subscriber data.
Not an authorization to publish, edit WordPress, install a plugin or mark QD PASS.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

MARGIN_RE = re.compile(r'<span\s+class="fv-margin-strip__item"[^>]*>[\s\S]*?</span>')
INDEX_RE = re.compile(r'--i:(\d+)')
JETPACK_OPEN = re.compile(r'<div\b[^>]*class="[^"]*\bwp-block-jetpack-subscriptions\b[^"]*"[^>]*>', re.I)
DIV = re.compile(r'</?div\b[^>]*>', re.I)
FOCUS = 'https://finalvestige.com/focus/'


def digest(value: str) -> str:
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def jetpack_block(html: str) -> str | None:
    opening = JETPACK_OPEN.search(html)
    if not opening:
        return None
    depth = 0
    for tag in DIV.finditer(html, opening.start()):
        depth += -1 if tag.group().startswith('</') else 1
        if depth == 0:
            return html[opening.start(): tag.end()]
    return None


def inventory(html: str) -> dict:
    records = MARGIN_RE.findall(html)
    idx = [int(m.group(1)) for record in records if (m := INDEX_RE.search(record))]
    block = jetpack_block(html)
    return {
        'content_sha256': digest(html),
        'record_count': len(records),
        'record_indexes': idx,
        'record_spans_sha256': digest('\n'.join(records)),
        'jetpack_block_present': block is not None,
        'jetpack_block_sha256': digest(block) if block is not None else None,
        'jetpack_block_length': len(block) if block else 0,
        'focus_href_count': html.count(FOCUS),
        'chapter_ids': sorted(set(re.findall(r'\bid="([^"]+)"', html))),
        'has_assembler_flagship': 'data-fv-home-flagship' in html,
    }


def evaluate(html: str, manifest: dict, require_current_snapshot: bool = False) -> dict:
    found = inventory(html)
    errors = []
    expected_indexes = list(range(manifest['record_count']))
    if found['record_count'] != manifest['record_count']:
        errors.append(f"72-item inventory changed: {found['record_count']} records; expected {manifest['record_count']}")
    if found['record_indexes'] != expected_indexes:
        errors.append('Hidden in the Margins record identifiers/order changed')
    if found['record_spans_sha256'] != manifest['record_spans_sha256']:
        errors.append('Original 72 Hidden in the Margins record markup/text differs')
    if not found['jetpack_block_present']:
        errors.append('Native Jetpack subscriptions block missing')
    if found['jetpack_block_sha256'] != manifest['jetpack_block_sha256']:
        errors.append('Native Jetpack subscriptions block changed')
    if found['focus_href_count'] < manifest['focus_href_min_count']:
        errors.append(f"Focus destination count fell to {found['focus_href_count']}")
    if not found['has_assembler_flagship']:
        errors.append('Homepage evidence flagship root missing')
    missing = sorted(set(manifest['required_chapter_ids']) - set(found['chapter_ids']))
    if missing:
        errors.append('Seven-chapter anchor IDs missing: ' + ', '.join(missing))
    if require_current_snapshot and found['content_sha256'] != manifest['page_content_sha256']:
        errors.append('Canonical Page 6 snapshot differs; re-review baseline')
    return {'gate': 'PASS' if not errors else 'HOLD', 'release_approved': False,
            'scope': 'offline supplied markup only: not WordPress/Jetpack staging acceptance',
            'errors': errors, 'measured': found, 'baseline_modified': manifest.get('modified')}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--candidate', type=Path, required=True,
                   help='Post-integration WordPress Page 6 markup; not standalone EX2 index.html')
    p.add_argument('--current-snapshot', action='store_true',
                   help='Check byte-exact current Page 6 content digest')
    p.add_argument('--out', type=Path)
    args = p.parse_args(argv)
    manifest = json.loads(args.baseline.read_text(encoding='utf-8'))
    html = args.candidate.read_text(encoding='utf-8')
    result = evaluate(html, manifest, args.current_snapshot)
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload + '\n', encoding='utf-8')
    print(payload)
    return 0 if result['gate'] == 'PASS' else 1


if __name__ == '__main__':
    sys.exit(main())
