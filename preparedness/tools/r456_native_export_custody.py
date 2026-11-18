#!/usr/bin/env python3
"""R456: read-only full Preparedness slate/WordPress export custody preflight.

This is a machine integrity HOLD gate, NOT editorial, emergency, food, clinical,
privacy, checkout, qualified QD or publication clearance. It REQUIRES a complete
native 35-article checkout, original files, BOTH real build output directories,
and build-report.json. It never creates source, builds, drafts or CMS changes.

Usage: python preparedness/tools/r456_native_export_custody.py --root preparedness
       (after native validate.py and build.py have independently succeeded)
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

HOLD = 'DRAFT_HARD_HOLD'
SLATE_SIZE = 35
MAX_FILE = 5_000_000
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


class CustodyHold(ValueError):
    """Fail-closed integrity decision; never a qualified review result."""


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_bytes_checked(root: Path, path: Path, *, label: str) -> bytes:
    """Avoid symlinks, traversal, oversized/unavailable evidence, and IO writes."""
    if not path.is_relative_to(root):
        raise CustodyHold(f'{label}: path outside checkout')
    for component in (path, *tuple(path.parents)[:len(path.relative_to(root).parts)]):
        if component.is_symlink():
            raise CustodyHold(f'{label}: linked path is not original evidence')
    if not path.is_file():
        raise CustodyHold(f'{label}: missing actual file {path.name}')
    if path.stat().st_size > MAX_FILE or path.stat().st_size == 0:
        raise CustodyHold(f'{label}: empty/oversized evidence')
    return path.read_bytes()


def load_local_json(root: Path, path: Path, label: str):
    try:
        return json.loads(read_bytes_checked(root, path, label=label))
    except (ValueError, UnicodeError) as exc:
        raise CustodyHold(f'{label}: malformed JSON: {exc}') from exc


def extract_canonical(url: str) -> str:
    if not isinstance(url, str) or not url.startswith('https://'):
        raise CustodyHold('canonical URL must be absolute HTTPS')
    parts = urlsplit(url)
    if parts.hostname != 'finalvestige.com' or parts.username or parts.password or parts.port:
        raise CustodyHold('canonical URL changes site authority')
    if parts.query or parts.fragment or parts.path.startswith('//') or not parts.path.endswith('/'):
        raise CustodyHold('canonical URL contains query/fragment or bad route')
    if '//' in parts.path or '/./' in parts.path or '/../' in parts.path or '%' in parts.path:
        raise CustodyHold('canonical route collision or path ambiguity')
    return url


def unique_rows(rows: list[dict], key: str, *, label: str) -> dict:
    if not isinstance(rows, list) or any(not isinstance(r, dict) or not isinstance(r.get(key), str) for r in rows):
        raise CustodyHold(f'{label}: malformed inventory')
    if len(rows) != len({r[key] for r in rows}):
        raise CustodyHold(f'{label}: duplicate {key}')
    return {r[key]: r for r in rows}


def validate_report(report: dict, expected: set[str]) -> dict[str, dict]:
    if not isinstance(report, dict) or not isinstance(report.get('release_evidence'), dict):
        raise CustodyHold('build-report missing explicit release hold')
    evidence = report['release_evidence']
    if evidence.get('state') not in ('HOLD', 'REQUIRES_INDEPENDENT_QA'):
        raise CustodyHold('build report attempts unsupported release advancement')
    if evidence.get('independent_qa_verified') is not False:
        raise CustodyHold('build report claims unverified independent QD approval')
    if evidence.get('wordpress_publication_performed') is not False:
        raise CustodyHold('build report claims/records public publication')
    index = unique_rows(report.get('articles'), 'slug', label='build report')
    if set(index) != expected:
        raise CustodyHold(f'build article inventory does not equal authentic source inventory: missing={sorted(expected-set(index))} extra={sorted(set(index)-expected)}')
    return index


def assert_slug(slug: str) -> None:
    if not isinstance(slug, str) or not SLUG.fullmatch(slug):
        raise CustodyHold('invalid or dangerous article slug')


def assert_wrapper(raw_wp: str, raw_preview: str, slug: str) -> None:
    if not raw_wp.startswith('<!-- wp:html -->') or not raw_wp.rstrip().endswith('<!-- /wp:html -->'):
        raise CustodyHold(f'{slug}: missing WordPress draft block envelope')
    if '<meta name="robots" content="noindex,nofollow">' not in raw_preview:
        raise CustodyHold(f'{slug}: preview not explicitly noindex,nofollow')
    if raw_wp.count(f'data-slug="{slug}"') != 1 or raw_preview.count(f'data-slug="{slug}"') != 1:
        raise CustodyHold(f'{slug}: export surface identity ambiguous')
    for unsafe in ('{{cite:', '{{ cite:', 'data-published="true"', 'data-qd-pass="true"'):
        if unsafe in raw_wp or unsafe in raw_preview:
            raise CustodyHold(f'{slug}: unresolved citation or unsafe status claim')


def verify_native(root: Path, library, parity) -> dict:
    """Use actual build.Library to respect contributor-specific sources and scopes.

    library and parity can be injected ONLY by isolated test harnesses; the CLI
    loads exact Python code from the provided local Preparedness checkout.
    """
    if not root.is_dir() or root.is_symlink():
        raise CustodyHold('native Preparedness root absent/linked')
    taxonomy = load_local_json(root, root / 'taxonomy.json', 'taxonomy')
    if not isinstance(taxonomy, dict):
        raise CustodyHold('malformed taxonomy root')
    slate = unique_rows(taxonomy.get('slate'), 'slug', label='original slate')
    if len(slate) != SLATE_SIZE:
        raise CustodyHold(f'expected exactly {SLATE_SIZE} original slate identities')
    articles = library.articles
    if not isinstance(articles, dict) or not set(slate).issubset(articles):
        raise CustodyHold('slate article bodies or metadata missing')
    for slug in articles:
        assert_slug(slug)
    # Real build report only. Missing report is a hard hold; no synthetic substitute.
    report = load_local_json(root, root / 'build' / 'build-report.json', 'native build-report')
    indexed = validate_report(report, set(articles))
    receipt: list[dict] = []
    seen_canonicals: set[str] = set()
    globally_seen_ids: dict[str, str] = {}
    shared_url_ids: dict[str, set[str]] = defaultdict(set)
    file_seen: set[str] = set()

    for slug in sorted(articles):
        meta = articles[slug]
        if not isinstance(meta, dict) or meta.get('slug') != slug:
            raise CustodyHold(f'{slug}: invalid source metadata identity')
        is_tool = meta.get('kind') == 'tool'
        folder = 'tools' if is_tool else 'articles'
        source_meta_path = root / 'content' / folder / f'{slug}.meta.json'
        source_body_path = root / 'content' / folder / f'{slug}.body.html'
        meta_bytes = read_bytes_checked(root, source_meta_path, label=f'{slug}: source metadata')
        try:
            disk_meta = json.loads(meta_bytes)
        except (ValueError, UnicodeError) as exc:
            raise CustodyHold(f'{slug}: malformed source metadata: {exc}') from exc
        if disk_meta.get('slug') != slug:
            raise CustodyHold(f'{slug}: source metadata file mismatch')
        body_bytes = read_bytes_checked(root, source_body_path, label=f'{slug}: original body')
        body = body_bytes.decode('utf-8', 'strict')
        if body != meta.get('_body'):
            raise CustodyHold(f'{slug}: build library changed article body from disk')
        wp_path = root / 'build' / 'wp' / f'{slug}.html'
        prev_path = root / 'build' / 'preview' / f'{slug}.html'
        wp_bytes = read_bytes_checked(root, wp_path, label=f'{slug}: real WordPress draft')
        prev_bytes = read_bytes_checked(root, prev_path, label=f'{slug}: real private preview')
        wp, preview = wp_bytes.decode('utf-8', 'strict'), prev_bytes.decode('utf-8', 'strict')
        assert_wrapper(wp, preview, slug)
        order = parity.authored_order(body)
        selected = {}
        for sid in order:
            src = library.source_for(meta, sid)
            if not isinstance(src, dict) or any(not src.get(k) for k in ('id', 'url', 'supports', 'title', 'publisher')):
                raise CustodyHold(f'{slug}: source identity or documented reading depth missing')
            if src['id'] != sid:
                raise CustodyHold(f'{slug}: wrong source selected')
            if sid in globally_seen_ids and globally_seen_ids[sid] != src['url']:
                raise CustodyHold(f'{slug}: same source ID reassigned to different URL')
            globally_seen_ids[sid] = src['url']
            shared_url_ids[src['url']].add(sid)
            selected[sid] = src
        # Checks exact citation number, title, URL, publisher, article-specific
        # Used for text, human-link-check status on BOTH rendered surfaces.
        try:
            pair = parity.verify_pair(body, selected, wp, preview, meta.get('source_use'))
        except (ValueError, TypeError, KeyError) as exc:
            raise CustodyHold(f'{slug}: R455 rendered citation/source integrity failure: {exc}') from exc
        canonical = extract_canonical(indexed[slug].get('canonical'))
        expected_url = extract_canonical('https://finalvestige.com' + library.url_path(slug))
        if canonical != expected_url or canonical in seen_canonicals:
            raise CustodyHold(f'{slug}: duplicate/changed canonical article destination')
        seen_canonicals.add(canonical)
        if indexed[slug].get('sources') != order:
            raise CustodyHold(f'{slug}: build report source IDs not original authored order')
        for p in (source_meta_path, source_body_path, wp_path, prev_path):
            if str(p) in file_seen:
                raise CustodyHold(f'{slug}: reused source/export file identity')
            file_seen.add(str(p))
        receipt.append({'slug': slug, 'kind': 'tool' if is_tool else 'article',
                        'canonical': canonical, 'source_ids': order,
                        'source_occurrences': pair['parity']['citation_occurrences'],
                        'sha256': {'meta': digest(meta_bytes), 'body': digest(body_bytes),
                                   'wp': digest(wp_bytes), 'preview': digest(prev_bytes)}})
    if len([x for x in receipt if x['slug'] in slate]) != SLATE_SIZE:
        raise CustodyHold('original slate not completely verified')
    # The original 17 shared-URL conflicts are a HUMAN review queue; never
    # collapse or clear them merely because output references are consistent.
    return {'release_state': HOLD, 'qualified_qd_pass': False,
            'source_claim_support_verified': False,
            'human_emergency_food_medical_review': 'NOT_APPROVED',
            'wordpress_published': False, 'native_full_build': 'NOT_ATTESTED_BY_THIS_GATE',
            'original_slate_items_checked': SLATE_SIZE, 'total_entries_checked': len(receipt),
            'rendered_surfaces_checked': len(receipt)*2,
            'shared_literal_urls_distinct_ids': sum(len(ids)>1 for ids in shared_url_ids.values()),
            'entries': receipt}


def trusted_module(path: Path, label: str):
    if not path.is_file() or path.is_symlink():
        raise CustodyHold(f'{label}: missing/linked checkout module')
    spec = importlib.util.spec_from_file_location('r456_' + label, path)
    if not spec or not spec.loader:
        raise CustodyHold(f'{label}: cannot load module')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='existing native preparedness/ checkout')
    args = parser.parse_args(argv)
    root = args.root.absolute()
    try:
        b = trusted_module(root/'tools'/'build.py', 'build')
        p = trusted_module(root/'tools'/'r455_rendered_citation_parity.py', 'parity')
        result = verify_native(root, b.Library(root), p)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (CustodyHold, OSError, ValueError, KeyError, UnicodeError, TypeError, AttributeError) as exc:
        print(json.dumps({'release_state': HOLD, 'qualified_qd_pass': False,
                          'wordpress_published': False, 'integrity': 'HOLD', 'error': str(exc)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
