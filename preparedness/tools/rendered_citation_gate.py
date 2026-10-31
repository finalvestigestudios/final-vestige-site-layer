#!/usr/bin/env python3
"""R12: independent source-to-rendered-citation parity gate for DRAFT exports.

R11 checks that exports match the renderer, but cannot establish that the
renderer faithfully mapped each contributor-owned source to the rendered
footnote. This read-only gate checks the mapping itself. It neither verifies
external claims nor authorizes release, safety, or a CMS change.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
SRC_ID = re.compile(r'src-([1-9][0-9]*)\Z')


class RenderCitationFailure(ValueError):
    """Rendered citations are not proven equal to the frozen draft sources."""


class CitationHTML(HTMLParser):
    """Collect only actual citation links in the main body and source footnotes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.body = 0
        self.sources = 0
        self.body_count = 0
        self.sources_count = 0
        self.refs = []
        self.footnotes = []
        self.source_ids = Counter()
        self.current_ref = None
        self.current_foot = None
        self.ref_anchor = 0
        self.foot_anchor = 0

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID:
            self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in VOID:
            return
        d = dict(attrs)
        classes = set((d.get('class') or '').split())
        self.stack.append(tag)
        depth = len(self.stack)
        if tag == 'div' and d.get('id') == 'pa-main':
            if self.body or self.body_count:
                raise RenderCitationFailure('duplicate or nested article body')
            self.body = depth
            self.body_count += 1
        if tag == 'section' and 'pa-sources' in classes:
            if self.sources or self.sources_count:
                raise RenderCitationFailure('duplicate source section')
            self.sources = depth
            self.sources_count += 1
        if tag == 'sup' and 'pa-cite' in classes:
            if not self.body or self.current_ref is not None:
                raise RenderCitationFailure('citation outside body or nested')
            self.current_ref = {'depth': depth, 'links': []}
        if tag == 'li' and isinstance(d.get('id'), str) and d['id'].startswith('src-'):
            if not self.sources or self.current_foot is not None:
                raise RenderCitationFailure('source anchor outside bibliography or nested')
            self.source_ids[d['id']] += 1
            self.current_foot = {'depth': depth, 'id': d['id'], 'links': [], 'text': ''}
        if tag == 'a' and self.current_ref is not None and self.body:
            self.current_ref['links'].append({'href': d.get('href'), 'aria': d.get('aria-label'), 'text': ''})
            self.ref_anchor = depth
        if tag == 'a' and self.current_foot is not None and self.sources:
            self.current_foot['links'].append({'href': d.get('href'), 'rel': d.get('rel', ''), 'text': ''})
            self.foot_anchor = depth

    def handle_data(self, data):
        if self.current_ref is not None and self.ref_anchor and self.current_ref['links']:
            self.current_ref['links'][-1]['text'] += data
        if self.current_foot is not None:
            self.current_foot['text'] += data
            if self.foot_anchor and self.current_foot['links']:
                self.current_foot['links'][-1]['text'] += data

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            raise RenderCitationFailure('malformed nested rendered HTML')
        depth = len(self.stack)
        if tag == 'a' and self.ref_anchor == depth:
            self.ref_anchor = 0
        if tag == 'a' and self.foot_anchor == depth:
            self.foot_anchor = 0
        if self.current_ref is not None and self.current_ref['depth'] == depth:
            if tag != 'sup':
                raise RenderCitationFailure('citation wrapper malformed')
            self.refs.append(self.current_ref['links'])
            self.current_ref = None
        if self.current_foot is not None and self.current_foot['depth'] == depth:
            if tag != 'li':
                raise RenderCitationFailure('source list item malformed')
            self.footnotes.append(self.current_foot)
            self.current_foot = None
        if self.body == depth:
            self.body = 0
        if self.sources == depth:
            self.sources = 0
        self.stack.pop()

    def finish(self):
        if self.stack or self.current_ref or self.current_foot or self.body or self.sources:
            raise RenderCitationFailure('truncated or malformed rendered HTML')
        if self.body_count != 1 or self.sources_count != 1:
            raise RenderCitationFailure('article body or bibliography missing')
        if any(count != 1 for count in self.source_ids.values()):
            raise RenderCitationFailure('duplicate source anchor')
        return self


