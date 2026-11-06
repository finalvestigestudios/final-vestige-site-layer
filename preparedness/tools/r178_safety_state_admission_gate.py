#!/usr/bin/env python3
"""R178: read-only, 35-article safety-state and source-custody admission gate.

Historical 'approved' / 'not-required' metadata NEVER conveys independent QD,
medical/food safety approval or authority to publish. Entirely local; no CMS.
"""
from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SCHEMA = 'fv-preparedness-r178-35-safety-state-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
PIN_PATH = Path('preparedness/review/r178/safety_state_roster.json')
PIN_SHA256 = '0de619c749047cb3bac73e664df2b49d3b0ea8770ea00bef7a71ed6d1a9cd094'
CUSTODY_PATH = Path('preparedness/docs/r161/body_custody.json')
CUSTODY_GIT_BLOB = 'fede4222c796d92798eff7cf0dcb225c291f7d61'
ARTICLES = Path('preparedness/content/articles')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
FILE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
RELEASE_FLAGS = ('publication_authorized', 'independent_qd_pass',
                 'qualified_safety_review_complete')


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path: Path, limit: int = 1_000_000) -> tuple[dict, bytes]:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > limit:
        raise ValueError('missing, symlinked or oversized input: ' + str(path))
    raw = path.read_bytes()
    result = json.loads(raw.decode('utf-8'), object_pairs_hook=no_duplicate_keys)
    if not isinstance(result, dict):
        raise ValueError('JSON object required: ' + str(path))
    return result, raw


def require(condition: bool, why: str) -> None:
    if not condition:
        raise ValueError(why)


def validate_baseline(pins: dict, custody: dict) -> None:
    """Verify the original fixed reviewer-hold roster and R161 article custody."""
    require(pins.get('schema') == SCHEMA and pins.get('state') == HOLD,
            'unexpected safety baseline schema/state')
    require(all(pins.get(k) is False for k in RELEASE_FLAGS), 'false approval in baseline')
    require(pins.get('historical_labels_are_not_approvals') is True,
            'legacy labels presented as approvals')
    require(pins.get('r161_body_custody_blob') == CUSTODY_GIT_BLOB,
            'unexpected R161 custody identity')
    require(pins.get('expected_articles') == 35 and pins.get('expected_citations') == 2000
            and pins.get('expected_source_use') == 385, 'changed corpus invariant')
    require(pins.get('recorded_state_counts') == {'pending': 29, 'not-required': 4,
                                                  'approved': 2}, 'changed historical state counts')
    require(pins.get('legacy_approved_unverified') == ['making-water-safer',
              'salt-beef-salt-pork-age-of-sail'], 'unexpected legacy approval exceptions')
    require(pins.get('not_required_still_editorial_hold') == [
        'navigation-before-gps', 'pioneer-supply-chains-failed',
        'root-cellars-cool-storage', 'sanitation-before-germ-theory'],
        'unexpected editorial-review exception set')
    rows = pins.get('articles')
    require(isinstance(rows, list) and len(rows) == 35, 'missing 35 metadata pins')
    slugs = [row['slug'] for row in rows]
    require(slugs == sorted(set(slugs)) and all(FILE.fullmatch(s) for s in slugs),
            'missing, duplicate, unsorted or malformed metadata slugs')
    require(sorted(row['article_number'] for row in rows) == list(range(1, 36)),
            'article slate numbers changed')
    require(sum(row['source_use_count'] for row in rows) == 385,
            'source-use record count changed')
    require(Counter(row['recorded_state'] for row in rows) ==
            pins['recorded_state_counts'], 'unexpected per-article state distribution')
    require(all(re.fullmatch(r'[0-9a-f]{40}', row['meta_git_blob']) for row in rows),
            'malformed pinned metadata Git blob')
    require(custody.get('article_count') == 35 and
            custody.get('article_source_relationships') == 385,
            'R161 custody corpus count mismatch')
    originals = custody.get('articles')
    require(isinstance(originals, dict) and set(originals) == set(slugs),
            'R161 body custody roster mismatch')
    require(sum(v['citations'] for v in originals.values()) == 2000,
            'R161 citation count mismatch')
    require(all(re.fullmatch(r'[0-9a-f]{40}', v['git_blob']) for v in originals.values()),
            'invalid R161 original body Git blob')


