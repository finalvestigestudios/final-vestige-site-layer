#!/usr/bin/env python3
"""R234: independent draft-card exposure and outbound-link gate for landing/hubs.

R232 proves bytes match an authenticated builder; it does not independently
prove that auxiliary pages label all 41 unpublished drafts, link to the correct
frozen routes, or avoid unreviewed outbound commerce/collection. This read-only
HOLD gate checks both WordPress and preview drafts. It cannot certify a source,
review a safety claim, or approve a publication or paid offer.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit

HOLD = 'DRAFT_HARD_HOLD'
HIDE = re.compile(r'(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\.0*)?\b)', re.I)
VOID = frozenset({'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'})


class _DraftCards(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.cards = []
        self.card = None
        self.anchor = None
        self.span = None
        self.errors = []
        self.robots_noindex = False

    def handle_startendtag(self, tag, attrs):
        # Ordinary non-void HTML is NOT self-closing in browsers. The already
        # authenticated R230 gate rejects tokenizer-mode ambiguity before us.
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        keys = [k for k, _ in attrs]
        if len(keys) != len(set(keys)):
            self.errors.append('duplicate HTML attribute')
        a = dict(attrs)
        hidden = bool((self.stack and self.stack[-1]['hidden'])
                      or 'hidden' in a or 'inert' in a
                      or a.get('aria-hidden', '').lower() == 'true'
                      or HIDE.search(a.get('style', '') or ''))
        if tag in ('base', 'iframe', 'object', 'embed'):
            self.errors.append('active/foreign auxiliary element: ' + tag)
        if tag == 'script' and a.get('src'):
            self.errors.append('external auxiliary script')
        if tag == 'form' and (a.get('action') or a.get('method', '').lower() == 'post'):
            self.errors.append('submitting auxiliary form')
        if tag == 'meta' and a.get('name', '').lower() == 'robots':
            self.robots_noindex |= 'noindex' in (a.get('content') or '').lower().split(',')
        if tag == 'a':
            href = a.get('href')
            if (type(href) is not str or not href or href.startswith('//')
                    or not (href.startswith('/') or href.startswith('#'))
                    or href.startswith('/\\') or any(k.startswith('on') for k in a)):
                self.errors.append('unreviewed outbound/active auxiliary anchor')
            if self.card is not None:
                if hidden or self.anchor is not None or not self.stack or self.stack[-1]['tag'] != 'h3':
                    self.errors.append('card anchor outside unique h3')
                self.anchor = {'href': href, 'text': ''}
        if tag == 'li' and 'pa-card' in (a.get('class') or '').split():
            if self.card is not None:
                self.errors.append('nested auxiliary card')
            self.card = {'attributes': a, 'hidden': hidden, 'links': [], 'badges': [],
                         'depth': len(self.stack)}
        if tag == 'span' and self.card is not None:
            if hidden:
                self.errors.append('concealed draft badge')
            self.span = ''
        self.stack.append({'tag': tag, 'hidden': hidden})
        if tag in VOID:
            self.stack.pop()

    def handle_data(self, data):
        if self.anchor is not None:
            self.anchor['text'] += data
        if self.span is not None:
            self.span += data

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == 'a' and self.anchor is not None:
            if self.card is not None:
                self.card['links'].append(self.anchor)
            self.anchor = None
        if tag == 'span' and self.span is not None:
            if self.card is not None:
                self.card['badges'].append(self.span.strip())
            self.span = None
        if tag == 'li' and self.card is not None and len(self.stack) == self.card['depth'] + 1:
            self.cards.append(self.card)
            self.card = None
        # Parser recovery is not publication evidence; R230 checks unsupported
        # tokenizer states, while exact R232 replay pins entire HTML bytes.
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                del self.stack[index:]
                break


def verify_page(page: str, expected: dict[str, dict], *, preview: bool) -> dict:
    """Compare all cards to source-controlled routes, titles and draft labels."""
    if type(page) is not str or type(expected) is not dict or not expected:
        raise ValueError('R234 invalid page or frozen card expectation')
    parser = _DraftCards()
    parser.feed(page)
    parser.close()
    if parser.card is not None or parser.anchor is not None or parser.span is not None:
        raise ValueError('R234 incomplete auxiliary card markup')
    if preview and not parser.robots_noindex:
        raise ValueError('R234 preview missing robots noindex')
    if parser.errors:
        raise ValueError('R234 unsafe auxiliary DOM: ' + '; '.join(parser.errors[:3]))
    if len(parser.cards) != len(expected):
        raise ValueError('R234 missing/duplicate auxiliary draft cards')
    observed = set()
    for card in parser.cards:
        a = card['attributes']
        if card['hidden']:
            raise ValueError('R234 concealed auxiliary draft card')
        if a.get('data-verify') != 'pending':
            raise ValueError('R234 false independent verification badge')
        if len(card['links']) != 1:
            raise ValueError('R234 card title link count not exactly one')
        link = card['links'][0]
        route = link['href']
        if route not in expected or route in observed:
            raise ValueError('R234 duplicate/foreign draft route')
        observed.add(route)
        meta = expected[route]
        if (a.get('data-section') != meta['section']
                or a.get('data-track') != meta['track']
                or link['text'].strip() != meta['title']):
            raise ValueError('R234 card source/title/track drift')
        if card['badges'].count('Draft') != 1:
            raise ValueError('R234 draft badge missing or ambiguous')
    if observed != set(expected):
        raise ValueError('R234 missing frozen auxiliary routes')
    return {'state': HOLD, 'draft_cards': len(observed), 'release_authorized': False,
            'commercial_approval': False, 'independent_qd_pass': False,
            'source_or_medical_safety_approved': False}


def verify_auxiliary_drafts(root: Path, library, tokenizer_guard, safe_read) -> dict:
    """Inspect all authentic auxiliary pages in two modes, without writes."""
    if type(getattr(library, 'articles', None)) is not dict or len(library.articles) != 41:
        raise ValueError('R234 expected 35 articles and six frozen tools')
    if any(m.get('status', {}).get('publish') != 'draft' for m in library.articles.values()):
        raise ValueError('R234 unapproved publication status')
    expected = {}
    by_section = {}
    for slug, meta in library.articles.items():
        route = library.url_path(slug)
        if (type(route) is not str or not route.startswith('/preparedness/')
                or urlsplit(route).query or urlsplit(route).fragment or route in expected):
            raise ValueError('R234 invalid or duplicate frozen route')
        expected[route] = {'title': meta['title'], 'section': meta['section'],
                           'track': meta['track']}
        by_section.setdefault(meta['section'], {})[route] = expected[route]
    sections = library.taxonomy.get('sections')
    if type(sections) is not list or not sections:
        raise ValueError('R234 missing section roster')
    names = {'landing': expected}
    for sec in sections:
        sid = sec.get('slug')
        if sid in by_section:
            name = 'hub-' + sid
            if name in names:
                raise ValueError('R234 duplicate auxiliary page name')
            names[name] = by_section[sid]
    if set(by_section) != {sec.get('slug') for sec in sections if sec.get('slug') in by_section}:
        raise ValueError('R234 article refers to unknown section')
    cards = 0
    for mode in ('wp', 'preview'):
        for name, indexed in names.items():
            page = safe_read(root, f'build/{mode}/{name}.html').decode('utf-8', 'strict')
            token_state = tokenizer_guard.verify_tokenizer_states(page)
            if token_state.get('state') != HOLD or token_state.get('release_authorized') is not False:
                raise ValueError('R234 unsupported tokenizer safety state')
            receipt = verify_page(page, indexed, preview=(mode == 'preview'))
            if receipt['state'] != HOLD or receipt['release_authorized'] is not False:
                raise ValueError('R234 unexpected draft custody state')
            cards += receipt['draft_cards']
    return {'state': HOLD, 'release_authorized': False, 'independent_qd_pass': False,
            'source_or_medical_safety_approved': False, 'commercial_approval': False,
            'auxiliary_files_verified': 2 * len(names), 'card_instances_verified': cards,
            'distinct_frozen_routes': len(expected)}
