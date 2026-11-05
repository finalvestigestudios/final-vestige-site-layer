#!/usr/bin/env python3
"""R139 read-only independent article depth/citation census. NEVER grants release.

Before measuring depth, require R133 immutable Git-blob custody and visible citations.
This is a regression guard against accidental article truncation during an APPROVED
future rebaseline, not source, medical, commercial, editorial, or QD review.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
from collections import Counter

CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
WORD = re.compile(r"\b[\w]+(?:[’'\-][\w]+)*\b", re.UNICODE)
HOLD = 'DRAFT_HOLD_INDEPENDENT_REVIEW_REQUIRED'

class DepthHold(ValueError):
    pass

def need(value, reason):
    if not value:
        raise DepthHold(reason)

def approx_words(body: str) -> int:
    """Approximate prose, not a readability, evidence, or safety judgment."""
    no_tags = re.sub(r'<[^>]*>', ' ', body)
    no_cites = CITE.sub(' ', no_tags)
    return len(WORD.findall(no_cites))

def inspect(slug: str, meta: dict, body: str) -> dict:
    cited = CITE.findall(body)
    used = meta.get('source_use')
    need(isinstance(used, dict) and
         set(used) == set(cited) and
         all(isinstance(v, str) and v.strip() for v in used.values()),
         'MISSING_AUTHOR_SOURCE_SCOPE:' + slug)
    need('{{cite:' not in CITE.sub('', body), 'MALFORMED_CITATION:' + slug)
    return {'slug': meta.get('slug'), 'observed_prose_words': approx_words(body),
            'citation_occurrences': len(cited), 'source_use_ids': len(used),
            'historical_safety_state': (meta.get('safety_review') or {}).get('state'),
            'publish': (meta.get('status') or {}).get('publish'),
            'editorial': (meta.get('status') or {}).get('editorial')}

def check_census(census: dict, observed: list[dict]) -> dict:
    need(isinstance(census, dict) and census.get('schema_version') == 1 and
         census.get('status') == HOLD, 'CENSUS_NOT_DRAFT_HOLD')
    for key in ('may_publish','qd_pass','medical_safety_verified','merchant_offer_verified'):
        need(census.get(key) is False, 'FORGED_APPROVAL:' + key)
    require_parent = 'preparedness/docs/r133/locked_files.json'
    need(census.get('parent_r133_manifest') == require_parent and
         census.get('source_ref') == '5ea94442b56ec040e8846d784032d38200cd7dae',
         'CENSUS_PARENT_REF_DRIFT')
    rows = census.get('articles')
    need(isinstance(rows, list) and len(rows) == 35 and
         isinstance(observed, list) and len(observed) == 35,
         'ARTICLE_CENSUS_NOT_35')
    declared, seen = {}, {}
    for row in rows:
        need(isinstance(row, dict) and isinstance(row.get('slug'), str) and row['slug'] and
             row['slug'] not in declared, 'MALFORMED_OR_DUPLICATE_CENSUS_SLUG')
        declared[row['slug']] = row
    for row in observed:
        need(isinstance(row, dict) and isinstance(row.get('slug'), str) and row['slug'] and
             row['slug'] not in seen, 'MALFORMED_OR_DUPLICATE_ARTICLE_SLUG')
        seen[row['slug']] = row
    need(set(declared) == set(seen), 'ARTICLE_ROSTER_DRIFT')
    for slug, target in declared.items():
        actual = seen[slug]
        need(target.get('historical_safety_state') in ('pending','approved','not-required') and
             actual.get('historical_safety_state') == target['historical_safety_state'],
             'SAFETY_STATE_DRIFT:' + slug)
        need(actual.get('publish') == 'draft' and actual.get('editorial') == 'drafted',
             'PUBLICATION_STATE_DRIFT:' + slug)
        need(type(target.get('minimum_prose_words')) is int and
             target['minimum_prose_words'] >= 500 and
             type(actual.get('observed_prose_words')) is int and
             actual['observed_prose_words'] >= target['minimum_prose_words'],
             'ARTICLE_READING_DEPTH_LOSS:' + slug)
        for key in ('citation_occurrences','source_use_ids'):
            need(type(target.get(key)) is int and
                 type(actual.get(key)) is int and actual[key] == target[key],
                 'ARTICLE_EVIDENCE_DRIFT:' + slug + ':' + key)
    totals = census.get('totals')
    need(isinstance(totals, dict) and totals.get('article_count') == 35 and
         totals.get('citation_occurrences') == sum(r['citation_occurrences'] for r in rows) == 2000 and
         totals.get('author_source_use_bindings') == sum(r['source_use_ids'] for r in rows) == 385,
         'CENSUS_TOTALS_DRIFT')
    states = dict(Counter(r['historical_safety_state'] for r in rows))
    need(states == totals.get('historical_safety_states') ==
         {'pending': 29, 'approved': 2, 'not-required': 4}, 'FROZEN_SAFETY_STATES_DRIFT')
    return {'status': 'HOLD_UNREVIEWED_SAFETY_SOURCES_INDEPENDENT_QD',
            'article_count': 35, 'citation_occurrences': 2000,
            'author_source_use_bindings': 385,
            'articles_with_reading_depth_floor_met': 35,
            'may_publish': False, 'qd_pass': False,
            'medical_safety_verified': False, 'merchant_offer_verified': False,
            'note': 'Prose depth and citation counts are structural evidence only; never a safety or source endorsement.'}

def audit_repository(root: Path, census: dict) -> dict:
    root = Path(root)
    # Strictly enforce R133 exact Git object custody BEFORE evaluating content.
    sys.path.insert(0, str(Path(__file__).resolve().parent))  # compatible with python -I
    from r133_snapshot_gate import audit as custody_audit, load_json
    frozen = load_json((root / census['parent_r133_manifest']).read_bytes())
    custody_audit(root, frozen)
    article_dir = root / 'preparedness/content/articles'
    meta_paths = sorted(article_dir.glob('*.meta.json'))
    body_paths = sorted(article_dir.glob('*.body.html'))
    need(len(meta_paths) == len(body_paths) == 35, 'MISSING_OR_EXTRA_ARTICLE')
    observed = []
    for mp in meta_paths:
        slug = mp.name[:-10]
        body_file = article_dir / (slug + '.body.html')
        need(body_file.is_file(), 'MISSING_ARTICLE_BODY:' + slug)
        meta = json.loads(mp.read_text(encoding='utf-8'))
        observed.append(inspect(slug, meta, body_file.read_text(encoding='utf-8')))
    return check_census(census, observed)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--census', type=Path,
                        default=Path('preparedness/docs/r139/article_depth_census.json'))
    args = parser.parse_args(argv)
    try:
        census = json.loads((args.root / args.census).read_text(encoding='utf-8'))
        print(json.dumps(audit_repository(args.root, census), sort_keys=True, indent=2))
        return 0
    except (DepthHold, ValueError, KeyError, TypeError, ImportError, OSError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
