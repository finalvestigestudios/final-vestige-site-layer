#!/usr/bin/env python3
"""R10: canonical source re-derivation and no-release Preparedness claim ledger.

The R8 claim digest intentionally covers selected claim fields, not every displayed
field. R9 validates each request identity but (by design) does not authenticate a
human, verify a citation or bind inherited safety labels to current article metadata.
This gate solves that distinct trust-boundary issue: regenerate the WHOLE R8 report
from the frozen, current local article/source corpus and compare every field before
accepting any reviewer packet. No network access, WordPress writes, or approvals.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

BASE_ROUTE = '/preparedness/'
MIN_ARTICLE_WORDS = 1800
MIN_TOOL_WORDS = 450
EXPECTED_ARTICLES = 35
EXPECTED_TOOLS = {'water-planner'}
KNOWN_STATES = {'pending', 'approved', 'not-required'}


def word_count(body: str) -> int:
    """Mirror the original build.py word-token rule, excluding script/style."""
    if not isinstance(body, str) or '\x00' in body:
        raise ValueError('body: missing, nontext or NUL')
    body = re.sub(r'<(style|script)\b[^>]*>[\s\S]*?</\1\s*>', ' ', body, flags=re.I)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-]*", html.unescape(re.sub(r'<[^>]+>', ' ', body))))


def first_diff(actual, expected, loc='$') -> str | None:
    """Return the first differing JSON location, not potentially private content."""
    if type(actual) is not type(expected):
        return f'{loc}: type differs'
    if isinstance(expected, dict):
        if actual.keys() != expected.keys():
            missing = sorted(expected.keys() - actual.keys())
            added = sorted(actual.keys() - expected.keys())
            return f'{loc}: keys changed (+{added[:5]}, -{missing[:5]})'
        for k in sorted(expected):
            diff = first_diff(actual[k], expected[k], f'{loc}.{k}')
            if diff:
                return diff
        return None
    if isinstance(expected, list):
        if len(actual) != len(expected):
            return f'{loc}: array length differs ({len(actual)} != {len(expected)})'
        for i, (v, w) in enumerate(zip(actual, expected)):
            diff = first_diff(v, w, f'{loc}[{i}]')
            if diff:
                return diff
        return None
    return None if actual == expected else f'{loc}: value differs'


def verify_editorial_corpus(lib, *, article_floor=MIN_ARTICLE_WORDS, tool_floor=MIN_TOOL_WORDS,
                            expected_articles=EXPECTED_ARTICLES, expected_tools=EXPECTED_TOOLS) -> dict:
    """Protect 35+1 draft slugs, sections, tracks, routes and long-form depth."""
    taxonomy = lib.taxonomy
    if not isinstance(taxonomy, dict) or taxonomy.get('base_path') != BASE_ROUTE:
        raise ValueError('taxonomy: unexpected Preparedness base path')
    slate = taxonomy.get('slate')
    if not isinstance(slate, list) or len(slate) != expected_articles:
        raise ValueError('taxonomy: 35-article slate drift')
    if any(not isinstance(x, dict) or not isinstance(x.get('slug'), str) for x in slate):
        raise ValueError('taxonomy: malformed slate entry')
    slugs = [x['slug'] for x in slate]
    if len(slugs) != len(set(slugs)):
        raise ValueError('taxonomy: duplicate article slug')
    if set(expected_tools) & set(slugs):
        raise ValueError('taxonomy: tool collides with article')
    tools = taxonomy.get('tools')
    if not isinstance(tools, list) or not expected_tools <= {x.get('slug') for x in tools if isinstance(x, dict)}:
        raise ValueError('taxonomy: water planner tool missing')
    tool_slugs = [x.get('slug') for x in tools if isinstance(x, dict)]
    if len(tool_slugs) != len(set(tool_slugs)):
        raise ValueError('taxonomy: duplicate tool slug')
    if set(lib.articles) != set(slugs) | set(expected_tools):
        raise ValueError('corpus: missing, extra or duplicated draft inputs')
    sections = {x.get('slug') for x in taxonomy.get('sections', []) if isinstance(x, dict)}
    if len(sections) != len(taxonomy.get('sections', [])) or not sections:
        raise ValueError('taxonomy: duplicate or malformed sections')
    routes, states, depths, track_counts = set(), Counter(), {}, Counter()
    for item in slate + [x for x in tools if x.get('slug') in expected_tools]:
        slug = item['slug']
        meta = lib.articles[slug]
        if meta.get('slug') != slug or not isinstance(meta.get('_body'), str):
            raise ValueError(f'{slug}: slug/body/metadata mismatch')
        if meta.get('section') not in sections or item.get('section', meta.get('section')) != meta.get('section'):
            raise ValueError(f'{slug}: section drift')
        if slug in slugs and (meta.get('track') != item.get('track') or meta.get('n') != item.get('n')):
            raise ValueError(f'{slug}: editorial slate ordering or track drift')
        if meta.get('status', {}).get('publish') != 'draft':
            raise ValueError(f'{slug}: publish state must remain draft')
        safety = meta.get('safety_review', {})
        state = safety.get('state')
        if state not in KNOWN_STATES:
            raise ValueError(f'{slug}: unknown safety state')
        if state == 'not-required' and meta.get('track') != 'lost-ways':
            raise ValueError(f'{slug}: modern emergency guidance cannot bypass safety review')
        if slug in expected_tools and meta.get('kind') != 'tool':
            raise ValueError(f'{slug}: tool identity lost')
        route = lib.url_path(slug)
        expected_route = f"{BASE_ROUTE}{meta['section']}/{slug}/"
        if route != expected_route or route in routes:
            raise ValueError(f'{slug}: duplicate or changed URL route')
        routes.add(route)
        count = word_count(meta['_body'])
        if count < (tool_floor if slug in expected_tools else article_floor):
            raise ValueError(f'{slug}: long-form reading-depth regression ({count} words)')
        depths[slug] = count
        states[state] += 1
        track_counts[meta['track']] += 1
    if track_counts['modern'] < 20 or track_counts['lost-ways'] < 15:
        raise ValueError('corpus: modern and historical tracks must both remain complete')
    return {'draft_items': len(lib.articles), 'article_drafts': len(slugs),
            'tool_drafts': len(expected_tools), 'unique_routes': len(routes),
            'safety_state_labels_not_independent_approval': dict(sorted(states.items())),
            'track_counts': dict(sorted(track_counts.items())),
            'shortest_article_words': min(depths[x] for x in slugs),
            'planner_words': depths[next(iter(sorted(expected_tools)))]}


def verify_physical_source_custody(rows: list[dict], expected_count: int = 224,
                                   expected_repeated_url_groups: int = 30, expected_distinct_urls: int = 186) -> dict:
    """Source origin/row keys are physical evidence; same URLs do NOT imply same reading."""
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise ValueError('source: expected physical row inventory changed')
    seen_keys, urls = set(), Counter()
    unread_base_placeholders = 0
    for r in rows:
        if not isinstance(r, dict) or any(not isinstance(r.get(k), str) or not r[k].strip()
                                            for k in ('row_key','origin','source_id','url')):
            raise ValueError('source: malformed physical reading record')
        support = r.get('supports')
        if not isinstance(support, str) or not support.strip():
            # The original base register deliberately retains 15 *unread* source
            # placeholders. They are not contributor evidence and cannot be cited
            # as verified. Do not reject them merely because their supports are
            # empty, but never permit a dated or mislabelled placeholder through.
            if (r['origin'] != 'base' or r.get('verified_on') or r.get('human_link_check')
                    or 'not yet read' not in str(r.get('reading_limits') or '').lower()
                    or support not in (None, '')):
                raise ValueError('source: unverified placeholder lacks explicit base custody or has approval markers')
            unread_base_placeholders += 1
        if r['row_key'] in seen_keys or not r['row_key'].startswith(r['origin'] + ':'):
            raise ValueError('source: duplicate or misattributed physical source row')
        if not isinstance(r['url'], str) or any(ord(ch) <= 32 for ch in r['url']) or '\\' in r['url']:
            raise ValueError('source: invalid HTTPS URL')
        try:
            u = urlsplit(r['url'])
            if u.scheme != 'https' or not u.hostname or u.username or u.password or u.port not in (None,443) or '@' in u.netloc:
                raise ValueError('bad URL')
        except ValueError as exc:
            raise ValueError('source: invalid HTTPS URL') from exc
        seen_keys.add(r['row_key'])
        urls[r['url']] += 1
    collisions = sum(n > 1 for n in urls.values())
    if collisions != expected_repeated_url_groups:
        raise ValueError('source: shared URL groups changed without review')
    if len(urls) != expected_distinct_urls:
        raise ValueError('source: distinct literal URL inventory changed without review')
    if expected_count == 224 and unread_base_placeholders != 15:
        raise ValueError('source: 15 original unread base placeholders must remain explicit and unverified')
    return {'physical_source_records': len(rows), 'literal_urls': len(urls),
            'repeated_url_groups_UNRESOLVED': collisions,
            'unread_base_placeholders_NOT_VERIFIED': unread_base_placeholders}


def audit_corpus(lib, rows, fingerprint, *, supplied_report=None, response_bundle=None,
                 today: date | None = None, make_report=None, review_audit=None,
                 baseline=None, article_floor=MIN_ARTICLE_WORDS, tool_floor=MIN_TOOL_WORDS,
                 expected_articles=EXPECTED_ARTICLES, expected_tools=EXPECTED_TOOLS,
                 expected_rows=224, expected_url_groups=30, expected_urls=186) -> dict:
    """Rebuild *all* authoritatively sourced fields before intake; never approve anything."""
    if make_report is None or review_audit is None or baseline is None:
        # Imports are deferred to let synthetic fixtures exercise the trust
        # boundary without pretending the private full repository was cloned.
        import claim_occurrence_audit as r8
        import claim_review_intake as r9
        make_report = make_report or r8.make_report
        review_audit = review_audit or r9.audit
        baseline = baseline if baseline is not None else r8.BASELINE
    editorial = verify_editorial_corpus(lib, article_floor=article_floor, tool_floor=tool_floor,
                                        expected_articles=expected_articles, expected_tools=expected_tools)
    source = verify_physical_source_custody(rows, expected_rows, expected_url_groups, expected_urls)
    canonical = make_report(lib, rows=rows, fingerprint=fingerprint, expect=baseline)
    if not isinstance(canonical, dict):
        raise ValueError('canonical: report generator returned malformed result')
    if supplied_report is not None:
        difference = first_diff(supplied_report, canonical)
        if difference is not None:
            raise ValueError(f'canonical corpus/report divergence at {difference} — stale or altered evidence')
    if canonical.get('release_state') != 'HOLD' or canonical.get('may_publish') is not False:
        raise ValueError('canonical: publishing or safety truth violation')
    if canonical.get('counts', {}).get('draft_items') != editorial['draft_items']:
        raise ValueError('canonical: draft inventory mismatch')
    if canonical.get('counts', {}).get('physical_source_rows') != source['physical_source_records']:
        raise ValueError('canonical: source inventory mismatch')
    if canonical.get('counts', {}).get('shared_url_groups') != source['repeated_url_groups_UNRESOLVED']:
        raise ValueError('canonical: repeated-URL inventory mismatch')
    if canonical.get('inherited_safety_states') != editorial['safety_state_labels_not_independent_approval']:
        raise ValueError('canonical: inherited safety labels inconsistent with exact metadata')
    claims = canonical.get('claims')
    if not isinstance(claims, list) or len(claims) != canonical['counts'].get('citation_occurrences'):
        raise ValueError('canonical: claim count mismatch')
    state_by_slug = {slug: meta['safety_review']['state'] for slug, meta in lib.articles.items()}
    for c in claims:
        if c.get('article') not in state_by_slug or c.get('inherited_safety_state') != state_by_slug[c['article']]:
            raise ValueError('canonical: claim inherited safety state differs from article metadata')
    if response_bundle is None:
        response_bundle = {'schema_version': 1, 'parent_evidence_digest_sha256': canonical['evidence_digest_sha256'],
                           'claim_responses': []}
    reviewed = review_audit(canonical, response_bundle, today=today, expected_counts=baseline, source_rows=rows)
    if (reviewed.get('release_state') != 'HOLD' or reviewed.get('may_publish') is not False
            or reviewed.get('independent_human_source_checks_verified') != 0
            or reviewed.get('qualified_safety_approvals') != 0):
        raise ValueError('intake: unexpected approval/verification authority')
    return {'schema_version': 1, 'authority': 'MACHINE_CANONICAL_CUSTODY_ONLY',
            'release_state': 'HOLD', 'may_publish': False,
            'no_wordpress_or_public_writes': True,
            'independent_human_source_checks_verified': 0, 'qualified_safety_approvals': 0,
            'source_content_digest_sha256': hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False,
                                                                     separators=(',', ':')).encode('utf-8')).hexdigest(),
            'evidence_digest_sha256': canonical['evidence_digest_sha256'],
            'response_digest_sha256': reviewed['response_digest_sha256'],
            'editorial': editorial, 'sources': source, 'review_counts': reviewed['counts'],
            'article_review_counts': reviewed['articles'],
            'reviewer_reports_are_self_assertions_only': True,
            'all_shared_url_groups_require_human_reconciliation': True}


def read_private_json(p: Path, root: Path, max_bytes=8 * 1024 * 1024):
    root = root.resolve(strict=True)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > max_bytes or p.stat().st_size < 2:
        raise ValueError('input: private file unavailable, symlink or oversized')
    resolved = p.resolve(strict=True)
    if not resolved.is_relative_to(root) or resolved.parent != root:
        raise ValueError('input: JSON must be a direct file in private preparedness/build')
    data = json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('input: expected JSON object')
    return data


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--report', type=Path, help='Optional prior R8 report in private build; recomputed and compared field-for-field')
    ap.add_argument('--responses', type=Path, help='Optional untrusted reviewer reports in private build; cannot grant release')
    ap.add_argument('--json-out', type=Path, help='Private HOLD-only evidence closure receipt in preparedness/build')
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tools'))
    import build, evidence_freeze, source_review_queue, validate, claim_occurrence_audit as r8
    lib = build.Library(root)
    locked_errors = evidence_freeze.verify(lib)
    if locked_errors:
        raise ValueError('evidence lock: ' + '; '.join(locked_errors[:5]))
    validation_errors, _warnings = validate.validate(lib)
    if validation_errors:
        raise ValueError('native validator: ' + '; '.join(validation_errors[:5]))
    private_root = root / 'build'
    if not private_root.is_dir():
        raise ValueError('private build/ directory required, no implicit public write')
    report = read_private_json(args.report, private_root) if args.report else None
    responses = read_private_json(args.responses, private_root) if args.responses else None
    result = audit_corpus(lib, source_review_queue.source_rows(root), evidence_freeze.fingerprint,
                          supplied_report=report, response_bundle=responses)
    if args.json_out:
        r8.safe_export(args.json_out, json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2)+'\n', private_root)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
