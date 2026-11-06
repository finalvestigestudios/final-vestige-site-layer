#!/usr/bin/env python3
"""R174: independently check draft HTML citation export provenance; NEVER a release PASS.

This is a deterministic read-only post-render gate, not a source-content or safety
endorsement. It compares numbered citations and their rendered references against
the original article-specific source interpretation rather than global source ID.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r174-rendered-citation-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
PINS = {
    'preparedness/docs/r151/contributor-three-way.json': '9cf386519eda970209ff6be4ff0243661cd9d996',
    'preparedness/docs/r161/body_custody.json': 'fede4222c796d92798eff7cf0dcb225c291f7d61',
    'preparedness/review/r173/claim-scope-human-docket.json': '48e1050e815f55c5f2564dc030b8ba2aa24df548',
}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SUP = re.compile(r'<sup class="pa-cite"><a href="#src-(\d+)" aria-label="Source (\d+): ([^"]+)">\[(\d+)\]</a></sup>')
ITEM = re.compile(r'<li id="src-(\d+)"><a href="([^"]+)" rel="noopener">([^<]+)</a>\.', re.S)
SOURCE_LI = re.compile(r'<li id="src-(\d+)">(.*?)</li>', re.S)
SHA = re.compile(r'[0-9a-f]{40}\Z')


def require(value: object, message: str) -> None:
    if not value:
        raise ValueError(message)


def blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def load_pinned(root: Path, name: str, expected: str) -> dict:
    file = root / name
    require(file.is_file() and not file.is_symlink(), 'missing or symlink: ' + name)
    raw = file.read_bytes()
    require(blob(raw) == expected, 'pinned evidence drift: ' + name)
    return json.loads(raw)


def audit_one(meta: dict, original: str, inner: str, order: list[str], sources: dict,
              *, strict: bool = True) -> dict:
    """Pure output audit. Synthetic tests can exercise this without release authority."""
    slug = meta.get('slug')
    require(type(slug) is str and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug), 'invalid slug')
    require(meta.get('status', {}).get('publish') == 'draft', slug + ': published metadata forbidden')
    uses = meta.get('source_use')
    require(type(uses) is dict and uses and type(original) is str and type(inner) is str,
            slug + ': missing content or interpretation')
    marks = CITE.findall(original)
    require(bool(marks) and set(marks) == set(uses), slug + ': source-use/citation mapping drift')
    expected_order = list(dict.fromkeys(marks))
    require(type(order) is list and order == expected_order and set(sources) == set(order),
            slug + ': article-specific source order drift')
    require(inner.count('<sup class="pa-cite">') == len(marks), slug + ': cite render lost/added')
    matches = SUP.findall(inner)
    require(len(matches) == len(marks), slug + ': malformed numbered citation')
    seq = {sid: n for n, sid in enumerate(order, 1)}
    for index, (ref, aria_no, label, display_no) in enumerate(matches):
        sid = marks[index]
        n = seq[sid]
        src = sources[sid]
        require((ref, aria_no, display_no) == (str(n), str(n), str(n)),
                slug + ': wrong in-text numbering/target')
        require(label == html.escape(src['title'], quote=True), slug + ': citation title/aria drift')
    items = ITEM.findall(inner)
    require(len(items) == len(order) == inner.count('<li id="src-'),
            slug + ': missing/duplicate source-list entry')
    detail = SOURCE_LI.findall(inner)
    require(len(detail) == len(order), slug + ': malformed source-list detail')
    for index, (n, href, title) in enumerate(items):
        sid = order[index]
        source = sources[sid]
        require(n == str(index + 1) and detail[index][0] == n,
                slug + ': source number out of sequence')
        require(href == html.escape(source['url'], quote=True) and
                title == html.escape(source['title'], quote=True),
                slug + ': wrong article-scope source URL/title')
        text = detail[index][1]
        require('Used for: ' + html.escape(uses[sid], quote=True) in text,
                slug + ': source-use explanation lost')
        require('Human source-link check pending' in text and
                'Human source-link check complete' not in text,
                slug + ': false human-checked claim')
        require(source.get('human_link_check') is False,
                slug + ': unreviewed source marked human-checked')
        if source.get('_shared_pending'):
            require('Shared-source reading scope: independent review pending' in text,
                    slug + ': shared URL scope disclaimer dropped')
    require('Draft: not public' in inner, slug + ': draft status disclosure lost')
    require('<section class="pa-sources"' in inner and
            '<div class="pa-body" id="pa-main">' in inner,
            slug + ': body/source sections missing')
    require('{{cite:' not in inner and '{{link:' not in inner,
            slug + ': unresolved template token')
    if strict:
        require(len(marks) >= 20, slug + ': original citation depth below baseline')
    return {'slug': slug, 'citations': len(marks), 'source_uses': len(order),
            'source_reference_sha256': hashlib.sha256(json.dumps(
                [(sid, sources[sid]['url'], uses[sid]) for sid in order],
                ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()}


def verify(root: Path, *, require_export: bool = False) -> dict:
    from importlib import util
    original = {p: load_pinned(root, p, s) for p, s in PINS.items()}
    legacy = original['preparedness/docs/r151/contributor-three-way.json']
    custody = original['preparedness/docs/r161/body_custody.json']
    docket = original['preparedness/review/r173/claim-scope-human-docket.json']
    require(legacy.get('decision') == HOLD and legacy.get('qd_pass') is False and
            legacy.get('qualified_safety_review') is False and
            docket.get('state') == HOLD and docket.get('qualified_food_safety_review') is False and
            docket.get('independent_qd_pass') is False and docket.get('published') is False and
            docket.get('source_alias_equivalence_approved') is False,
            'original independent review remains unresolved')
    require(custody.get('status') == HOLD and custody.get('article_count') == 35 and
            custody.get('total_citations') == 2000 and
            custody.get('article_source_relationships') == 385,
            '35-article immutable baseline drift')
    tools = root / 'preparedness/tools'
    def import_local(name: str):
        path = tools / (name + '.py')
        require(path.is_file() and not path.is_symlink(), name + ' missing')
        spec = util.spec_from_file_location('r174_' + name, path)
        require(spec is not None and spec.loader is not None, name + ' import failure')
        module = util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    r161 = import_local('r161_body_custody_gate')
    cust = r161.verify(root)
    require(cust.get('articles') == 35 and cust.get('citations') == 2000 and
            cust.get('source_uses') == 385 and cust.get('independent_qd_pass') is False,
            'underlying body/source custody failed')
    build = import_local('build')
    lib = build.Library(root / 'preparedness')
    require(set(lib.articles) >= set(custody['articles']) and
            len(custody['articles']) == 35, 'article census missing')
    receipts, routes, total_cites, total_uses = [], set(), 0, 0
    for slug in sorted(custody['articles']):
        meta = lib.articles[slug]
        require(meta['slug'] == slug, 'meta slug drift')
        route = lib.url_path(slug)
        require(route not in routes, 'duplicate route: ' + route)
        routes.add(route)
        built = build.build_article(lib, slug)
        require(built['canonical'] == build.SITE + route and
                built['words'] >= 1500 and len(built['inner']) > 0,
                'canonical/reading-depth drift: ' + slug)
        order = built['sources']
        variants = {}
        for sid in order:
            s = dict(lib.source_for(meta, sid))
            crosswalk = lib.crosswalk_member_groups.get((s.get('_origin'), sid, s['url']))
            s['_shared_pending'] = bool(crosswalk and crosswalk.get('review_status') != 'resolved')
            variants[sid] = s
        receipt = audit_one(meta, meta['_body'], built['inner'], order, variants)
        total_cites += receipt['citations']
        total_uses += receipt['source_uses']
        wp = build.wp_wrap(lib, built['inner'])
        preview = build.preview_wrap(lib, built['inner'], meta['h1'] + ' | The Preparedness Archive', meta['description'])
        require(wp.count('<!-- wp:html -->') == 1 and
                wp.count('<!-- /wp:html -->') == 1 and
                built['inner'] in wp and built['inner'] in preview and
                'noindex,nofollow' in preview,
                slug + ': draft WordPress/preview wrapper integrity failed')
        if require_export:
            for sub, expected in [('wp', wp), ('preview', preview)]:
                path = root / 'preparedness/build' / sub / (slug + '.html')
                require(path.is_file() and not path.is_symlink() and
                        path.read_bytes() == expected.encode('utf-8'),
                        slug + ': stale or modified generated ' + sub + ' export')
        receipts.append({**receipt, 'route': route, 'words': built['words']})
    require(total_cites == 2000 and total_uses == 385 and len(routes) == 35,
            'complete 35-article rendered citation baseline lost')
    return {'schema': SCHEMA, 'state': HOLD, 'article_count': len(receipts),
            'rendered_citations': total_cites, 'rendered_source_uses': total_uses,
            'distinct_article_routes': len(routes),
            'draft_export_bytes_checked': require_export,
            'receipt_sha256': hashlib.sha256(json.dumps(receipts, sort_keys=True,
                separators=(',', ':')).encode()).hexdigest(),
            'qualified_source_review': False, 'food_safety_approved': False,
            'independent_qd_pass': False, 'commercial_offer_verified': False,
            'publication_authorized': False}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, default=Path('.'))
    ap.add_argument('--check-export', action='store_true', help='require byte-for-byte existing draft outputs')
    args = ap.parse_args(argv)
    try:
        out = verify(args.repo.resolve(strict=True), require_export=args.check_export)
    except (OSError, ValueError, KeyError, TypeError, ImportError, UnicodeError,
            AttributeError, json.JSONDecodeError) as exc:
        out = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
               'error': str(exc), 'publication_authorized': False}
    print(json.dumps(out, sort_keys=True))
    return 2  # even valid structural evidence never authorizes publication

if __name__ == '__main__':
    raise SystemExit(main())
