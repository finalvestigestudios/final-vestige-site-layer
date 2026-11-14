#!/usr/bin/env python3
"""R363 Preparedness citation ID -> contributor-source binding review docket.

Read only. Resolves *literal IDs*, never URL aliases, to original source rows.
The output is strictly a HARD HOLD: it is not claim validation or QD approval.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r363-citation-source-binding-v1'
TAXONOMY_BLOB = '15c547bb3018ac182b12a51036389cfa39a59168'
SOURCE_BLOBS = {
 'base': ('register.json', 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77', 34),
 'food': ('fragments/food.json', 'a1f73c8170932d6b3192e9cd506686d516d23d30', 30),
 'health': ('fragments/health.json', 'cc29c439372b9d49debf78e63020ffe4d62baeb8', 21),
 'hist-field': ('fragments/hist-field.json', '3dafa9425f3829c0be2e6fea00889aff95124031', 28),
 'hist-food': ('fragments/hist-food.json', 'd10628342fea5f177a8d1be00dd906d0c9c7850e', 28),
 'hist-home': ('fragments/hist-home.json', '8d85fd868508c5caba14a839d119d55f31f14f72', 29),
 'shelter': ('fragments/shelter.json', '2a3f1a7ddeab2782add875be1e0e378513504aa1', 45),
 'start': ('fragments/start.json', '96140d6d1872588e5d20d9052445c9157e88934d', 29),
}
CITE = re.compile(r'\{\{cite:([a-z][a-z0-9-]*)\}\}')
TOKEN_START = re.compile(r'\{\{cite:')
FORBIDDEN = ('published', 'live', 'approved', 'safety-reviewed', 'public')
HOLD = {'qd_pass': False, 'may_publish': False, 'may_merge': False,
        'medical_safety_verified': False, 'merchant_verified': False,
        'verified_paid_conversion': False, 'source_approval': False}


def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def unique_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('DUPLICATE_JSON_KEY:' + key)
        value[key] = item
    return value


def load_json(path: Path):
    return json.loads(path.read_text('utf-8'), object_pairs_hook=unique_pairs)


def source_index(records):
    out = defaultdict(list)
    for origin, rows in records.items():
        if not isinstance(rows, list):
            raise ValueError('BAD_SOURCE_ROWS:' + origin)
        for i, source in enumerate(rows):
            if not isinstance(source, dict) or not isinstance(source.get('id'), str):
                raise ValueError('BAD_SOURCE_RECORD:' + origin + ':' + str(i))
            out[source['id']].append((origin, i, source))
    return out


def check(meta, body, source_map):
    """Emit an occurrence-level docket; never resolve an ambiguous ID by URL alone."""
    errors, review = set(), set()
    if not isinstance(meta, dict) or not isinstance(body, str) or not isinstance(source_map, dict):
        return {'errors': ['BAD_INPUT'], 'review': [], 'occurrences': []}
    slug = meta.get('slug')
    if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        errors.add('BAD_SLUG')
    status = meta.get('status')
    safety = meta.get('safety_review')
    if not isinstance(status, dict) or status.get('publish') != 'draft':
        errors.add('UNAPPROVED_PUBLICATION_STATE')
    if not isinstance(safety, dict) or safety.get('state') not in ('pending', 'approved', 'not-required'):
        errors.add('UNAPPROVED_SAFETY_STATE')
    elif safety['state'] != 'pending':
        review.add('HUMAN_SAFETY_STATE_EVIDENCE_REQUIRED:' + safety['state'])
    uses = meta.get('source_use')
    if not isinstance(uses, dict):
        errors.add('SOURCE_USE_MISSING')
        uses = {}
    offsets = list(CITE.finditer(body))
    if len(offsets) != len(TOKEN_START.findall(body)):
        errors.add('MALFORMED_CITATION_TOKEN')
    cited = Counter(m.group(1) for m in offsets)
    for key, claim in uses.items():
        if not isinstance(key, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', key):
            errors.add('BAD_SOURCE_USE_ID')
        if not isinstance(claim, str) or not claim.strip():
            errors.add('EMPTY_SOURCE_USE:' + str(key))
        if key not in cited:
            review.add('DECLARED_NOT_CITED:' + str(key))
    for key in cited:
        if key not in uses:
            errors.add('CITED_BUT_UNDECLARED:' + key)
        candidates = source_map.get(key, [])
        if not candidates:
            errors.add('CITED_SOURCE_NOT_REGISTERED:' + key)
        elif len(candidates) != 1:
            review.add('MULTI_ORIGIN_SOURCE_ID:' + key)
        for origin, n, source in candidates:
            if not isinstance(source, dict):
                errors.add('INVALID_CANDIDATE:' + key)
                continue
            if not isinstance(source.get('url'), str) or not source['url'].startswith('https://'):
                errors.add('INVALID_SOURCE_URL:' + key)
            if not isinstance(source.get('supports'), str) or not source['supports'].strip():
                review.add('UNSUPPORTED_READING_SCOPE:' + key)
            if not source.get('verified_on'):
                review.add('NO_VERIFICATION_DATE:' + key)
            if source.get('human_link_check') is not True:
                review.add('HUMAN_LINK_CHECK_PENDING:' + key)
    occurrences = []
    for m in offsets:
        key = m.group(1)
        context = body[max(0, m.start()-90):min(len(body), m.end()+90)]
        candidates = source_map.get(key, [])
        occurrences.append({'id': key, 'offset': m.start(),
            'context_sha256': hashlib.sha256(context.encode('utf-8')).hexdigest(),
            'origins': [{'origin': origin, 'row': row, 'url': s.get('url')}
                for origin, row, s in candidates if isinstance(s, dict)]})
    return {'slug': slug, 'errors': sorted(errors), 'review': sorted(review),
            'occurrences': occurrences, 'citation_count': sum(cited.values()),
            'distinct_cited_ids': len(cited), 'declared_source_uses': len(uses)}


def report(errors, dockets=None):
    return {'schema': SCHEMA,
            'status': 'INVALID_HARD_HOLD' if errors else 'REVIEW_REQUIRED_HARD_HOLD',
            'errors': sorted(set(errors)), 'dockets': dockets or [], **HOLD}


def audit(root):
    """Pin the real original files; fail closed on absent checkout or source edits."""
    root = Path(root)
    if root.is_symlink() or not (root/'.git').exists():
        return report(['AUTHENTIC_CHECKOUT_MISSING'])
    try:
        src = root/'preparedness/sources'
        tax_path = root/'preparedness/taxonomy.json'
        if tax_path.is_symlink() or blob(tax_path.read_bytes()) != TAXONOMY_BLOB:
            return report(['TAXONOMY_PIN_DRIFT'])
        taxonomy = load_json(tax_path)
        slate = taxonomy['slate']
        if len(slate) != 35 or len(set(x['slug'] for x in slate)) != 35:
            return report(['SLATE_CLOSURE_DRIFT'])
        records = {}
        for origin, (rel, sha, n) in SOURCE_BLOBS.items():
            p = src/rel
            if p.is_symlink() or blob(p.read_bytes()) != sha:
                return report(['SOURCE_PIN_DRIFT:' + origin])
            records[origin] = load_json(p)['sources']
            if len(records[origin]) != n:
                return report(['SOURCE_ROWS_DRIFT:' + origin])
        index = source_index(records)
        dockets, errs = [], []
        article_dir = root/'preparedness/content/articles'
        tool_dir = root/'preparedness/content/tools'
        if len(list(article_dir.glob('*.meta.json'))) != 35:
            errs.append('ARTICLE_METADATA_COUNT_DRIFT')
        if len(list(tool_dir.glob('*.meta.json'))) != 6:
            errs.append('AUTHORED_TOOL_METADATA_COUNT_DRIFT')
        for kind, slugs, folder in (
            ('article', [row['slug'] for row in slate], article_dir),
            ('tool', [p.name[:-10] for p in sorted(tool_dir.glob('*.meta.json'))], tool_dir)):
            for slug in slugs:
                mpath = folder/(slug+'.meta.json')
                bpath = folder/(slug+'.body.html')
                if mpath.is_symlink() or bpath.is_symlink():
                    errs.append('SYMLINK_CONTENT:' + slug)
                    continue
                meta = load_json(mpath)
                if meta.get('slug') != slug:
                    errs.append('SLUG_MISMATCH:' + slug)
                result = check(meta, bpath.read_text('utf-8'), index)
                dockets.append({'kind': kind, **result})
                errs.extend(slug + ':' + err for err in result['errors'])
        if len(dockets) != 41:
            errs.append('TOTAL_DOCKET_COUNT_DRIFT')
        return report(errs, dockets)
    except (OSError, TypeError, ValueError, KeyError, UnicodeError) as exc:
        return report(['SOURCE_OR_CONTENT_PARSE_ERROR:' + type(exc).__name__])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(audit(args.repo_root), sort_keys=True, indent=2))
    raise SystemExit(2)  # HARD HOLD even if the structural checks are clean.
