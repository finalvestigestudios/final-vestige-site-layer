#!/usr/bin/env python3
"""R236 read-only source-use parity, preserving three UNREVIEWED citation occurrences.

A source-use explanation is author metadata, NOT verified citation evidence.
Nothing here grants QD, safety, medical, source or publication approval.
"""
from collections import Counter
import hashlib
import json
import re

HOLD = 'DRAFT_HARD_HOLD'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
# Original occurrence-level editorial holds persist even after source-use notes exist.
UNREVIEWED = {(7, 'cdc-find-clean-water'): 2, (20, 'start-ready-plan'): 1}


def _no_duplicates(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate source-use JSON key: ' + key)
        value[key] = item
    return value


def audit_parity(root, roster, safe_read):
    """Audit all exactly 35 frozen article manuscripts, never their public status."""
    if type(roster) is not list or len(roster) != 35:
        raise ValueError('R236 requires all 35 original articles')
    seen, articles, found_holds = set(), [], {}
    for index, entry in enumerate(roster, 1):
        if type(entry) is not dict or type(entry.get('n')) is not int or entry['n'] != index:
            raise ValueError('R236 article order/id mismatch')
        slug = entry.get('slug')
        if type(slug) is not str or re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) is None or slug in seen:
            raise ValueError('R236 duplicate/unsafe article slug')
        seen.add(slug)
        body = safe_read(root, 'content/articles/' + slug + '.body.html').decode('utf-8', 'strict')
        meta_raw = safe_read(root, 'content/articles/' + slug + '.meta.json')
        meta = json.loads(meta_raw.decode('utf-8', 'strict'), object_pairs_hook=_no_duplicates,
                          parse_constant=lambda v: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
        if type(meta) is not dict or meta.get('n') != index or meta.get('slug') != slug:
            raise ValueError('R236 metadata/roster mismatch: ' + slug)
        if type(meta.get('status')) is not dict or meta['status'].get('publish') != 'draft':
            raise ValueError('R236 public article status forbidden: ' + slug)
        notes = meta.get('source_use')
        if type(notes) is not dict:
            raise ValueError('R236 missing source-use notes: ' + slug)
        citation_counts = Counter(CITE.findall(body))
        absent = sorted(set(citation_counts) - set(notes))
        if absent:
            raise ValueError('R236 source-use note omitted: ' + slug + ':' + ','.join(absent))
        # Do not silently count malformed or empty author notes as reconciled.
        for sid in citation_counts:
            if type(notes[sid]) is not str or not notes[sid].strip():
                raise ValueError('R236 blank source-use note: ' + slug + ':' + sid)
        article_holds = []
        for (n, sid), expected in UNREVIEWED.items():
            if n == index:
                if citation_counts.get(sid) != expected:
                    raise ValueError('R236 original citation hold changed: ' + slug + ':' + sid)
                found_holds[(n, sid)] = expected
                article_holds.append({'source_id': sid, 'occurrences': expected,
                                      'status': 'UNREVIEWED_CLAIM_SOURCE'})
        articles.append({'n': index, 'slug': slug, 'citations': sum(citation_counts.values()),
                         'distinct_cited_ids': len(citation_counts),
                         'unused_source_use_notes': sorted(set(notes) - set(citation_counts)),
                         'citation_metadata_present': True,
                         'source_claims_verified': False,
                         'unreviewed_original_citations': article_holds,
                         'evidence_sha256': hashlib.sha256(body.encode('utf-8') + b'\0' + meta_raw).hexdigest()})
    if found_holds != UNREVIEWED:
        raise ValueError('R236 original citation review docket incomplete')
    return {'state': HOLD, 'article_count': 35,
            'citation_occurrences': sum(a['citations'] for a in articles),
            'unreviewed_original_occurrences': sum(UNREVIEWED.values()),
            'unreviewed_original_groups': len(UNREVIEWED),
            'source_use_missing_occurrences': 0,
            'source_use_parity_only_not_source_approval': True,
            'independent_qd_pass': False, 'medical_safety_verified': False,
            'source_review_approved': False, 'release_authorized': False,
            'articles': articles}
