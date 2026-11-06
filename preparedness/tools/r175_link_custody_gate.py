#!/usr/bin/env python3
"""R175: read-only draft crosslink/anchor provenance; permanently DRAFT/HARD HOLD.

R174 verifies citation-to-source custody. This independent boundary checks that
article-to-article routes, inline editorial links, related links and in-page
references survive rendering without inserted/rewritten commercial destinations.
No structural success grants safety, source approval or production publishing.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r175-link-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
LINK = re.compile(r'\{\{link:([a-z0-9]+(?:-[a-z0-9]+)*)\|([^{}]+)\}\}')
CITE = re.compile(r'\{\{cite:[a-z0-9-]+\}\}')
INLINE = re.compile(r'\{\{inline-js:[a-z_]+\.js\}\}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location('r175_' + name, path)
    require(path.is_file() and not path.is_symlink() and spec and spec.loader,
            'missing or symlinked module: ' + name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LinkReader(HTMLParser):
    """Read only anchors in article body or related aside, plus all fragment IDs."""
    VOID = frozenset(('area','base','br','col','embed','hr','img','input','link',
                      'meta','param','source','track','wbr'))

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.mode = None
        self.div_level = 0
        self.aside_level = 0
        self.citation_level = 0
        self.ids: list[str] = []
        self.body: list[tuple[str, str]] = []
        self.related: list[tuple[str, str]] = []
        self.fragments: list[str] = []
        self._link = None
        self._buffer: list[str] = []
        self.unclosed = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        cls = set((attrs.get('class') or '').split())
        if self.mode is None and tag == 'div' and 'pa-body' in cls and attrs.get('id') == 'pa-main':
            self.mode = 'body'; self.div_level = 1
        elif self.mode == 'body' and tag == 'div':
            self.div_level += 1
        elif self.mode is None and tag == 'aside' and 'pa-related' in cls:
            self.mode = 'related'; self.aside_level = 1
        elif self.mode == 'related' and tag == 'aside':
            self.aside_level += 1
        if self.mode == 'body' and tag == 'sup' and 'pa-cite' in cls:
            self.citation_level += 1
        if tag == 'a':
            require(self._link is None, 'nested or malformed anchor')
            if self.mode in ('body','related') and not self.citation_level:
                require('href' in attrs and isinstance(attrs['href'], str), 'missing anchor href')
                self._link = (self.mode, attrs['href'])
                self._buffer = []
        if tag == 'a' and isinstance(attrs.get('href'), str) and attrs['href'].startswith('#'):
            self.fragments.append(attrs['href'][1:])

    def handle_data(self, data):
        if self._link:
            self._buffer.append(data)

    def handle_endtag(self, tag):
        if tag == 'a' and self._link:
            mode, href = self._link
            (self.body if mode == 'body' else self.related).append((href, ''.join(self._buffer)))
            self._link = None
            self._buffer = []
        if self.mode == 'body' and tag == 'sup' and self.citation_level:
            self.citation_level -= 1
        if self.mode == 'body' and tag == 'div':
            self.div_level -= 1
            if self.div_level == 0:
                self.mode = None
        elif self.mode == 'related' and tag == 'aside':
            self.aside_level -= 1
            if self.aside_level == 0:
                self.mode = None

    def finish(self):
        self.close()
        require(self._link is None and self.div_level == 0 and
                self.aside_level == 0 and self.citation_level == 0,
                'unclosed link or article scope')
        return self


def expected_links(original: str, routes: dict[str, str]) -> tuple[list[tuple[str,str]], list[str]]:
    """Independent prediction from *original* link tokens and literal body HTML."""
    targets = []
    def replace(match):
        slug, label = match.groups()
        require(slug in routes, 'unknown/unbuilt editorial link target: ' + slug)
        require(bool(label.strip()) and '<' not in label and '>' not in label,
                'invalid editorial link label')
        targets.append(slug)
        return '<a href="' + routes[slug] + '">' + label + '</a>'
    body = INLINE.sub('', CITE.sub('', LINK.sub(replace, original)))
    require('{{link:' not in body and '{{cite:' not in body and '{{inline-js:' not in body,
            'unresolved editorial token')
    reader = LinkReader()
    reader.feed('<div class="pa-body" id="pa-main">' + body + '</div>')
    return reader.finish().body, targets


def audit_one(meta: dict, original: str, rendered: str, routes: dict[str,str],
              related_meta: dict[str,dict], *, require_citations: bool = True) -> dict:
    slug = meta.get('slug')
    require(type(slug) is str and SLUG.fullmatch(slug) and slug in routes,
            'missing original article slug/route')
    require(meta.get('status', {}).get('publish') == 'draft', slug + ': not a draft')
    require(isinstance(original, str) and isinstance(rendered, str) and original and rendered,
            slug + ': missing original or rendered content')
    require(len(routes) == len(set(routes.values())) and all(
        isinstance(path,str) and path.startswith('/preparedness/') and path.endswith('/') and
        '//' not in path and '?' not in path and '#' not in path and
        urlsplit(path).scheme == '' and urlsplit(path).netloc == ''
        for path in routes.values()), slug + ': duplicate/malformed archive route')
    if require_citations:
        require(len(CITE.findall(original)) >= 20, slug + ': citation depth dropped')
    expected, targets = expected_links(original, routes)
    reader = LinkReader();reader.feed(rendered);reader.finish()
    require('pa-main' in reader.ids, slug + ': rendered body missing')
    require(reader.body == expected, slug + ': body href, link count/order or label drift')
    require(len(reader.ids) == len(set(reader.ids)), slug + ': duplicate HTML id')
    require(all(frag and frag in reader.ids for frag in reader.fragments),
            slug + ': dangling in-page citation/TOC/skip target')
    related = meta.get('related', [])
    require(isinstance(related, list) and len(related) == len(set(related)),
            slug + ': duplicate/invalid related targets')
    require(all(type(x) is str and x in routes and x in related_meta for x in related),
            slug + ': unknown related draft target')
    actual_related = [(routes[x], related_meta[x]['title']) for x in related]
    require(reader.related == actual_related, slug + ': related link route or title drift')
    for url, _ in reader.body + reader.related:
        require(not url.startswith('//') and not url.lower().startswith(('javascript:','data:')),
                slug + ': unsafe or protocol-relative body link')
    return {'slug': slug, 'route': routes[slug], 'token_links': len(targets),
            'literal_body_links': len(expected) - len(targets),
            'related_links': len(related), 'in_page_refs': len(reader.fragments),
            'edges': targets + related}


def verify(root: Path, *, require_export: bool = False) -> dict:
    tools = root / 'preparedness' / 'tools'
    prev = _load(tools / 'r174_rendered_citation_gate.py', 'r174')
    proof = prev.verify(root, require_export=require_export)
    require(proof['state'] == HOLD and proof['article_count'] == 35 and
            proof['rendered_citations'] == 2000 and
            proof['rendered_source_uses'] == 385 and
            proof['publication_authorized'] is False,
            'R174 source/citation evidence not admitted')
    build = _load(tools / 'build.py', 'build')
    library = build.Library(root / 'preparedness')
    custody = prev.load_pinned(root, 'preparedness/docs/r161/body_custody.json',
                               prev.PINS['preparedness/docs/r161/body_custody.json'])
    slugs = sorted(custody['articles'])
    require(len(slugs) == 35 and set(slugs).issubset(library.articles), 'original census drift')
    # The 35 immutable articles may link to an authored draft tool (e.g. a
    # family card). Preserve those draft destinations without promoting them to
    # the 35-article corpus or implying they are publicly reachable.
    routes = {slug: library.url_path(slug) for slug in library.articles}
    related_meta = library.articles
    require(len(set(routes.values())) == len(routes), 'duplicate article/tool route')
    receipts = []
    for slug in slugs:
        meta = library.articles[slug]
        built = build.build_article(library, slug)
        require(built['canonical'] == build.SITE + routes[slug],
                slug + ': canonical drift')
        receipts.append(audit_one(meta,meta['_body'],built['inner'],routes,related_meta))
    payload = json.dumps(receipts, sort_keys=True, separators=(',', ':')).encode()
    return {'schema': SCHEMA, 'state': HOLD, 'articles': 35,
            'canonical_routes': len(routes), 'token_links': sum(x['token_links'] for x in receipts),
            'related_links': sum(x['related_links'] for x in receipts),
            'literal_body_links': sum(x['literal_body_links'] for x in receipts),
            'in_page_references': sum(x['in_page_refs'] for x in receipts),
            'link_graph_sha256': hashlib.sha256(payload).hexdigest(),
            'export_compared': require_export, 'independent_source_review': False,
            'medical_food_safety_approved': False, 'independent_qd_pass': False,
            'commercial_offer_verified': False, 'publication_authorized': False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--check-export', action='store_true')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(verify(args.repo.resolve(strict=True), require_export=args.check_export),
                         sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, ImportError, UnicodeError,
            AttributeError, json.JSONDecodeError) as exc:
        print(json.dumps({'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                          'reason': str(exc), 'publication_authorized': False}, sort_keys=True))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
