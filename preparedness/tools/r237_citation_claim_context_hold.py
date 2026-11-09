#!/usr/bin/env python3
"""Read-only per-occurrence citation claim-context docket; never a source/safety approval.

The receipt shows *where* a contributor placed each source and the claim text
nearby, not whether the reference supports it. No article or source is changed.
"""
from collections import Counter
import hashlib
import html
import json
import re

HOLD = 'DRAFT_HARD_HOLD'
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
TOKEN = re.compile(r'\{\{cite:[\s\S]*?\}\}|\{\{cite:[^\n]*')
NON_READER = re.compile(r'<!--.*?-->|<(script|style|template|noscript|textarea)\b[^>]*>.*?</\1\s*>', re.I | re.S)
TAG = re.compile(r'<[^>]*>', re.S)
ANY_TOKEN = re.compile(r'\{\{(?:cite|link):.*?\}\}', re.S)
SPACES = re.compile(r'\s+')
RISK_TERMS = ('medication', 'medical', 'oxygen', 'insulin', 'water', 'filter',
              'generator', 'carbon monoxide', 'refrigerat', 'temperature',
              'infant', 'disinfect', 'boil', 'canning', 'evacuat', 'smoke')
ORIGINAL_HOLDS = {(7, 'cdc-find-clean-water'): 2, (20, 'start-ready-plan'): 1}


def strict_object(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError('duplicate JSON key: ' + k)
        result[k] = v
    return result


def readable(text):
    text = ANY_TOKEN.sub(' ', text)
    text = TAG.sub(' ', text)
    return SPACES.sub(' ', html.unescape(text)).strip()


def source_context(body, start, end):
    # Bounded text excerpt for REVIEW, not an assertion about semantic support.
    # Do not allow the following claim to be mistaken for the cited claim.
    left = body[max(0, start - 300):start]
    right = body[end:min(len(body), end + 70)]
    pre = readable(left)[-195:]
    post = readable(right)[:48]
    return (pre + ' ' + post).strip()


def cited_in_markup(body, start, end):
    # Detect tokens in tag attributes (not reader-visible text). This is a
    # conservative fail-closed source-input gate; HTML output has other gates.
    before = body.rfind('>', 0, start)
    inside = body.rfind('<', 0, start) > before
    return inside or any(m.start() <= start < m.end()
                         for m in NON_READER.finditer(body))


def audit_claim_contexts(root, roster, safe_read):
    if type(roster) is not list or len(roster) != 35:
        raise ValueError('R237 exact 35-article source roster required')
    articles, combined, holds, seen = [], hashlib.sha256(), Counter(), set()
    for n, entry in enumerate(roster, 1):
        if type(entry) is not dict or type(entry.get('n')) is not int or entry['n'] != n:
            raise ValueError('R237 article identity/order mismatch')
        slug = entry.get('slug')
        if type(slug) is not str or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in seen:
            raise ValueError('R237 invalid or duplicate article route')
        seen.add(slug)
        body_raw = safe_read(root, 'content/articles/' + slug + '.body.html')
        metadata_raw = safe_read(root, 'content/articles/' + slug + '.meta.json')
        body = body_raw.decode('utf-8', 'strict')
        meta = json.loads(metadata_raw.decode('utf-8', 'strict'), object_pairs_hook=strict_object,
                          parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite metadata')))
        if (type(meta) is not dict or type(meta.get('n')) is not int or meta['n'] != n
                or meta.get('slug') != slug or type(meta.get('status')) is not dict
                or meta['status'].get('publish') != 'draft'):
            raise ValueError('R237 article metadata/status mismatch: ' + slug)
        notes = meta.get('source_use')
        if type(notes) is not dict:
            raise ValueError('R237 source-use notes unavailable: ' + slug)
        occurrences = list(CITE.finditer(body))
        if len(occurrences) != len(list(TOKEN.finditer(body))) or body.count('{{cite:') != len(occurrences):
            raise ValueError('R237 malformed citation token: ' + slug)
        rows = []
        for ordinal, match in enumerate(occurrences, 1):
            source_id = match.group(1)
            if cited_in_markup(body, match.start(), match.end()):
                raise ValueError('R237 citation concealed in markup: ' + slug + ':' + source_id)
            note = notes.get(source_id)
            if type(note) is not str or not note.strip():
                raise ValueError('R237 citation lacks an author reading note: ' + slug + ':' + source_id)
            excerpt = source_context(body, match.start(), match.end())
            # Empty surrounding text is evidence of a floating source marker.
            if len(excerpt) < 6:
                raise ValueError('R237 citation lacks legible adjacent claim: ' + slug + ':' + source_id)
            risks = sorted({term for term in RISK_TERMS if term in excerpt.lower()})
            receipt = {'ordinal': ordinal, 'source_id': source_id,
                       'offset': match.start(), 'context_excerpt': excerpt,
                       'context_sha256': hashlib.sha256(excerpt.encode('utf-8')).hexdigest(),
                       'author_note_sha256': hashlib.sha256(note.encode('utf-8')).hexdigest(),
                       'human_risk_review_terms': risks,
                       'independent_claim_source_verified': False}
            rows.append(receipt)
            holds[(n, source_id)] += 1
        # Evidence is canonical JSON; avoid a locale-dependent serialized receipt.
        packed = json.dumps(rows, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        row_digest = hashlib.sha256(packed).hexdigest()
        combined.update(str(n).encode('ascii') + b'\0' + row_digest.encode('ascii') + b'\n')
        articles.append({'n': n, 'slug': slug, 'citation_count': len(rows),
                         'claim_context_receipt_sha256': row_digest,
                         'body_sha256': hashlib.sha256(body_raw).hexdigest(),
                         'metadata_sha256': hashlib.sha256(metadata_raw).hexdigest(),
                         'source_use_without_citations': sorted(set(notes) - {m.group(1) for m in occurrences}),
                         'occurrences': rows})
    for key, count in ORIGINAL_HOLDS.items():
        if holds[key] != count:
            raise ValueError('R237 original source-review occurrence HOLD drift: ' + str(key))
    return {'state': HOLD, 'release_authorized': False, 'independent_qd_pass': False,
            'source_review_approved': False, 'medical_safety_verified': False,
            'claim_evidence_adjudicated': False, 'original_hold_occurrences': 3,
            'article_count': len(articles), 'citation_count': sum(a['citation_count'] for a in articles),
            'human_review_required': True, 'receipt_sha256': combined.hexdigest(),
            'articles': articles}
