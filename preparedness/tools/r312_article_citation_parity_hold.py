#!/usr/bin/env python3
"""Read-only R312: all 35 articles, source-use citations, context and routes.

Integrates R306 frozen-lineage input custody with R311 six-tool source custody.
This gate NEVER approves a claim, a medical action, a paid offer or publication.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('r311_source_gate', HERE / 'r311_cited_source_crosswalk_hold.py')
r311 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r311)
r310 = r311.r310
SCHEMA = 'fv-preparedness-r312-35-article-citation-context-crosswalk-v1'
LEDGER = 'preparedness/audits/r306_live_lineage_35_articles_HARD_HOLD.json'
LEDGER_OID = 'c7ab84eeacbd43f17bb3cab72a888430cb102f25'
CITATIONS = re.compile(r'\{\{cite:([^{}]*)\}\}')
LINKS = re.compile(r'\{\{link:([^{}]*)\}\}')
SOURCE_ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
ROUTE = re.compile(r'/preparedness/(?:[a-z0-9-]+/)+\Z')


def inspect_pair(slug: str, body: str, meta: object, known_targets: set[str]) -> tuple[list[str], dict]:
    """Pure validator: no filesystem, no source rewriting, no approval side effects."""
    errors: list[str] = []
    if not isinstance(meta, dict):
        return ['META_NOT_OBJECT:' + slug], {'slug': slug, 'cited_ids': [], 'citation_occurrences': 0, 'context_witnesses': []}
    if meta.get('slug') != slug:
        errors.append('METADATA_SLUG_DRIFT:' + slug)
    status = meta.get('status')
    if not isinstance(status, dict) or status.get('publish') != 'draft':
        errors.append('ARTICLE_NOT_DRAFT:' + slug)
    safety = meta.get('safety_review')
    if not isinstance(safety, dict) or safety.get('state') in ('approved', 'passed', 'cleared'):
        errors.append('UNAUTHORIZED_SAFETY_APPROVAL:' + slug)
    uses = meta.get('source_use')
    if not isinstance(uses, dict):
        errors.append('SOURCE_USE_NOT_OBJECT:' + slug)
        uses = {}
    elif any(not isinstance(k, str) or not SOURCE_ID.fullmatch(k) or
             not isinstance(v, str) or not v.strip() for k, v in uses.items()):
        errors.append('SOURCE_USE_INVALID_ENTRY:' + slug)
    tokens = list(CITATIONS.finditer(body))
    if body.count('{{cite:') != len(tokens):
        errors.append('MALFORMED_CITATION_TOKEN:' + slug)
    ids = [m.group(1) for m in tokens]
    if any(not SOURCE_ID.fullmatch(x) for x in ids):
        errors.append('MALFORMED_CITATION_ID:' + slug)
    absent_meta = sorted(set(ids) - set(uses))
    absent_body = sorted(set(uses) - set(ids))
    if absent_meta:
        errors.append('CITATION_NOT_DECLARED:' + slug + ':' + ','.join(absent_meta))
    if absent_body:
        errors.append('SOURCE_USE_WITHOUT_CITATION:' + slug + ':' + ','.join(absent_body))
    link_tokens = list(LINKS.finditer(body))
    if body.count('{{link:') != len(link_tokens):
        errors.append('MALFORMED_INTERNAL_LINK_TOKEN:' + slug)
    links = [x.group(1).split('|', 1)[0] for x in link_tokens]
    if any(not SOURCE_ID.fullmatch(x) for x in links):
        errors.append('MALFORMED_INTERNAL_LINK_TARGET:' + slug)
    unknown = sorted(set(links) - known_targets)
    if unknown:
        errors.append('UNRESOLVED_AUTHORED_LINK:' + slug + ':' + ','.join(unknown))
    witnesses = []
    for m in tokens:
        # Hash adjoining author markup to tie each citation to its claim context;
        # this is a navigation/debug witness, NOT evidence that a claim is true.
        preceding = re.sub(r'<[^>]*>', ' ', body[max(0, m.start()-240):m.start()])
        preceding = re.sub(r'\s+', ' ', preceding).strip()
        digest = hashlib.sha256(preceding[-160:].encode('utf-8')).hexdigest()
        witnesses.append({'source_id': m.group(1), 'prior_text_sha256': digest,
                          'occurrence_ordinal': len(witnesses) + 1})
    return errors, {'slug': slug, 'cited_ids': sorted(set(ids)),
                    'citation_occurrences': len(ids), 'metadata_source_ids': sorted(uses),
                    'authored_link_targets': sorted(set(links)), 'context_witnesses': witnesses,
                    'status_publish': status.get('publish') if isinstance(status, dict) else None,
                    'safety_state': safety.get('state') if isinstance(safety, dict) else None}


def audit_articles(root: Path, ledger: dict, *, require_pins: bool = True) -> dict:
    errors: list[str] = []
    articles = ledger.get('articles') if isinstance(ledger, dict) else None
    if not isinstance(articles, list) or len(articles) != 35:
        errors.append('EXACTLY_35_ARTICLES_REQUIRED')
        articles = articles if isinstance(articles, list) else []
    slugs = [r.get('slug') for r in articles if isinstance(r, dict)]
    if len(slugs) != 35 or len(set(slugs)) != 35 or any(not isinstance(s, str) or not SOURCE_ID.fullmatch(s) for s in slugs):
        errors.append('MISSING_DUPLICATE_OR_MALFORMED_ARTICLE_SLUG')
    target_slugs = set(slugs) | set(r310.SLUGS)
    routes = [r.get('route') for r in articles if isinstance(r, dict)]
    if len(set(routes)) != 35 or any(not isinstance(r, str) or not ROUTE.fullmatch(r) for r in routes):
        errors.append('DUPLICATE_OR_MALFORMED_CANONICAL_ROUTE')
    expected_files = {s + ext for s in slugs if isinstance(s, str) for ext in ('.body.html', '.meta.json')}
    directory = root / 'preparedness/content/articles'
    observed_files = {p.name for p in directory.iterdir()} if directory.is_dir() and not directory.is_symlink() else set()
    if observed_files != expected_files:
        errors.append('ARTICLE_INPUT_SET_DRIFT')
    entries = []
    files_ok = 0
    for row in articles:
        if not isinstance(row, dict) or not isinstance(row.get('slug'), str) or not SOURCE_ID.fullmatch(row['slug']):
            errors.append('INVALID_ARTICLE_LEDGER_ROW')
            continue
        slug = row['slug']
        body_path = f'preparedness/content/articles/{slug}.body.html'
        meta_path = f'preparedness/content/articles/{slug}.meta.json'
        pair = []
        for path, key in ((body_path, 'integrated_body_blob'), (meta_path, 'integrated_meta_blob')):
            b = r310.file_bytes(root, path)
            if b is None:
                errors.append('ARTICLE_INPUT_MISSING_OR_SYMLINK:' + path)
            elif require_pins and r310.oid(b) != row.get(key):
                errors.append('ARTICLE_INTEGRATED_BLOB_DRIFT:' + path)
            else:
                files_ok += 1
            pair.append(b)
        if None in pair:
            continue
        try:
            body = pair[0].decode('utf-8')
            meta = json.loads(pair[1].decode('utf-8'))
        except (UnicodeError, json.JSONDecodeError):
            errors.append('ARTICLE_BAD_ENCODING_OR_METADATA:' + slug)
            continue
        issues, item = inspect_pair(slug, body, meta, target_slugs)
        errors.extend(issues)
        entries.append(item)
    return {'schema': SCHEMA,
            'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors': sorted(set(errors)), 'article_count': len(entries),
            'verified_article_input_blobs': files_ok,
            'citation_occurrences': sum(e['citation_occurrences'] for e in entries),
            'distinct_cited_source_ids': sorted({s for e in entries for s in e['cited_ids']}),
            'article_source_context_crosswalk': entries,
            'publication_authorized': False, 'independent_qd_pass': False,
            'medical_safety_verified': False, 'actual_41_wordpress_drafts_verified': False,
            'paid_offer_approved': False, 'merchant_paid_orders_verified': False}


def source_coverage(article_rows: list[dict], source_payloads: dict[str, object]) -> dict:
    """Cross-check article citations against fetched records; no human safety assertion."""
    records: dict[str, list[dict]] = {}
    problems: list[str] = []
    for filename, payload in sorted(source_payloads.items()):
        if not isinstance(payload, dict) or not isinstance(payload.get('sources'), list):
            problems.append('SOURCE_FRAGMENT_UNREADABLE:' + filename)
            continue
        for src in payload['sources']:
            if not isinstance(src, dict) or not isinstance(src.get('id'), str):
                problems.append('SOURCE_FRAGMENT_RECORD_INVALID:' + filename)
                continue
            records.setdefault(src['id'], []).append(src)
    not_registered = []
    not_fetched = []
    multiple_fetched = []
    awaiting_human = []
    for sid in sorted({sid for row in article_rows for sid in row['cited_ids']}):
        candidates = records.get(sid, [])
        fetched = [r for r in candidates if isinstance(r.get('verified_on'), str) and r['verified_on']]
        if not candidates:
            not_registered.append(sid)
        elif not fetched:
            not_fetched.append(sid)
        else:
            if len(fetched) > 1:
                multiple_fetched.append(sid)
            if not any(r.get('human_link_check') is True for r in fetched):
                awaiting_human.append(sid)
    problems.extend('ARTICLE_CITED_SOURCE_NOT_REGISTERED:' + s for s in not_registered)
    problems.extend('ARTICLE_CITED_SOURCE_NOT_FETCH_VERIFIED:' + s for s in not_fetched)
    problems.extend('ARTICLE_MULTIPLE_FETCHED_SOURCE_RECORDS:' + s for s in multiple_fetched)
    return {'errors': sorted(set(problems)), 'unregistered': not_registered,
            'not_machine_fetched': not_fetched,
            'competing_fetched_records': multiple_fetched,
            'no_human_link_witness': awaiting_human,
            'human_safety_review_passed': False}


def run(root: Path) -> dict:
    raw = r310.file_bytes(root, LEDGER)
    if raw is None or r310.oid(raw) != LEDGER_OID:
        raise ValueError('R306_AUTHENTIC_LEDGER_UNAVAILABLE_OR_CHANGED')
    prior = r311.audit(root)
    current = audit_articles(root, json.loads(raw.decode('utf-8')))
    payloads = {}
    for source_path in r311.SOURCES:
        data = r310.file_bytes(root, source_path)
        if data is None:
            payloads[source_path] = None
        else:
            try:
                payloads[source_path] = json.loads(data.decode('utf-8'))
            except (UnicodeError, json.JSONDecodeError):
                payloads[source_path] = None
    coverage = source_coverage(current['article_source_context_crosswalk'], payloads)
    current['article_source_coverage'] = coverage
    current['errors'].extend(coverage['errors'])
    if coverage['errors']:
        current['errors'] = sorted(set(current['errors']))
        current['state'] = 'INVALID_HARD_HOLD'
    current['inherited_r311_state'] = prior['state']
    current['inherited_r311_errors'] = prior['errors']
    if prior['errors']:
        current['errors'].extend('INHERITED_R311:' + x for x in prior['errors'])
        current['errors'] = sorted(set(current['errors']))
        current['state'] = 'INVALID_HARD_HOLD'
    # No result state is a green light. Independently verified article claims
    # and all 41 real WordPress draft exports remain release dependencies.
    return current


def main() -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = p.parse_args()
    try:
        result = run(args.root)
    except (OSError, ValueError, TypeError, UnicodeError, KeyError) as e:
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'errors': ['CHECKOUT_OR_LEDGER_UNAVAILABLE:' + type(e).__name__],
                  'publication_authorized': False, 'independent_qd_pass': False,
                  'medical_safety_verified': False}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 1 if result['state'] == 'INVALID_HARD_HOLD' else 2


if __name__ == '__main__':
    raise SystemExit(main())
