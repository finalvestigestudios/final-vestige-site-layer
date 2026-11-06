#!/usr/bin/env python3
"""R173: source-adjacent, claim-specific jerky review gate. Never an approval.

Complements, does not replace, original R161/R172 full-body/source custody.
Works read-only on authentic 35-article checkout; isolated fixtures for tests.
"""
from __future__ import annotations
import argparse
import hashlib
from html import unescape
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r173-jerky-claim-scope-v1'
HOLD = 'DRAFT_HARD_HOLD'
BODY_SHAS = {
    'safe-jerky-dehydration': '6fa55c397b161437e016d5d4a6c27da7ce3fa6bd',
    'pemmican-and-dried-meats': '0b3319cc85ea2bc6d069b46d13a40e12ddbd5bc5',
    'pioneer-travel-rations': '058c90b763d8cd6dec0731a7b0a9cee4dd5a57c7',
}
META_SHAS = {
    'safe-jerky-dehydration': '50b365e8109c14bdb9ce1a9365db88215a678ec5',
    'pemmican-and-dried-meats': '03d3824e07fe51931671d0ddc7aa8c85eda58435',
    'pioneer-travel-rations': '7191acba55d63dc405ad9c2003d66193276da89f',
}
DOCKET_SHA = '45963b30ce48a069539c66ace9f1a2d2f5cf1dfd'
# Each anchor denotes a proposed editorial claim, not a validated safety action.
# The IDs must occur in the very same structural content block as its claim.
CLAIMS = (
    ('safe-jerky-dehydration', 'usda-before', 'current recommendation is to heat meat',
     ('food-fsis-jerky-qa', 'nchfp-jerky')),
    ('safe-jerky-dehydration', 'published-method-conflict', 'FSIS says to heat',
     ('food-fsis-jerky', 'nchfp-jerky')),
    ('safe-jerky-dehydration', 'nchfp-after-method', 'After drying, if the strips were not heated in the marinade',
     ('nchfp-jerky', 'food-ksu-jerky')),
    ('safe-jerky-dehydration', 'wild-game-parasite', 'NCHFP says to treat the meat for the parasite',
     ('nchfp-jerky',)),
    ('safe-jerky-dehydration', 'room-storage-nchfp', 'at room temperature for two weeks',
     ('nchfp-jerky',)),
    ('pemmican-and-dried-meats', 'not-a-recipe', 'This is a history, not a recipe', ()),
    ('pemmican-and-dried-meats', 'fsis-heat-guidance', 'current recommendation for making jerky safely',
     ('hist-food-fsis-jerky',)),
    ('pemmican-and-dried-meats', 'nchfp-scope-and-storage', 'The National Center for Home Food Preservation gives',
     ('hist-food-nchfp-jerky', 'hist-food-fsis-jerky')),
    ('pioneer-travel-rations', 'historical-modern-comparison', 'current recommendation for home jerky',
     ('hist-food-fsis-jerky', 'hist-food-marcy-prairie-traveler-text')),
    ('pioneer-travel-rations', 'agencies-disagree', 'two federal and extension sources we read disagree',
     ('hist-food-nchfp-jerky', 'hist-food-fsis-jerky')),
)
CITATION = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')


def require(ok: object, error: str) -> None:
    if not ok:
        raise ValueError(error)


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