def inspect(repo: Path, *, pins_sha256: str = PIN_SHA256,
            custody_git_blob: str = CUSTODY_GIT_BLOB) -> dict:
    """Read-only structural review. Test injections exist only in this Python API.

    CLI never exposes pin overrides and always returns exit 2, including a clean
    structural receipt. An error means INVALID_HARD_HOLD, not a partial PASS.
    """
    receipt = {'schema': SCHEMA, 'state': INVALID, 'publication_authorized': False,
               'independent_qd_pass': False, 'qualified_safety_review_complete': False,
               'medical_safety_approved': False, 'food_safety_approved': False,
               'source_claims_independently_adjudicated': False,
               'commercial_product_verified': False, 'human_review_admission': 'NONE',
               'article_count': 0, 'citations': 0, 'source_use': 0,
               'legacy_approved_unverified': [], 'not_required_editorial_hold': [],
               'errors': []}
    try:
        require(repo.is_dir() and not repo.is_symlink(), 'missing or symlinked checkout')
        pins, pins_raw = read_json(repo / PIN_PATH, 100_000)
        require(hashlib.sha256(pins_raw).hexdigest() == pins_sha256,
                'baseline safety-roster SHA-256 drift')
        custody, custody_raw = read_json(repo / CUSTODY_PATH)
        require(git_blob(custody_raw) == custody_git_blob, 'R161 body custody Git blob drift')
        validate_baseline(pins, custody)
        root = repo / ARTICLES
        require(root.is_dir() and not root.is_symlink(), 'missing or symlinked article directory')
        metas = {p.name[:-10] for p in root.glob('*.meta.json')}
        bodies = {p.name[:-10] for p in root.glob('*.body.html')}
        original = {row['slug'] for row in pins['articles']}
        require(metas == bodies == original, '35 original body/metadata pairs changed')
        seen_routes = set()
        total_cites = total_source_uses = 0
        for row in pins['articles']:
            slug = row['slug']
            meta, meta_raw = read_json(root / (slug + '.meta.json'))
            require(git_blob(meta_raw) == row['meta_git_blob'],
                    slug + ': metadata changed from source-reviewed baseline')
            path = root / (slug + '.body.html')
            require(path.is_file() and not path.is_symlink() and
                    path.stat().st_size <= 8_000_000, slug + ': missing/unsafe body file')
            raw = path.read_bytes()
            require(git_blob(raw) == custody['articles'][slug]['git_blob'],
                    slug + ': full original body changed, risking reading depth/warnings')
            body = raw.decode('utf-8')
            require(meta.get('slug') == slug and meta.get('n') == row['article_number'],
                    slug + ': article identity mismatch')
            require(meta.get('status', {}).get('publish') == 'draft',
                    slug + ': publication status is not draft')
            safety = meta.get('safety_review')
            require(isinstance(safety, dict) and
                    safety.get('state') == row['recorded_state'],
                    slug + ': recorded safety state changed')
            source_use = meta.get('source_use')
            require(isinstance(source_use, dict) and
                    len(source_use) == row['source_use_count'] and all(
                        isinstance(k, str) and k and isinstance(v, str) and v.strip()
                        for k, v in source_use.items()),
                    slug + ': author-scoped source relationship changed')
            cite_ids = CITE.findall(body)
            require(len(cite_ids) == custody['articles'][slug]['citations'],
                    slug + ': original citation count/order custody mismatch')
            require(set(cite_ids).issubset(source_use),
                    slug + ': cite token missing original author-scoped source interpretation')
            section = meta.get('section')
            require(isinstance(section, str) and FILE.fullmatch(section),
                    slug + ': invalid section')
            route = f'/preparedness/{section}/{slug}/'
            require(route not in seen_routes, slug + ': duplicate canonical route')
            seen_routes.add(route)
            # The historical label is evidence of editor bookkeeping ONLY.
            if safety['state'] == 'approved':
                note = str(safety.get('scope') or '').casefold()
                require('not an independent' in note and 'qd' in note and
                        'scope' in note, slug + ': ambiguous founder reply not disclaimed')
                receipt['legacy_approved_unverified'].append(slug)
            if safety['state'] == 'not-required':
                note = str(safety.get('scope') or '').casefold()
                require('review' in note or 'read' in note,
                        slug + ': editorial/read-through still needs a human')
                receipt['not_required_editorial_hold'].append(slug)
            total_cites += len(cite_ids)
            total_source_uses += len(source_use)
            receipt['article_count'] += 1
        require(total_cites == 2000 and total_source_uses == 385 and
                len(seen_routes) == 35, 'total citation/source/route invariant drift')
        require(sorted(receipt['legacy_approved_unverified']) ==
                pins['legacy_approved_unverified'], 'legacy approval exception mismatch')
        require(sorted(receipt['not_required_editorial_hold']) ==
                pins['not_required_still_editorial_hold'], 'editorial exception mismatch')
        receipt['citations'] = total_cites
        receipt['source_use'] = total_source_uses
        receipt['state'] = HOLD
    except (ValueError, KeyError, TypeError, UnicodeError, OSError, AttributeError) as exc:
        receipt['errors'].append(type(exc).__name__ + ': ' + str(exc))
    receipt['structural_receipt_only'] = True
    receipt['human_reviewer_required'] = True
    return receipt


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    print(json.dumps(inspect(args.repo.resolve()), sort_keys=True, separators=(',', ':')))
    return 2  # HOLD or INVALID_HOLD; never code 0 / release PASS.


if __name__ == '__main__':
    sys.exit(main())
