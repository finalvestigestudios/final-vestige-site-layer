#!/usr/bin/env python3
"""Read-only, author-scoped Preparedness citation/review packet. NEVER a safety or QD PASS.

Run from repository root only after immutable R133 custody audit. Output is a local
review artifact, not publication data. Exact passage/source scope is for HUMANS.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

from r133_snapshot_gate import audit as custody_audit, load_json, IntegrityHold, CITE

BLOCK = frozenset({'p', 'li', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'dt', 'dd', 'figcaption'})
VOID = frozenset({'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'})
HIDE = frozenset({'script', 'style', 'template', 'noscript'})
RISK = {
    'water-treatment': re.compile(r'\b(?:boil(?:ing)?|bleach|chlorin\w*|disinfect\w*|filter\w*|potable|purif\w*|contaminat\w*)\b', re.I),
    'food-preservation': re.compile(r'\b(?:jerky|dehydrat\w*|pressure.cann\w*|botulis\w*|freez\w*|refrigerat\w*|meat.cur\w*|temperatur\w*)\b', re.I),
    'power-fire-carbon-monoxide': re.compile(r'\b(?:generator\w*|carbon.monoxide|breaker\w*|electrical|gas.heater\w*|open.flame\w*|fire.escape|extension.cord\w*)\b', re.I),
    'medicine-medical-dependency': re.compile(r'\b(?:medicat\w*|insulin|oxygen|dialysis|dose\w*|medical.device\w*|pharmacist\w*)\b', re.I),
    'evacuation-shelter': re.compile(r'\b(?:evacuat\w*|shelter.in.place|wildfire\w*|smoke.inhalation|floodwater\w*)\b', re.I),
}


def citation_ids(text: str) -> list[str]:
    return CITE.findall(text)


def plain(text: str) -> str:
    return re.sub(r'\s+', ' ', CITE.sub('', re.sub(r'\{\{link:[^}]*\}\}', '', text))).strip()


class ReaderBlocks(HTMLParser):
    """Build ordered visible-text blocks without duplicating nested elements."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.buffer: list[str] = []
        self.blocks: list[str] = []

    def flush(self):
        text = re.sub(r'\s+', ' ', ' '.join(self.buffer)).strip()
        if text:
            self.blocks.append(text)
        self.buffer.clear()

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK:
            self.flush()
        if tag in VOID:
            return
        d = dict(attrs)
        style = re.sub(r'\s+', '', d.get('style') or '').lower()
        hidden = (tag in HIDE or 'hidden' in d or 'inert' in d or
                  (d.get('aria-hidden') or '').lower() == 'true' or
                  'display:none' in style or 'visibility:hidden' in style or
                  any(v for _, v in self.stack))
        self.stack.append((tag, hidden))

    def handle_startendtag(self, tag, attrs):
        if tag in BLOCK:
            self.flush()

    def handle_endtag(self, tag):
        if tag in BLOCK:
            self.flush()
        for idx in range(len(self.stack) - 1, -1, -1):
            if self.stack[idx][0] == tag:
                del self.stack[idx:]
                break

    def handle_data(self, data):
        if not any(hidden for _, hidden in self.stack):
            self.buffer.append(data)

    def finish(self):
        self.flush()
        return self.blocks


def segments(html: str) -> list[str]:
    p = ReaderBlocks()
    p.feed(html)
    p.close()
    return p.finish()


def resolve_author_source(origin: str, sid: str, sources: dict):
    author = sources.get(origin, {})
    base = sources.get('base', {})
    if sid in author:
        src = author[sid]
        selected_origin = origin
    elif sid in base:
        src = base[sid]
        selected_origin = 'base'
    else:
        raise IntegrityHold(f'UNRESOLVED_AUTHOR_CITATION:{origin}:{sid}')
    shadowed = (selected_origin != 'base' and sid in base and
                (src.get('url'), src.get('supports')) !=
                (base[sid].get('url'), base[sid].get('supports')))
    return selected_origin, src, shadowed


