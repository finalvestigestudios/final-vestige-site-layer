#!/usr/bin/env python3
"""R455: read-only authored-to-WordPress/preview citation and reading-scope custody.

Build-facing integrity gate, NOT source truth or safety approval. This adapter checks
actual build.py citation and bibliography HTML. It never publishes, writes a
report, modifies the source register or chooses competing contributor variants.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
from html import unescape
import json
from pathlib import Path
import re

TOKEN = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
TOKEN_LIKE = re.compile(r'\{\{\s*cite\s*:', re.I)
DISALLOWED_ATTR = {'hidden', 'inert'}
MAX_BYTES = 5_000_000
HOLD = 'DRAFT_HARD_HOLD'


class CitationParityError(ValueError):
    pass


def norm(text: str) -> str:
    return ' '.join(unescape(text).split())


def attributes(raw: list[tuple[str, str | None]]) -> dict[str, str | None]:
    attrs = {}
    for name, value in raw:
        if name in attrs:
            raise CitationParityError('duplicate HTML attribute: ' + name)
        attrs[name] = value
    return attrs


def visible(attrs: dict, role: str) -> None:
    if DISALLOWED_ATTR & attrs.keys():
        raise CitationParityError(role + ': hidden or inert citation')
    if attrs.get('aria-hidden', '').lower() == 'true':
        raise CitationParityError(role + ': aria-hidden citation')
    style = re.sub(r'\s+', '', attrs.get('style') or '').lower()
    if any(term in style for term in ('display:none', 'visibility:hidden', 'opacity:0', 'font-size:0', 'font-size:0px')):
        raise CitationParityError(role + ': concealed citation')


class RenderedProof(HTMLParser):
    """Extract numbered anchors, exact bibliography URLs and reader-visible scope."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict]] = []
        self.refs: list[dict] = []
        self.entries: list[dict] = []
        self.active_ref: dict | None = None
        self.active_entry: dict | None = None
        self._anchor_text: list[str] | None = None
        self._active_anchor = None
        self._citation_sups = 0
        self._source_section = 0
        self._seen_source_section = False

    def handle_starttag(self, tag: str, raw: list[tuple[str, str | None]]):
        attrs = attributes(raw)
        inherited = any('hidden' in f[1] or 'inert' in f[1] or
                        f[1].get('aria-hidden') == 'true' or
                        re.search(r'display\s*:\s*none|visibility\s*:\s*hidden', f[1].get('style') or '', re.I)
                        for f in self.stack)
        if tag == 'section' and 'pa-sources' in (attrs.get('class') or '').split():
            if self._seen_source_section:
                raise CitationParityError('duplicate sources section')
            self._source_section += 1
            self._seen_source_section = True
        if tag == 'sup' and 'pa-cite' in (attrs.get('class') or '').split():
            if inherited:
                raise CitationParityError('citation in hidden ancestor')
            visible(attrs, 'inline citation')
            if self.active_ref is not None:
                raise CitationParityError('nested citation superscript')
            self.active_ref = {'href': None, 'label': None, 'aria': None}
            self._citation_sups += 1
        if self._source_section and tag == 'li' and re.fullmatch(r'src-[0-9]+', attrs.get('id') or ''):
            if inherited:
                raise CitationParityError('source entry in hidden ancestor')
            visible(attrs, 'source entry')
            if self.active_entry is not None:
                raise CitationParityError('nested bibliography entry')
            self.active_entry = {'id': attrs['id'], 'url': None, 'title': None, 'text': []}
        if tag == 'a' and (self.active_ref is not None or self.active_entry is not None):
            visible(attrs, 'source/citation link')
            if inherited:
                raise CitationParityError('link in hidden ancestor')
            if self._active_anchor is not None:
                raise CitationParityError('nested citation link')
            if self.active_ref is not None:
                if self.active_ref['href'] is not None:
                    raise CitationParityError('multiple links in citation')
                self.active_ref['href'] = attrs.get('href')
                self.active_ref['aria'] = attrs.get('aria-label')
                self._active_anchor = 'ref'
            else:
                if self.active_entry['url'] is not None:
                    raise CitationParityError('multiple source links')
                self.active_entry['url'] = attrs.get('href')
                if 'noopener' not in (attrs.get('rel') or '').split():
                    raise CitationParityError('external source link missing noopener')
                self._active_anchor = 'entry'
            self._anchor_text = []
        self.stack.append((tag, attrs))

    def handle_startendtag(self, tag, raw):
        self.handle_starttag(tag, raw)
        self.handle_endtag(tag)

    def handle_data(self, data: str):
        if self._anchor_text is not None:
            self._anchor_text.append(data)
        if self.active_entry is not None:
            self.active_entry['text'].append(data)

    def handle_endtag(self, tag: str):
        if tag == 'a' and self._active_anchor is not None:
            value = norm(''.join(self._anchor_text or []))
            if self._active_anchor == 'ref':
                self.active_ref['label'] = value
            else:
                self.active_entry['title'] = value
            self._active_anchor = None
            self._anchor_text = None
        if tag == 'sup' and self.active_ref is not None:
            if self.active_ref['href'] is None or self.active_ref['label'] is None:
                raise CitationParityError('citation has no link')
            self.refs.append(self.active_ref)
            self.active_ref = None
        if tag == 'li' and self.active_entry is not None:
            if self.active_entry['url'] is None or not self.active_entry['title']:
                raise CitationParityError('source entry has no outbound link')
            self.active_entry['text'] = norm(''.join(self.active_entry['text']))
            self.entries.append(self.active_entry)
            self.active_entry = None
        if tag == 'section' and self._source_section:
            self._source_section -= 1
        # HTML blocks can contain void elements, so do not require complete stack
        # balance; remove matching opening tag and nested descendants conservatively.
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def proof(self, raw: str) -> dict:
        try:
            self.feed(raw)
            self.close()
        except (UnicodeError, TypeError) as exc:
            raise CitationParityError(str(exc)) from exc
        if self.active_ref or self.active_entry or self._active_anchor:
            raise CitationParityError('unclosed citation or source entry')
        if len(self.refs) != self._citation_sups:
            raise CitationParityError('lost a superscript in rendered HTML')
        if not self._seen_source_section:
            raise CitationParityError('missing sources section')
        return {'refs': self.refs, 'entries': self.entries}