def audit_article(lib, renderer, slug, *, claim_parser):
    """Check independent input citation ordinals against actual rendered links."""
    meta = lib.articles[slug]
    if meta.get('slug') != slug or meta.get('status', {}).get('publish') != 'draft':
        raise RenderCitationFailure(f'{slug}: non-draft or mismatched article')
    claimed = claim_parser(meta.get('_body'))
    if not claimed:
        raise RenderCitationFailure(f'{slug}: no visible source citations')
    if any(not isinstance(c, dict) or c.get('source_id') is None for c in claimed):
        raise RenderCitationFailure(f'{slug}: malformed original citation occurrence')
    expected_sources = list(dict.fromkeys(c['source_id'] for c in claimed))
    if set(expected_sources) != set(meta.get('source_use', {})):
        raise RenderCitationFailure(f'{slug}: article source-use inventory differs from citations')
    if any(not isinstance(note, str) or not note.strip() for note in meta['source_use'].values()):
        raise RenderCitationFailure(f'{slug}: empty or invalid article-specific source explanation')
    built = renderer.build_article(lib, slug)
    if built.get('slug') != slug or built.get('meta') is not meta or built.get('sources') != expected_sources:
        raise RenderCitationFailure(f'{slug}: renderer returned a wrong article/source ordering')
    inner = built.get('inner')
    if not isinstance(inner, str) or '{{cite:' in inner:
        raise RenderCitationFailure(f'{slug}: missing or unresolved rendered article')
    parser = CitationHTML()
    try:
        parser.feed(inner)
        parser.close()
        parser.finish()
    except (TypeError, ValueError) as exc:
        raise RenderCitationFailure(f'{slug}: invalid rendered source markup: {exc}') from exc
    if len(parser.refs) != len(claimed) or len(parser.footnotes) != len(expected_sources):
        raise RenderCitationFailure(f'{slug}: citation or bibliography reference lost/duplicated')
    if set(parser.source_ids) != {f'src-{n}' for n in range(1, len(expected_sources) + 1)}:
        raise RenderCitationFailure(f'{slug}: bibliography ordinals or IDs changed')
    for ordinal, (original, links) in enumerate(zip(claimed, parser.refs), 1):
        sid = original['source_id']
        n = expected_sources.index(sid) + 1
        source = lib.source_for(meta, sid)
        expected = {'href': f'#src-{n}', 'aria': f'Source {n}: {source["title"]}', 'text': f'[{n}]'}
        if len(links) != 1 or links[0] != expected:
            raise RenderCitationFailure(f'{slug}: rendered citation {ordinal} is mismapped or inaccessible')
    for n, (sid, note) in enumerate(((s, meta['source_use'][s]) for s in expected_sources), 1):
        source = lib.source_for(meta, sid)
        foot = parser.footnotes[n - 1]
        if foot['id'] != f'src-{n}' or len(foot['links']) != 1:
            raise RenderCitationFailure(f'{slug}: source {n} has a malformed footnote')
        link = foot['links'][0]
        if (link['href'] != source['url'] or link['text'] != source['title']
                or 'noopener' not in link['rel'].split()):
            raise RenderCitationFailure(f'{slug}: source {n} URL/title/rel differs from contributor record')
        if not isinstance(note, str) or not note.strip() or f'Used for: {note}' not in foot['text']:
            raise RenderCitationFailure(f'{slug}: source {n} lost its article-specific evidence-use explanation')
        if source.get('human_link_check') is True or 'Human source-link check pending' not in foot['text'] or 'Human source-link check complete' in foot['text']:
            raise RenderCitationFailure(f'{slug}: source {n} falsely implies human verification')
        if source.get('notes') and f'Reading scope / limitations: {source["notes"]}' not in foot['text']:
            raise RenderCitationFailure(f'{slug}: source {n} lost its contributor reading limits')
        group = lib.crosswalk_groups.get(source['url'])
        if group and group.get('review_status') != 'resolved' and 'Shared-source reading scope: independent review pending' not in foot['text']:
            raise RenderCitationFailure(f'{slug}: unresolved shared source hidden')
    return {'slug': slug, 'citations': len(claimed), 'source_pairs': len(expected_sources)}


def audit_corpus(lib, renderer, *, claim_parser, expected_items=36, expected_occurrences=1959, expected_pairs=367):
    if len(lib.articles) != expected_items:
        raise RenderCitationFailure('35+1 unpublished item baseline changed')
    entries = [audit_article(lib, renderer, slug, claim_parser=claim_parser) for slug in sorted(lib.articles)]
    if sum(x['citations'] for x in entries) != expected_occurrences or sum(x['source_pairs'] for x in entries) != expected_pairs:
        raise RenderCitationFailure('original/rendered occurrence or pair census drift')
    return {'schema_version': 1, 'authority': 'MACHINE_RENDERED_CITATION_CUSTODY_ONLY',
            'release_state': 'HOLD', 'may_publish': False, 'human_source_claim_verification': False,
            'medical_food_water_fire_safety_verified': False, 'draft_items': len(entries),
            'rendered_citation_occurrences': sum(x['citations'] for x in entries),
            'article_source_pairs': sum(x['source_pairs'] for x in entries), 'articles': entries}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--receipt', type=Path, help='HOLD-only local receipt inside preparedness/build')
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tools'))
    import build, evidence_freeze, validate, claim_occurrence_audit as r8
    import claim_corpus_release_gate as r10, draft_export_custody as r11, source_review_queue
    lib = build.Library(root)
    errors = evidence_freeze.verify(lib)
    if errors:
        raise RenderCitationFailure('source freeze failures: ' + '; '.join(errors[:5]))
    errors, _warnings = validate.validate(lib)
    if errors:
        raise RenderCitationFailure('native validator failures: ' + '; '.join(errors[:5]))
    canonical = r10.audit_corpus(lib, source_review_queue.source_rows(root), evidence_freeze.fingerprint)
    r11.audit_export(lib, root / 'build', build, canonical_receipt=canonical)
    result = audit_corpus(lib, build, claim_parser=r8.parse_visible_claims)
    if args.receipt:
        r8.safe_export(args.receipt, json.dumps(result, sort_keys=True, indent=2) + '\n', root / 'build')
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
