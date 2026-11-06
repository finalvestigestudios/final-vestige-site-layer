#!/usr/bin/env python3
"""R161 fail-closed custody check for 35 original Preparedness article bodies.

Pins are reviewer evidence, NOT confirmation that any cited claim is correct.
Exit 2 even on a clean frozen snapshot: publication remains DRAFT/HARD HOLD.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

R151 = 'preparedness/docs/r151/contributor-three-way.json'
R151_BLOB = '9cf386519eda970209ff6be4ff0243661cd9d996'
R161 = 'preparedness/docs/r161/body_custody.json'
R161_BLOB = 'fede4222c796d92798eff7cf0dcb225c291f7d61'
ARTICLE_DIR = 'preparedness/content/articles'
SCHEMA = 'fv-preparedness-r161-body-custody-v1'
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
ANY_CITE = re.compile(r'\{\{\s*cite\b[^}]*\}\}', re.I)
WORD = re.compile(r'[A-Za-z0-9_’\-]+')
TAGS = re.compile(r'<[^>]*>')
SPACE = re.compile(r'\s+')


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def read(root: Path, name: str, expected: str | None = None) -> bytes:
    path = root / name
    require(path.is_file() and not path.is_symlink(), 'missing or symlink: ' + name)
    data = path.read_bytes()
    if expected:
        require(git_blob(data) == expected, 'Git blob drift: ' + name)
    return data


def words(html: str) -> int:
    without_cites = CITE.sub(' ', html)
    text = SPACE.sub(' ', TAGS.sub(' ', without_cites))
    return len(WORD.findall(text))


def verify(root: Path, baseline: dict | None = None, legacy: dict | None = None) -> dict:
    """Verify frozen content. Inject baseline/legacy ONLY for synthetic unit tests."""
    if baseline is None:
        baseline = json.loads(read(root, R161, R161_BLOB))
    if legacy is None:
        legacy = json.loads(read(root, R151, R151_BLOB))
    require(baseline.get('schema') == SCHEMA and baseline.get('status') == 'DRAFT_HARD_HOLD', 'body manifest schema/hold invalid')
    require(baseline.get('source_commit') and re.fullmatch('[0-9a-f]{40}', baseline['source_commit']), 'missing exact snapshot ref')
    require(legacy.get('schema') == 'fv-preparedness-r151-v1' and legacy.get('decision') == 'DRAFT_HARD_HOLD', 'R151 identity/hold invalid')
    if baseline.get('r151_manifest_git_blob'):
        # Canonical R151 on disk is authenticated by the pinned Git blob above.
        require(baseline['r151_manifest_git_blob'] == R151_BLOB, 'R151 trust anchor drift')
    article_pins = baseline.get('articles')
    meta_pins = legacy.get('metadata_blobs')
    require(isinstance(article_pins, dict) and len(article_pins) == 35, 'must pin 35 article bodies')
    require(isinstance(meta_pins, dict) and len(meta_pins) == 35, 'must pin 35 metadata files')
    require(set(article_pins) == set(meta_pins), 'body / metadata slug set mismatch')
    require(baseline.get('article_count') == 35, 'body census expectation changed')
    directory = root / ARTICLE_DIR
    require(directory.is_dir() and not directory.is_symlink(), 'article directory missing or symlink')
    bodies = {p.name[:-10] for p in directory.glob('*.body.html')}
    metas = {p.name[:-10] for p in directory.glob('*.meta.json')}
    require(bodies == metas == set(article_pins), '35 original article pairs changed')
    routes, receipts = set(), []
    citations, source_uses = 0, 0
    states = {'pending': 0, 'not-required': 0, 'approved': 0}
    candidate = {x['slug']: x['candidate']['blob'] for x in legacy.get('articles', [])}
    for slug in sorted(article_pins):
        require(SLUG.fullmatch(slug), 'unsafe slug: ' + str(slug))
        entry = article_pins[slug]
        require(isinstance(entry, dict), 'malformed body pin: ' + slug)
        sha, num = entry.get('git_blob'), entry.get('citations')
        require(isinstance(sha, str) and re.fullmatch('[0-9a-f]{40}', sha), 'malformed body blob pin: ' + slug)
        require(type(num) is int and num >= 20, 'malformed citation count pin: ' + slug)
        if slug in candidate:
            require(sha == candidate[slug], 'seven-branch resolution not preserved: ' + slug)
        body_bytes = read(root, f'{ARTICLE_DIR}/{slug}.body.html', sha)
        meta = json.loads(read(root, f'{ARTICLE_DIR}/{slug}.meta.json', meta_pins[slug]))
        html = body_bytes.decode('utf-8')
        marks = CITE.findall(html)
        require(len(marks) == len(ANY_CITE.findall(html)) == num, 'citation count/markup drift: ' + slug)
        require(words(html) >= 1500, 'reading-depth below minimum: ' + slug)
        require(meta.get('slug') == slug and meta.get('status', {}).get('publish') == 'draft', 'article identity/publication drift: ' + slug)
        state = meta.get('safety_review', {}).get('state')
        require(state in states, 'invalid recorded safety state: ' + slug)
        states[state] += 1
        section = meta.get('section')
        require(isinstance(section, str) and SLUG.fullmatch(section), 'unsafe section: ' + slug)
        route = f'/preparedness/{section}/{slug}/'
        require(route not in routes, 'duplicate route: ' + route)
        routes.add(route)
        uses = meta.get('source_use')
        require(isinstance(uses, dict) and bool(uses), 'missing author source interpretations: ' + slug)
        require(set(marks) == set(uses), 'unmapped or orphaned citation: ' + slug)
        require(all(SLUG.fullmatch(k) and isinstance(v, str) and len(v.strip()) >= 8 for k,v in uses.items()), 'invalid source interpretation: ' + slug)
        citations += len(marks)
        source_uses += len(uses)
        receipts.append({'slug': slug, 'body_git_blob': sha, 'citations': len(marks), 'route': route, 'recorded_safety_state': state})
    require(citations == baseline.get('total_citations'), 'total original citations changed')
    require(source_uses == baseline.get('article_source_relationships'), 'original source-use count changed')
    require(states == {'pending': 29, 'not-required': 4, 'approved': 2}, 'recorded safety-state distribution changed')
    receipt_hash = hashlib.sha256(json.dumps(receipts, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    return {'schema': SCHEMA, 'state': 'DRAFT_HARD_HOLD', 'articles': len(receipts),
            'routes': len(routes), 'citations': citations, 'source_uses': source_uses,
            'recorded_safety_states_not_approvals': states, 'custody_receipt_sha256': receipt_hash,
            'claim_verification': False, 'independent_safety_review': False,
            'independent_qd_pass': False, 'paid_offer_verified': False,
            'publication_authorized': False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    try:
        report = verify(args.repo.resolve(strict=True))
    except (ValueError, OSError, UnicodeError, TypeError, KeyError, json.JSONDecodeError) as error:
        report = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD', 'error': str(error), 'publication_authorized': False}
    print(json.dumps(report, sort_keys=True))
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