def authored_order(body: str) -> list[str]:
    refs = TOKEN.findall(body)
    if not refs or len(refs) != len(TOKEN_LIKE.findall(body)):
        raise CitationParityError('missing citations or malformed citation placeholder')
    return list(dict.fromkeys(refs))


def one_surface(surface: str, ordered: list[str], body: str,
                sources: dict[str, dict], overrides: dict[str, str]) -> dict:
    document = RenderedProof().proof(surface)
    if len(document['entries']) != len(ordered):
        raise CitationParityError('missing, extra or merged source bibliography entries')
    expected_index = {sid: str(n) for n, sid in enumerate(ordered, 1)}
    source_refs = TOKEN.findall(body)
    if len(document['refs']) != len(source_refs):
        raise CitationParityError('inline citation count changed')
    for actual, sid in zip(document['refs'], source_refs):
        n = expected_index[sid]
        if actual['href'] != '#src-' + n or actual['label'] != '[' + n + ']':
            raise CitationParityError('source citation retargeted or mislabeled: ' + sid)
        if actual['aria'] != 'Source ' + n + ': ' + sources[sid]['title']:
            raise CitationParityError('citation accessible label changed: ' + sid)
    for position, (sid, item) in enumerate(zip(ordered, document['entries']), 1):
        source = sources[sid]
        if item['id'] != 'src-' + str(position):
            raise CitationParityError('bibliography reordered or duplicate numbering')
        if item['url'] != source['url']:
            raise CitationParityError('literal source URL reassigned or normalized: ' + sid)
        if item['title'] != norm(source['title']):
            raise CitationParityError('source title differs from registered identity: ' + sid)
        if source['publisher'] not in item['text']:
            raise CitationParityError('source publisher attribution missing: ' + sid)
        scope = norm(overrides.get(sid) or source.get('supports') or '')
        if not scope or 'Used for: ' + scope not in item['text']:
            raise CitationParityError('article-specific source reading scope shortened or missing: ' + sid)
        if 'Human source-link check pending' not in item['text'] and 'Human source-link check complete' not in item['text']:
            raise CitationParityError('human source-link status concealed: ' + sid)
    return {'source_id_order': ordered, 'citation_occurrences': len(source_refs),
            'bibliography_entries': len(ordered), 'all_id_url_scope_links_preserved': True}


def verify_pair(body: str, sources: dict[str, dict], wordpress: str, preview: str,
                overrides: dict[str, str] | None = None) -> dict:
    """Fail closed: exact authored IDs, raw URLs and reading scopes on BOTH outputs."""
    if any(not isinstance(x, str) or len(x.encode('utf-8')) > MAX_BYTES for x in (body, wordpress, preview)):
        raise CitationParityError('missing/oversized input')
    if not isinstance(sources, dict) or not isinstance(overrides or {}, dict):
        raise CitationParityError('invalid evidence map')
    order = authored_order(body)
    for sid in order:
        source = sources.get(sid)
        if not isinstance(source, dict) or not all(isinstance(source.get(key), str) and source[key]
                for key in ('url', 'title', 'publisher', 'supports')):
            raise CitationParityError('missing original source record/scope: ' + sid)
        if not source['url'].startswith('https://'):
            raise CitationParityError('source URL must use HTTPS: ' + sid)
    for sid in (overrides or {}):
        if sid not in order:
            raise CitationParityError('unused source_use override: ' + sid)
    wp = one_surface(wordpress, order, body, sources, overrides or {})
    pr = one_surface(preview, order, body, sources, overrides or {})
    if wp != pr:
        raise CitationParityError('WordPress and preview evidence mismatch')
    return {'release_state': HOLD, 'qd_pass': False,
            'source_claim_support_verified': False, 'qualified_safety_review': 'NOT_APPROVED',
            'wordpress_published': False, 'native_35_article_run': 'NOT_EXECUTED',
            'parity': wp, 'surfaces_checked': ('wordpress-draft', 'private-preview')}


def main(argv=None) -> int:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--manifest', required=True, type=Path,
                     help='Read-only local JSON with body, sources, wordpress, preview and optional source_use')
    args = cli.parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        data = verify_pair(manifest['body'], manifest['sources'], manifest['wordpress'],
                           manifest['preview'], manifest.get('source_use'))
        print(json.dumps(data, sort_keys=True))
        return 0
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(json.dumps({'release_state': HOLD, 'qd_pass': False, 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
