#!/usr/bin/env python3
"""Fail-closed, read-only human source/safety review queue from the R134 custody packet.

This is a triage *worklist*, never independent fact-checking, medical approval,
source equivalence, publishing approval, or a revenue measurement.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sys

TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))  # Python -I does not put script directory on sys.path

PRIORITY = (
    'medicine-medical-dependency', 'power-fire-carbon-monoxide',
    'water-treatment', 'food-preservation', 'evacuation-shelter',
)
HOLD = 'HOLD_HUMAN_SOURCE_AND_SAFETY_ADJUDICATION'


class ReviewHold(ValueError):
    pass


def require(ok: bool, code: str) -> None:
    if not ok:
        raise ReviewHold(code)


def fingerprint(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False,
                     separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def review_queue(packet: dict, *, expected_articles: int = 35,
                 expected_citations: int = 2000, expected_groups: int = 32) -> dict:
    """Generate stable, traceable tasks without ever accepting a human approval claim."""
    require(isinstance(packet, dict) and
            packet.get('purpose') == 'HUMAN_REVIEW_PACKET_NOT_SAFETY_APPROVAL' and
            packet.get('status') == 'HOLD' and packet.get('may_publish') is False and
            packet.get('qd_pass') is False and
            packet.get('merchant_offer_verified') is False, 'UPSTREAM_CUSTODY_HOLD_REQUIRED')
    articles = packet.get('articles')
    require(isinstance(articles, list) and len(articles) == expected_articles and
            packet.get('article_count') == expected_articles, 'ARTICLE_ROSTER_DRIFT')
    require(packet.get('citation_occurrences') == expected_citations,
            'UPSTREAM_CITATION_TOTAL_DRIFT')
    seen_slugs: set[str] = set()
    group_exposure: dict[int, list[dict]] = defaultdict(list)
    passage_tasks: list[dict] = []
    missing_human_link_checks = 0
    total = 0
    for article in articles:
        slug, origin = article.get('slug'), article.get('origin')
        require(isinstance(slug, str) and slug and slug not in seen_slugs and
                isinstance(origin, str) and origin, 'DUPLICATE_OR_INVALID_SLUG')
        seen_slugs.add(slug)
        require(article.get('publication_state') == 'draft', 'ARTICLE_NOT_DRAFT:' + slug)
        require(article.get('safety_review_state_historical_only') in
                ('pending', 'approved', 'not-required'), 'INVALID_HISTORICAL_STATE:' + slug)
        blocks = article.get('blocks_for_human_review')
        require(isinstance(blocks, list), 'MISSING_BLOCKS:' + slug)
        block_seen: set[int] = set()
        local_count = 0
        for block in blocks:
            index, bindings = block.get('block_index'), block.get('bindings')
            require(type(index) is int and index > 0 and index not in block_seen and
                    isinstance(bindings, list), 'DUPLICATE_OR_INVALID_BLOCK:' + slug)
            block_seen.add(index)
            require(block.get('citation_occurrences') == len(bindings),
                    'BLOCK_BINDING_COUNT_DRIFT:' + slug)
            local_count += len(bindings)
            family = block.get('review_keyword_families')
            require(isinstance(family, list) and len(set(family)) == len(family) and
                    all(x in PRIORITY for x in family), 'INVALID_RISK_FAMILY:' + slug)
            require(block.get('attention_no_inline_citation') is bool(family and not bindings),
                    'CITATION_ATTENTION_DRIFT:' + slug)
            excerpt = block.get('excerpt')
            require(isinstance(excerpt, str) and len(excerpt) <= 220,
                    'INVALID_EXCERPT:' + slug)
            normalized = []
            for b in bindings:
                sid, sorigin, url = b.get('citation_id'), b.get('source_origin'), b.get('source_url')
                require(all(isinstance(v, str) and v for v in (sid, sorigin, url)) and
                        url.startswith(('https://', 'http://')), 'UNRESOLVED_SOURCE:' + slug)
                scope = b.get('author_reading_scope')
                require(isinstance(scope, str) and scope.strip(), 'MISSING_AUTHOR_SCOPE:' + slug)
                group = b.get('shared_source_group')
                require(group is None or (type(group) is int and 1 <= group <= expected_groups),
                        'INVALID_SHARED_GROUP:' + slug)
                if b.get('human_link_check') is not True:
                    missing_human_link_checks += 1
                identity = {'origin': sorigin, 'citation_id': sid, 'literal_url': url,
                            'author_reading_scope': scope,
                            'source_supports': b.get('source_supports'),
                            'source_verified_on': b.get('source_verified_on'),
                            'human_link_check': b.get('human_link_check'),
                            'shadows_base': b.get('author_shadows_different_base_source') is True}
                normalized.append(identity)
                if group is not None:
                    group_exposure[group].append({'slug': slug, 'block_index': index,
                                                  'source': identity})
            if family:
                priority = min(PRIORITY.index(x) for x in family)
                witness = {'slug': slug, 'origin': origin, 'block_index': index,
                           'excerpt': excerpt, 'families': sorted(family), 'sources': normalized}
                passage_tasks.append({
                    'task_id': 'PASSAGE-' + fingerprint(witness)[:20],
                    'priority': priority + 1, 'slug': slug, 'origin': origin,
                    'block_index': index, 'excerpt': excerpt,
                    'risk_families_for_triage_only': sorted(family),
                    'no_citation_in_this_block': not bool(bindings),
                    'source_variants_exact': normalized,
                    'witness_sha256': fingerprint(witness),
                    'decision': 'UNREVIEWED_HUMAN_REQUIRED',
                    'required_reviewer_action': 'Check each concrete claim against source passage and applicable current guidance; document limits and corrections separately.'
                })
        require(local_count == article.get('citation_occurrences'),
                'ARTICLE_CITATION_COUNT_DRIFT:' + slug)
        total += local_count
    require(total == expected_citations, 'FULL_CITATION_CENSUS_DRIFT')
    require(set(group_exposure) == set(range(1, expected_groups + 1)),
            'SHARED_GROUP_EXPOSURE_INCOMPLETE')
    source_tasks = []
    for group in range(1, expected_groups + 1):
        exposure = group_exposure[group]
        variants = sorted({(e['source']['origin'], e['source']['citation_id'],
                            e['source']['literal_url']) for e in exposure})
        # An article may not cite every variant; the canonical crosswalk (R132)
        # remains authoritative. Do not infer author equivalence from this set.
        witness = {'group': group, 'cited_variants': variants, 'exposure': exposure}
        source_tasks.append({'task_id': 'SOURCE-' + fingerprint(witness)[:20],
                             'crosswalk_group_index': group,
                             'cited_variant_identities_only': [list(v) for v in variants],
                             'citation_occurrences': len(exposure),
                             'affected_articles': sorted({e['slug'] for e in exposure}),
                             'decision': 'UNREVIEWED_HUMAN_REQUIRED',
                             'required_reviewer_action': 'Open original R132 crosswalk; adjudicate every registered variant and author reading scope, including variants not cited in this packet. Never auto-merge source IDs.'})
    passage_tasks.sort(key=lambda d: (d['priority'], d['slug'], d['block_index']))
    require(len({t['task_id'] for t in passage_tasks}) == len(passage_tasks),
            'PASSAGE_WITNESS_ID_COLLISION')
    return {'status': HOLD, 'may_publish': False, 'qd_pass': False,
            'medical_safety_verified': False, 'merchant_offer_verified': False,
            'provenance': {'candidate_parent': packet.get('candidate_parent'),
                           'article_count': expected_articles,
                           'citation_occurrences': total},
            'summary': {'crosswalk_groups_requiring_human_review': expected_groups,
                        'risk_passages_requiring_human_review': len(passage_tasks),
                        'risk_passages_without_inline_citations': sum(t['no_citation_in_this_block'] for t in passage_tasks),
                        'citation_bindings_without_true_human_link_check': missing_human_link_checks},
            'source_group_tasks': source_tasks, 'safety_passage_tasks': passage_tasks,
            'warning': 'Worklist only; source presence does not verify a claim, historical approved/not-required metadata is not new approval. No public use, medical safety attestation, revenue claim or QD PASS.'}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path('.'))
    args = ap.parse_args(argv)
    try:
        from r133_snapshot_gate import load_json, IntegrityHold
        from r134_reviewer_packet import packet as trusted_packet
        root = args.root
        manifest = load_json((root / 'preparedness/docs/r133/locked_files.json').read_bytes())
        result = review_queue(trusted_packet(root, manifest))  # authentic R133 custody ALWAYS first
        print(json.dumps(result, sort_keys=True, ensure_ascii=False, indent=2))
        return 0
    except (ReviewHold, OSError, ValueError, TypeError, KeyError, UnicodeError, ImportError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