def review_article(slug: str, body: str, meta: dict, origin: str, sources: dict, membership: dict):
    blocks = segments(body)
    citations = citation_ids(body)
    visible = [sid for b in blocks for sid in citation_ids(b)]
    if visible != citations:
        raise IntegrityHold('VISIBLE_CITATION_ORDER_DRIFT:' + slug)
    if set(citations) != set(meta.get('source_use', {})):
        raise IntegrityHold('AUTHOR_SCOPE_CITATION_DRIFT:' + slug)
    records = []
    classifications = Counter()
    cited = 0
    for index, block in enumerate(blocks, start=1):
        prose = plain(block)
        family = sorted(k for k, pattern in RISK.items() if pattern.search(prose))
        ids = citation_ids(block)
        if not ids and not family:
            continue
        classifications.update(family)
        bindings = []
        for sid in ids:
            chosen, src, shadowed = resolve_author_source(origin, sid, sources)
            key = (chosen, sid, src['url'])
            membership_info = membership.get(key)
            bindings.append({
                'citation_id': sid, 'source_origin': chosen, 'publisher': src.get('publisher'),
                'source_url': src['url'], 'source_verified_on': src.get('verified_on'),
                'human_link_check': src.get('human_link_check'),
                'author_reading_scope': meta['source_use'][sid],
                'source_supports': src.get('supports'),
                'shared_source_group': membership_info,
                'author_shadows_different_base_source': shadowed,
            })
            cited += 1
        records.append({
            'block_index': index, 'excerpt': prose[:220],
            'review_keyword_families': family,
            'citation_occurrences': len(bindings),
            'attention_no_inline_citation': bool(family and not bindings),
            'bindings': bindings,
        })
    return {
        'slug': slug, 'origin': origin,
        'visible_words_approx': sum(len(re.findall(r'\b[\w\u2019-]+\b', plain(b))) for b in blocks),
        'citation_occurrences': cited,
        'author_source_ids': len(meta['source_use']),
        'keyword_flagged_blocks': sum(bool(rec['review_keyword_families']) for rec in records),
        'keyword_flagged_without_inline_citation': sum(rec['attention_no_inline_citation'] for rec in records),
        'keyword_family_counts': dict(sorted(classifications.items())),
        'safety_review_state_historical_only': meta['safety_review']['state'],
        'publication_state': meta['status']['publish'],
        'blocks_for_human_review': records,
    }


def packet(root: Path, manifest: dict):
    root = Path(root)
    custody = custody_audit(root, manifest)  # fail closed first; never reinterprets historical approval
    def read(rel):
        return load_json((root / rel).read_bytes())
    cross = read('preparedness/sources/crosswalk.json')
    taxonomy = read('preparedness/taxonomy.json')
    sources = {}
    for origin in ('base','start','shelter','food','health','hist-food','hist-home','hist-field'):
        path = 'preparedness/sources/' + ('register.json' if origin == 'base' else f'fragments/{origin}.json')
        sources[origin] = {s['id']: s for s in read(path)['sources']}
    membership = {}
    for idx, group in enumerate(cross['groups'], start=1):
        if group.get('review_status') != 'pending-human-source-and-reading-scope-review':
            raise IntegrityHold('SHARED_SOURCE_REVIEW_NOT_HOLD')
        for v in group['variants']:
            key = (v['origin'], v['source']['id'], v['source']['url'])
            if key in membership:
                raise IntegrityHold('DUPLICATE_SHARED_SOURCE_MEMBERSHIP')
            membership[key] = idx
    articles = []
    for a in taxonomy['slate']:
        slug = a['slug']
        meta = read(f'preparedness/content/articles/{slug}.meta.json')
        body = (root / f'preparedness/content/articles/{slug}.body.html').read_text(encoding='utf-8')
        articles.append(review_article(slug, body, meta, cross['article_origins'].get(slug, 'base'), sources, membership))
    total = sum(a['citation_occurrences'] for a in articles)
    if total != manifest['expected_citation_occurrences']:
        raise IntegrityHold('REVIEW_PACKET_CITATION_TOTAL_DRIFT')
    return {
        'purpose': 'HUMAN_REVIEW_PACKET_NOT_SAFETY_APPROVAL',
        'status': 'HOLD', 'may_publish': False, 'qd_pass': False,
        'merchant_offer_verified': False,
        'candidate_parent': manifest['candidate_parent'],
        'immutable_custody': custody,
        'article_count': len(articles),
        'citation_occurrences': total,
        'keyword_flagged_without_inline_citation': sum(a['keyword_flagged_without_inline_citation'] for a in articles),
        'warning': 'Keyword flags are triage prompts, NOT judgments of harm, falsity, or clinical safety. Human source-scope, technical and qualified emergency/medical review remains required.',
        'articles': articles,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    try:
        manifest = load_json((args.root / 'preparedness/docs/r133/locked_files.json').read_bytes())
        print(json.dumps(packet(args.root, manifest), sort_keys=True, ensure_ascii=False, indent=2))
        return 0
    except (IntegrityHold, OSError, ValueError, TypeError, KeyError, UnicodeError) as e:
        print('HOLD: ' + str(e), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
