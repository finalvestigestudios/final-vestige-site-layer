#!/usr/bin/env python3
"""R25: independent, read-only claim-to-source *review packet*, never a safety PASS.

Run on the complete, 81-file-frozen checkout after source_group_review_gate.
Every article-source relationship retains the contributor-specific source record,
full original supports/notes and article-specific source_use. No URL de-duping.
"""
from __future__ import annotations
from collections import Counter
import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys

CITE = re.compile(r'\{\{cite:([A-Za-z0-9_.-]+)\}\}')
EXPECTED = (35, 1, 1959, 367, 43, 30)

class ReviewHold(ValueError):
    """Missing or ambiguous evidence: this is not publication authorization."""

def need(ok, reason):
    if not ok:
        raise ReviewHold(reason)

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def excerpt(body, begin, end):
    # Context only; original HTML remains authoritative and frozen separately.
    before, after = body[max(0, begin - 210):begin], body[end:end + 210]
    before = re.sub(r'<[^>]*>', ' ', before)
    after = re.sub(r'<[^>]*>', ' ', after)
    return re.sub(r'\s+', ' ', html.unescape(before[-140:] + ' [CITATION] ' + after[:140])).strip()

def audit(lib, expected=EXPECTED):
    """Re-derive every citation occurrence and source binding from draft objects.

    expected = articles, tools, occurrences, relationships, base fallbacks,
    shared URLs. Only tests may override production frozen totals.
    """
    need(type(expected) is tuple and len(expected) == 6 and
         all(type(x) is int and x >= 0 for x in expected), 'invalid audit contract')
    origins = lib.article_origins
    articles = lib.articles
    need(type(origins) is dict and set(origins) == set(articles),
         'crosswalk origin map does not cover every article and tool')
    need(len(articles) == expected[0] + expected[1], 'article/tool count drift')
    need(len({a.get('slug') for a in articles.values()}) == len(articles) and
         all(a.get('slug') == s for s, a in articles.items()), 'article slug duplication')
    need(sum(a.get('kind') == 'tool' for a in articles.values()) == expected[1],
         'tool inventory drift')
    need(all(isinstance(k, str) and k and '/' not in k for k in articles),
         'unsafe article URL slug')
    urls = {}
    for versions in lib.source_variants.values():
        for v in versions:
            need(type(v.get('id')) is str and type(v.get('url')) is str and
                 v['url'].startswith('https://') and type(v.get('_origin')) is str,
                 'source ID, URL or original origin invalid')
            urls.setdefault(v['url'], []).append(v)
    collisions = {url for url, rows in urls.items() if len(rows) > 1}
    need(len(collisions) == expected[5] and set(lib.crosswalk_groups) == collisions,
         'shared URL review groups missing or silently collapsed')
    for url in collisions:
        g = lib.crosswalk_groups[url]
        need(g.get('review_status') == 'pending-human-source-and-reading-scope-review' and
             g.get('reviewer') is None and g.get('reviewed_on') is None,
             'shared URL group falsely marked reviewed')
    queue, total, fallback_count = [], 0, 0
    for slug, meta in sorted(articles.items()):
        origin = origins[slug]
        need(type(origin) is str and origin in {'base','start','shelter','food','health',
             'hist-food','hist-home','hist-field'}, 'unknown contributor origin')
        need(type(meta.get('status')) is dict and meta['status'].get('publish') == 'draft',
             'non-draft article or tool forbidden')
        body, uses = meta.get('_body'), meta.get('source_use')
        need(type(body) is str and type(uses) is dict,
             'article body or article-specific source-use missing')
        found = list(CITE.finditer(body))
        ids = {m.group(1) for m in found}
        need(ids == set(uses), 'citation/source_use map missing, extra or mismatched')
        need(all(type(s) is str and bool(s.strip()) for s in uses.values()),
             'blank or nontext reading-scope explanation')
        total += len(found)
        by_id = {}
        for m in found:
            by_id.setdefault(m.group(1), []).append(excerpt(body, m.start(), m.end()))
        for sid, contexts in sorted(by_id.items()):
            variants = lib.source_variants.get(sid)
            need(type(variants) is list and len(variants) >= 1, 'unknown source ID')
            own = [v for v in variants if v['_origin'] == origin]
            base = [v for v in variants if v['_origin'] == 'base']
            need(len(own) <= 1 and len(base) <= 1, 'ambiguous same-origin source variant')
            need(bool(own or base), 'source never read in own cluster or base')
            selected = own[0] if own else base[0]
            # Independent parity with the renderer's source-selection rule.
            need(lib.source_for(meta, sid)['_origin'] == selected['_origin'],
                 'rendered source provenance differs from audit')
            need(type(selected.get('verified_on')) is str and
                 bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', selected['verified_on'])),
                 'source has no machine verification date')
            need(type(selected.get('supports')) is str and bool(selected['supports'].strip()),
                 'original reading-depth evidence missing')
            is_fallback = selected['_origin'] != origin
            fallback_count += int(is_fallback)
            queue.append({'slug': slug, 'article_origin': origin,
                          'source_id': sid, 'source_origin': selected['_origin'],
                          'source_url': selected['url'], 'machine_verified_on': selected['verified_on'],
                          'base_fallback_requires_human_scope_review': is_fallback,
                          'shared_url_group_requires_human_review': selected['url'] in collisions,
                          'source_supports_as_recorded': selected['supports'],
                          'source_notes_as_recorded': selected.get('notes'),
                          'article_source_use_as_recorded': uses[sid],
                          'citation_occurrences': len(contexts),
                          'all_citation_contexts_for_human_claim_review': contexts,
                          'human_link_checked_by_this_gate': False,
                          'human_claim_reviewed_by_this_gate': False})
    need((len(articles) - expected[1], expected[1], total, len(queue),
          fallback_count, len(collisions)) == expected,
         'frozen 35+1 claim/source counts or base-fallback coverage changed')
    payload = {'schema_version': 1, 'issue': 136, 'release_state': 'HOLD',
               'may_publish': False, 'qualified_safety_clearance': False,
               'independent_QD_approval': False, 'human_source_reviews_completed': False,
               'source_claim_accuracy_verified': False,
               'machine_authority': 'STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY',
               'counts': {'articles': expected[0], 'tools': expected[1],
                          'citations': total, 'relationships': len(queue),
                          'base_fallback_relationships': fallback_count,
                          'shared_url_groups_unreviewed': len(collisions)},
               'review_queue': queue}
    payload['fingerprint_sha256'] = hashlib.sha256(canonical(payload)).hexdigest()
    return payload

def audit_checkout(root):
    root = Path(root)
    need(root.is_dir() and not root.is_symlink(), 'checkout unavailable or linked')
    root = root.resolve(strict=True)
    prep = root / 'preparedness'
    for part in ('taxonomy.json','sources/crosswalk.json','sources/register.json'):
        path = prep / part
        need(path.is_file() and not path.is_symlink() and
             path.resolve(strict=True).is_relative_to(prep), 'unsafe source input: ' + part)
    tool = prep / 'tools/build.py'
    need(tool.is_file() and not tool.is_symlink(), 'original renderer missing')
    spec = importlib.util.spec_from_file_location('preparedness_draft_build', tool)
    need(spec and spec.loader, 'renderer cannot be loaded')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return audit(module.Library(root=prep))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        print(json.dumps(audit_checkout(args.repo_root), sort_keys=True, ensure_ascii=False))
    except (ReviewHold, OSError, KeyError, TypeError, ValueError) as exc:
        print(f'citation source review HOLD: {exc}', file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