class BlockReader(HTMLParser):
    """Retain each complete p/li/td/th block with its own citations only."""
    TAGS = {'p', 'li', 'td', 'th'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        if tag in self.TAGS:
            self.stack.append([tag, []])

    def handle_data(self, data):
        for _, chunks in self.stack:
            chunks.append(data)

    def handle_endtag(self, tag):
        if tag in self.TAGS:
            require(self.stack and self.stack[-1][0] == tag,
                    'malformed content block nesting')
            _, parts = self.stack.pop()
            self.blocks.append(' '.join(''.join(parts).split()))

    def close(self):
        super().close()
        require(not self.stack, 'unterminated content block')


def evaluate(bodies: dict, metas: dict, *, strict: bool = True) -> dict:
    """Pure claim-locality audit; strict=False is synthetic only, never a PASS."""
    require(type(bodies) is dict and set(bodies) == set(BODY_SHAS),
            'three affected HTML bodies absent or expanded')
    require(type(metas) is dict and set(metas) == set(META_SHAS),
            'three affected metadata records absent or expanded')
    blocks, routes = {}, set()
    for slug in BODY_SHAS:
        body, meta = bodies[slug], metas[slug]
        require(type(body) is str and len(body) > 0 and '\x00' not in body,
                'invalid HTML body')
        require(type(meta) is dict and meta.get('slug') == slug and
                meta.get('status', {}).get('publish') == 'draft' and
                meta.get('safety_review', {}).get('state') == 'pending' and
                meta.get('safety_review', {}).get('reviewer') is None and
                meta.get('safety_review', {}).get('date') is None,
                'draft/safety-review authority changed: ' + slug)
        section = 'food' if slug == 'safe-jerky-dehydration' else 'lost-ways'
        require(meta.get('section') == section, 'article section/route drift: ' + slug)
        route = '/preparedness/' + section + '/' + slug + '/'
        require(route not in routes, 'duplicate article URL')
        routes.add(route)
        require(type(meta.get('source_use')) is dict, 'missing source-use record')
        reader = BlockReader()
        reader.feed(body)
        reader.close()
        require(len(reader.blocks) > 0, 'no parseable article blocks')
        blocks[slug] = reader.blocks
    matches = []
    for slug, label, anchor, ids in CLAIMS:
        found = [b for b in blocks[slug] if anchor.casefold() in b.casefold()]
        require(len(found) == 1, 'missing or ambiguous claim anchor: ' + slug + '/' + label)
        segment = found[0]
        cited = set(CITATION.findall(segment))
        require(set(ids).issubset(cited), 'missing same-block source citation: ' + slug + '/' + label)
        require(set(ids).issubset(metas[slug]['source_use']),
                'citation lacks article-level source-use explanation: ' + slug + '/' + label)
        if label == 'not-a-recipe':
            require('no method' in segment.casefold() and 'no storage times' in segment.casefold(),
                    'historical non-instructional guardrail removed')
        if label == 'published-method-conflict':
            require('after' in segment.casefold() and 'more heat resistant' in segment.casefold(),
                    'official disagreement qualifier removed')
        if label == 'agencies-disagree':
            require('before drying' in segment.casefold() and 'after drying' in segment.casefold(),
                    'historical advice disagreement erased')
        matches.append({'slug': slug, 'claim': label, 'source_ids': list(ids),
                        'block_sha256': hashlib.sha256(segment.encode('utf-8')).hexdigest(),
                        'decision': 'PENDING_INDEPENDENT_HUMAN_SOURCE_AND_SAFETY_REVIEW'})
    require(len(matches) == len(CLAIMS), 'incomplete claim review roster')
    if strict:
        require(len(matches) == 10 and len(routes) == 3, 'authentic review size drift')
    return {'schema': SCHEMA, 'state': HOLD, 'claims_flagged_for_human_review': matches,
            'affected_articles': 3, 'source_scope_review_completed': False,
            'medically_or_food_safe': False, 'qualified_reviewer_approved': False,
            'independent_qd_pass': False, 'publication_authorized': False,
            'paid_preparedness_product_verified': False,
            'review_receipt_sha256': hashlib.sha256(json.dumps(matches, sort_keys=True,
                separators=(',', ':')).encode()).hexdigest()}


def pinned(root: Path, path: str, sha: str) -> bytes:
    f = root / path
    require(f.is_file() and not f.is_symlink(), 'missing/symlink original: ' + path)
    data = f.read_bytes()
    require(git_blob(data) == sha, 'original Git identity drift: ' + path)
    return data


def verify(root: Path) -> dict:
    docket = json.loads(pinned(root, 'preparedness/review/r172/jerky-source-impact.json', DOCKET_SHA))
    require(docket.get('state') == HOLD and docket.get('review_decisions') == {
        'url_equivalence': False, 'source_claim_scope': False,
        'qualified_food_safety': False, 'independent_qd': False,
        'founder_publication_authorized': False}, 'R172 decision integrity drift')
    modpath = root / 'preparedness/tools/r172_jerky_alias_claim_gate.py'
    require(modpath.is_file() and not modpath.is_symlink(), 'R172 source gate missing')
    spec = importlib.util.spec_from_file_location('r173_parent_r172', modpath)
    require(spec is not None and spec.loader is not None, 'R172 source gate unreadable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    old = module.verify(root)  # invokes R161 full 35-body / 2000-citation custody
    require(old.get('state') == HOLD and old.get('article_routes') == 35 and
            old.get('source_uses') == 385 and old.get('food_safety_approved') is False,
            'parent source/citation custody failed')
    bodies, metas = {}, {}
    for slug in BODY_SHAS:
        base = 'preparedness/content/articles/' + slug
        bodies[slug] = pinned(root, base + '.body.html', BODY_SHAS[slug]).decode('utf-8')
        metas[slug] = json.loads(pinned(root, base + '.meta.json', META_SHAS[slug]))
    require({x['slug'] for x in docket.get('impacted_articles', [])} == set(BODY_SHAS),
            'original article-impact roster altered')
    return evaluate(bodies, metas)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path('.'))
    options = parser.parse_args(argv)
    try:
        result = verify(options.repo.resolve(strict=True))
    except (ValueError, OSError, TypeError, KeyError, UnicodeError,
            json.JSONDecodeError, ImportError, AttributeError) as error:
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'error': str(error), 'publication_authorized': False}
    print(json.dumps(result, sort_keys=True))
    return 2  # Even a structurally valid, unchanged draft is NOT approved for release.


if __name__ == '__main__':
    raise SystemExit(main())
