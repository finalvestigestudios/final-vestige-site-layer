#!/usr/bin/env python3
"""Fail-closed audit joining R135 passage/source tasks with R137 author dossiers.

All evidence is derived from the frozen 35-article Preparedness candidate. This is
structural reconciliation, not source agreement, medical approval, QD or release.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

HOLD = 'HOLD_INDEPENDENT_SOURCE_SAFETY_QD_AND_RELEASE_REQUIRED'


class ReconciliationHold(ValueError):
    """A missing, conflicting, incomplete or prematurely approved evidence link."""


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ReconciliationHold(code)


def fingerprint(data: object) -> str:
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def cited_identity(v: dict) -> tuple[str, str, str]:
    return v['origin'], v['id'], v['literal_url']


def reconcile(queue: dict, scope: dict) -> dict:
    """Compare independent R135 and R137 outputs without equating review groups.

    R135 crosswalk indices follow the original crosswalk order. R137 indices
    follow sorted URL aliases. Match actual (origin, source ID, literal URL)
    identities instead of assuming those two group indices are identical.
    """
    require(isinstance(queue, dict) and isinstance(scope, dict), 'INPUTS_NOT_OBJECTS')
    require(queue.get('status') == 'HOLD_HUMAN_SOURCE_AND_SAFETY_ADJUDICATION' and
            scope.get('status') == 'HOLD_QUALIFIED_SOURCE_AND_SAFETY_REVIEW_REQUIRED',
            'UPSTREAM_REVIEW_HOLD_REQUIRED')
    for obj in (queue, scope):
        for field in ('may_publish', 'qd_pass', 'medical_safety_verified',
                      'merchant_offer_verified'):
            require(obj.get(field) is False, 'FORGED_UPSTREAM_APPROVAL:' + field)
    p, qstats, stats = queue.get('provenance'), queue.get('summary'), scope.get('stats')
    require(isinstance(p, dict) and isinstance(qstats, dict) and isinstance(stats, dict),
            'MISSING_EVIDENCE_COUNTS')
    require(p.get('candidate_parent') == scope.get('candidate_parent') and
            isinstance(scope.get('candidate_parent'), str) and scope['candidate_parent'],
            'DIFFERENT_FROZEN_CANDIDATES')
    require(p.get('article_count') == stats.get('articles') == 35 and
            p.get('citation_occurrences') == stats.get('citations') == 2000 and
            qstats.get('crosswalk_groups_requiring_human_review') ==
            stats.get('shared_groups') == 32 and stats.get('source_rows') == 244 and
            stats.get('frozen_files') == 80, 'ARCHIVE_CENSUS_NOT_FROZEN')
    require(stats.get('literal_source_urls') == 202 and
            stats.get('review_aliases') == 201, 'SOURCE_ALIAS_CENSUS_DRIFT')
    articles = scope.get('articles')
    require(isinstance(articles, list) and len(articles) == 35 and
            all(isinstance(a, dict) and a.get('status') == 'DRAFT_HOLD' and
                isinstance(a.get('slug'), str) and a['slug'] for a in articles) and
            len({a['slug'] for a in articles}) == 35 and
            sum(a.get('citation_occurrences', -1) for a in articles) == 2000,
            'ARTICLE_ROSTER_OR_CITATION_DRIFT')
    article_slugs = {a['slug'] for a in articles}
    groups, tasks = scope.get('source_group_dossiers'), queue.get('source_group_tasks')
    require(isinstance(groups, list) and isinstance(tasks, list) and
            len(groups) == len(tasks) == 32, 'GROUP_TASK_CENSUS_DRIFT')
    require({g.get('group_index') for g in groups if isinstance(g, dict)} ==
            set(range(1, 33)) and
            {t.get('crosswalk_group_index') for t in tasks if isinstance(t, dict)} ==
            set(range(1, 33)), 'GROUP_INDICES_INVALID')
    indexed: dict[tuple[str, str, str], int] = {}
    seen_source: dict[int, tuple[set[tuple[str, str, str]], int, set[str]]] = {}
    for d in groups:
        index = d['group_index']
        require(d.get('status') == 'UNREVIEWED_HUMAN_REQUIRED' and
                isinstance(d.get('witness_sha256'), str) and
                len(d['witness_sha256']) == 64 and
                isinstance(d.get('review_alias'), str) and d['review_alias'].startswith('https://'),
                'SOURCE_DOSSIER_APPROVAL_OR_WITNESS_DRIFT')
        variants = d.get('variants')
        require(isinstance(variants, list) and len(variants) >= 2,
                'MISSING_REGISTERED_SOURCE_VARIANTS')
        cited = set()
        cite_count, affected = 0, set()
        for v in variants:
            require(isinstance(v, dict) and all(isinstance(v.get(k), str) and v[k]
                    for k in ('origin', 'id', 'literal_url', 'source_file')),
                    'SOURCE_IDENTITY_INCOMPLETE')
            identity = cited_identity(v)
            require(identity not in indexed, 'SOURCE_VARIANT_IN_MULTIPLE_GROUPS')
            indexed[identity] = index
            references = v.get('article_reading_scopes')
            require(isinstance(references, list) and
                    v.get('uncited_variant_not_an_approval') is (len(references) == 0),
                    'CITED_VARIANT_OR_UNCITED_FLAG_DRIFT')
            if references:
                cited.add(identity)
            seen_article = set()
            for r in references:
                require(isinstance(r, dict) and
                        r.get('article_slug') in article_slugs and
                        r['article_slug'] not in seen_article and
                        r.get('citation_id') == v['id'] and
                        r.get('literal_url') == v['literal_url'] and
                        isinstance(r.get('author_reading_scope'), str) and
                        bool(r['author_reading_scope'].strip()) and
                        type(r.get('citation_occurrences')) is int and
                        r['citation_occurrences'] > 0,
                        'AUTHOR_SCOPED_REFERENCE_INCONSISTENT')
                seen_article.add(r['article_slug'])
                affected.add(r['article_slug'])
                cite_count += r['citation_occurrences']
        require(cited, 'UNREFERENCED_SHARED_GROUP')
        seen_source[index] = (cited, cite_count, affected)
    matched = set()
    mappings = []
    for task in tasks:
        require(task.get('decision') == 'UNREVIEWED_HUMAN_REQUIRED' and
                isinstance(task.get('task_id'), str) and
                task['task_id'].startswith('SOURCE-') and
                len(task['task_id']) == 27, 'SOURCE_TASK_APPROVAL_OR_ID_DRIFT')
        raw = task.get('cited_variant_identities_only')
        require(isinstance(raw, list) and bool(raw), 'MISSING_CITED_TASK_IDENTITIES')
        require(all(isinstance(row, list) and len(row) == 3 and
                    all(isinstance(x, str) and x for x in row) for row in raw),
                'MALFORMED_CITED_TASK_IDENTITY')
        identities = [tuple(row) for row in raw]
        require(len(set(identities)) == len(identities), 'DUPLICATE_CITED_IDENTITY')
        target = {indexed.get(i) for i in identities}
        require(None not in target and len(target) == 1,
                'R135_GROUP_CROSSES_R137_SOURCE_IDENTITIES')
        r137_idx = target.pop()
        require(r137_idx not in matched, 'MULTIPLE_R135_GROUPS_COLLAPSE')
        matched.add(r137_idx)
        cited, count, affected = seen_source[r137_idx]
        require(set(identities) == cited, 'CITED_SOURCE_VARIANT_MISSING_OR_EXTRA')
        require(type(task.get('citation_occurrences')) is int and
                task['citation_occurrences'] == count,
                'GROUP_CITATION_OCCURRENCES_DISAGREE')
        require(isinstance(task.get('affected_articles'), list) and
                set(task['affected_articles']) == affected and
                len(task['affected_articles']) == len(affected),
                'GROUP_AFFECTED_ARTICLES_DISAGREE')
        mappings.append({'r135_crosswalk_index': task['crosswalk_group_index'],
                         'r137_alias_sorted_index': r137_idx,
                         'cited_author_variants': len(cited),
                         'cited_occurrences': count,
                         'affected_article_count': len(affected),
                         'source_task_id': task['task_id']})
    require(matched == set(range(1, 33)), 'UNMATCHED_SHARED_SOURCE_GROUP')
    require(len({t['task_id'] for t in tasks}) == 32, 'DUPLICATE_SOURCE_TASK')
    passages = queue.get('safety_passage_tasks')
    require(isinstance(passages, list) and
            len(passages) == qstats.get('risk_passages_requiring_human_review') and
            len({p.get('task_id') for p in passages if isinstance(p, dict)}) == len(passages) and
            all(isinstance(t, dict) and t.get('decision') == 'UNREVIEWED_HUMAN_REQUIRED'
                for t in passages), 'SAFETY_PASSAGE_WORKLIST_DRIFT')
    return {'status': HOLD, 'may_publish': False, 'qd_pass': False,
            'medical_safety_verified': False, 'merchant_offer_verified': False,
            'crosswalk_complete_structurally': True,
            'human_source_review_complete': False,
            'human_emergency_safety_review_complete': False,
            'source_agreement_inferred': False,
            'candidate_parent': scope['candidate_parent'],
            'input_queue_sha256': fingerprint(queue),
            'input_author_dossiers_sha256': fingerprint(scope),
            'stats': {'articles': 35, 'citation_occurrences': 2000,
                      'shared_groups_joined': len(mappings),
                      'cited_group_occurrences': sum(m['cited_occurrences'] for m in mappings),
                      'safety_passage_tasks_pending': len(passages),
                      'r135_r137_group_indices_differ': sum(m['r135_crosswalk_index'] !=
                                                           m['r137_alias_sorted_index'] for m in mappings)},
            'group_index_crosswalk': sorted(mappings, key=lambda a: a['r135_crosswalk_index']),
            'warning': 'This is a structural reconciliation only. Human source, emergency safety, independent QD and founder approval remain mandatory HOLD.'}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path('.'))
    args = ap.parse_args(argv)
    try:
        root = args.root
        sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -I
        from r133_snapshot_gate import load_json
        from r134_reviewer_packet import packet
        from r135_review_queue import review_queue
        from r137_author_scope_crosswalk import audit
        manifest = load_json((root / 'preparedness/docs/r133/locked_files.json').read_bytes())
        q = review_queue(packet(root, manifest))  # original R133 custody enforced
        d = audit(root)  # second independent original-blob custody check
        print(json.dumps(reconcile(q, d), sort_keys=True, indent=2, ensure_ascii=False))
        return 0
    except (ReconciliationHold, OSError, ValueError, KeyError, TypeError,
            UnicodeError, ImportError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
