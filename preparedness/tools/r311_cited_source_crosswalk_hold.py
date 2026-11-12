#!/usr/bin/env python3
"""R311 read-only cited-source crosswalk for all six FV Preparedness tools.

Maintains source custody and detects competing fetched citations; never approves
medical/safety guidance, publication, privacy, commercial offers or QD status.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('r310_pinned', HERE / 'r310_six_tool_identity_citation_privacy_hold.py')
r310 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r310)

SCHEMA = 'fv-preparedness-r311-six-tool-cited-source-crosswalk-v1'
PREDECESSOR = 'preparedness/tools/r310_six_tool_identity_citation_privacy_hold.py'
PREDECESSOR_OID = '0e7252475a0bb66711470c0b9ac5c2bdd699157c'
SOURCES = {
    'preparedness/sources/register.json': 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
    'preparedness/sources/fragments/start.json': '96140d6d1872588e5d20d9052445c9157e88934d',
    'preparedness/sources/fragments/shelter.json': '2a3f1a7ddeab2782add875be1e0e378513504aa1',
    'preparedness/sources/fragments/food.json': 'a1f73c8170932d6b3192e9cd506686d516d23d30',
    'preparedness/sources/fragments/health.json': 'cc29c439372b9d49debf78e63020ffe4d62baeb8',
}
ISO_DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
SOURCE_ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def source_url(url: object) -> bool:
    if not isinstance(url, str) or not url or url.strip() != url:
        return False
    try:
        u = urlsplit(url)
        return (u.scheme == 'https' and bool(u.hostname) and not u.username and
                not u.password and not any(c.isspace() or ord(c) < 32 for c in url) and
                not u.hostname.endswith('.invalid'))
    except ValueError:
        return False


def audit(root: Path, *, source_pins: dict | None = None, tool_pins: dict | None = None,
          predecessor_oid: str | None = None, r310_predecessor_oid: str | None = None,
          taxonomy_oid: str | None = None, require_pins: bool = True) -> dict:
    """Read-only; fixture pins permitted for controlled synthetic regression tests."""
    source_pins = SOURCES if source_pins is None else source_pins
    tool_pins = r310.BLOBS if tool_pins is None else tool_pins
    predecessor_oid = PREDECESSOR_OID if predecessor_oid is None else predecessor_oid
    errors: list[str] = []
    if set(source_pins) != set(SOURCES):
        errors.append('SOURCE_FILE_SET_INCOMPLETE_OR_EXTRA')
    data = r310.file_bytes(root, PREDECESSOR)
    if data is None or (require_pins and r310.oid(data) != predecessor_oid):
        errors.append('R310_PREDECESSOR_MISSING_OR_CHANGED')
    prior = r310.audit(root, pins=tool_pins,
                       predecessor_oid=r310.PREDECESSOR_OID if r310_predecessor_oid is None else r310_predecessor_oid,
                       taxonomy_oid=r310.TAXONOMY_OID if taxonomy_oid is None else taxonomy_oid,
                       enforce_custody=require_pins)
    errors.extend('INHERITED_R310:' + e for e in prior['errors'])
    records: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    file_counts: dict[str, int] = {}
    verified_blobs = 0
    for p, expected in sorted(source_pins.items()):
        if p not in SOURCES:
            errors.append('UNEXPECTED_SOURCE_FILE:' + p)
            continue
        b = r310.file_bytes(root, p)
        if b is None:
            errors.append('SOURCE_FILE_MISSING_OR_SYMLINK:' + p)
            continue
        if require_pins and r310.oid(b) != expected:
            errors.append('SOURCE_FILE_GIT_BLOB_DRIFT:' + p)
        else:
            verified_blobs += 1
        try:
            payload = json.loads(b.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            errors.append('SOURCE_FILE_INVALID_JSON:' + p)
            continue
        sources = payload.get('sources') if isinstance(payload, dict) else None
        if not isinstance(sources, list):
            errors.append('SOURCE_FILE_INVALID_SCHEMA:' + p)
            continue
        file_counts[p] = len(sources)
        seen = set()
        for i, src in enumerate(sources):
            if not isinstance(src, dict):
                errors.append(f'SOURCE_RECORD_NOT_OBJECT:{p}:{i}')
                continue
            sid = src.get('id')
            if not isinstance(sid, str) or not SOURCE_ID.fullmatch(sid):
                errors.append(f'SOURCE_ID_INVALID:{p}:{i}')
                continue
            if sid in seen:
                errors.append(f'DUPLICATE_ID_IN_SOURCE_FILE:{p}:{sid}')
            seen.add(sid)
            if not source_url(src.get('url')):
                errors.append(f'SOURCE_URL_INVALID:{p}:{sid}')
            when = src.get('verified_on')
            if when is not None:
                if not isinstance(when, str) or not ISO_DATE.fullmatch(when):
                    errors.append(f'SOURCE_FETCH_DATE_INVALID:{p}:{sid}')
                else:
                    try:
                        if date.fromisoformat(when) > date(2026, 11, 12):
                            errors.append(f'SOURCE_FUTURE_FETCH_DATE:{p}:{sid}')
                    except ValueError:
                        errors.append(f'SOURCE_FETCH_DATE_INVALID:{p}:{sid}')
            records[sid].append((p, src))
    cited = []
    missing = []
    dup_verified = []
    human_unchecked = []
    # Each tool is separately pinned by R310; citations are a metadata source-use
    # crosswalk, not a claim that the source substantiates the text.
    for slug in r310.SLUGS:
        p = f'preparedness/content/tools/{slug}.meta.json'
        raw = r310.file_bytes(root, p)
        if raw is None:
            continue
        try:
            meta = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError):
            errors.append('TOOL_META_INVALID_JSON:' + slug)
            continue
        uses = meta.get('source_use') if isinstance(meta, dict) else None
        if not isinstance(uses, dict):
            errors.append('TOOL_SOURCE_USE_INVALID:' + slug)
            continue
        for sid, claim in sorted(uses.items()):
            if not isinstance(sid, str) or not SOURCE_ID.fullmatch(sid):
                errors.append('TOOL_CITATION_ID_INVALID:' + slug)
                continue
            candidates = records.get(sid, [])
            fetched = [(path, row) for path, row in candidates if row.get('verified_on') is not None]
            if not candidates:
                errors.append(f'CITED_SOURCE_NOT_REGISTERED:{slug}:{sid}')
                missing.append(sid)
            elif not fetched:
                errors.append(f'CITED_SOURCE_NOT_FETCH_VERIFIED:{slug}:{sid}')
            else:
                if any(not isinstance(v.get('supports'), str) or not v.get('supports').strip() for _, v in fetched):
                    errors.append(f'CITED_SOURCE_SUPPORT_MISSING:{slug}:{sid}')
                if len(fetched) > 1:
                    errors.append(f'DUPLICATE_FETCH_VERIFIED_SOURCE_REQUIRES_ADJUDICATION:{sid}')
                    dup_verified.append(sid)
                if len({v.get('url') for _, v in fetched}) > 1:
                    errors.append(f'FETCH_VERIFIED_URL_CONFLICT:{sid}')
                if any(v.get('url') != fetched[0][1].get('url') for _, v in candidates):
                    errors.append(f'UPGRADE_URL_DRIFT_REQUIRES_REVIEW:{sid}')
                if not any(v.get('human_link_check') is True for _, v in fetched):
                    human_unchecked.append(sid)
            cited.append({'tool_slug': slug, 'source_id': sid,
                          'source_use_claim': claim if isinstance(claim, str) else None,
                          'fetched_records': [{'file': p, 'verified_on': r.get('verified_on'),
                                               'url': r.get('url'), 'publisher': r.get('publisher'),
                                               'human_link_check': r.get('human_link_check')}
                                              for p, r in fetched],
                          'source_record_count': len(candidates)})
    return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors': sorted(set(errors)), 'source_files_loaded': file_counts,
            'source_blobs_verified': verified_blobs, 'crosswalk_entries': cited,
            'total_source_use_links': len(cited),
            'unique_cited_source_ids': len({x['source_id'] for x in cited}),
            'unregistered': sorted(set(missing)),
            'duplicate_fetch_verified_ids': sorted(set(dup_verified)),
            'human_link_check_outstanding_ids': sorted(set(human_unchecked)),
            'r310_state': prior['state'], 'r310_number_collisions': prior['number_collisions'],
            'publication_authorized': False, 'independent_qd_pass': False,
            'medical_safety_verified': False, 'actual_41_wordpress_drafts_verified': False,
            'rights_cleared_paid_sku_verified': False, 'confirmed_paid_orders': None,
            'net_revenue_per_1000_qualified_sessions': None}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument('--output', type=Path, help='Optional local JSON output; never touches source files')
    args = ap.parse_args()
    result = audit(args.root)
    report = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding='utf-8')
    else:
        print(report, end='')
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
