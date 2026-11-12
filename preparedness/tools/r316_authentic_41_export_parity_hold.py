#!/usr/bin/env python3
"""R316 read-only 41-item export custody gate, FV Preparedness Issue #136.

Derive WordPress/preview markup from the pinned repository builder, compare
actual generated drafts byte-for-byte and reconcile the build report. No CMS
calls, mutations, revenue claims, source/safety/QD approval or publication.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

SCHEMA = 'fv-preparedness-r316-authentic-41-export-parity-v1'
BUILD_PATH = 'preparedness/tools/build.py'
BUILD_GIT_BLOB = '349173d1e1d735eade218d95c7a0a2649c8cccd9'
R315_PATH = 'preparedness/tools/r315_html5_entity_visible_citation_hold.py'
R315_GIT_BLOB = 'e0518450c3b45e5e8b59a2f5d0f801279be4821b'
EXPECTED_ARTICLES = 35
EXPECTED_TOOLS = 6
EXPECTED_TOTAL = 41
SAFE_SLUG = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def file_bytes(root: Path, rel: str) -> bytes | None:
    """Refuse symlinks at every source/export path component."""
    base = root.resolve(strict=True)
    parts = Path(rel).parts
    if not parts or any(x in ('', '.', '..') for x in parts) or Path(rel).is_absolute():
        return None
    p = base
    for part in parts:
        p = p / part
        if p.is_symlink():
            return None
    if not p.is_file():
        return None
    try:
        return p.read_bytes()
    except OSError:
        return None


def _fingerprint(data: bytes) -> dict:
    return {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}


def _bad(error: str, slug: str | None = None) -> str:
    return error if slug is None else f'{error}:{slug}'


def audit_exports(root: Path, expected: dict[str, dict], report: dict | None,
                  *, allowed_other_slugs: set[str] | None = None) -> dict:
    """Pure fixture-testable parity audit; never generates or edits output.

    expected[slug] contains independently rendered wp/preview bytes and
    words, minutes, sources, canonical from the source-controlled builder.
    """
    errors: list[str] = []
    allowed = {'landing'} | (allowed_other_slugs or set())
    if len(expected) != EXPECTED_TOTAL or len(set(expected)) != EXPECTED_TOTAL or any(
        not isinstance(s, str) or not SAFE_SLUG.fullmatch(s) for s in expected
    ):
        errors.append('EXPECTED_EXACTLY_41_UNIQUE_SAFE_ARTICLE_TOOL_SLUGS')
    if any(not isinstance(x, str) or not SAFE_SLUG.fullmatch(x) for x in allowed):
        errors.append('INVALID_EXTRA_PAGE_ALLOWLIST')
    allowed = {x for x in allowed if isinstance(x, str) and SAFE_SLUG.fullmatch(x)}
    if set(expected) & allowed:
        errors.append('GUIDE_AND_HUB_SLUG_COLLISION')
    receipt: list[dict] = []
    for surface in ('wp', 'preview'):
        directory = root / 'preparedness' / 'build' / surface
        if directory.is_symlink() or not directory.is_dir():
            errors.append('MISSING_OR_LINKED_EXPORT_DIRECTORY:' + surface)
            continue
        actual = {p.name for p in directory.iterdir()}
        wanted = {s + '.html' for s in expected}
        permitted = {s + '.html' for s in allowed}
        if not wanted.issubset(actual):
            errors.extend(_bad('MISSING_REAL_EXPORT:' + surface, s) for s in sorted(wanted - actual))
        if actual - wanted - permitted:
            errors.extend(_bad('UNEXPECTED_EXPORT:' + surface, s) for s in sorted(actual - wanted - permitted))
        if set(x for x in actual if not x.endswith('.html')):
            errors.append('NON_HTML_EXPORT_FILE:' + surface)
        for slug, exp in sorted(expected.items()):
            if not SAFE_SLUG.fullmatch(slug):
                continue
            data = file_bytes(root, f'preparedness/build/{surface}/{slug}.html')
            target = exp.get(surface)
            if data is None:
                errors.append(_bad('MISSING_OR_SYMLINK_EXPORT:' + surface, slug))
                continue
            if not isinstance(target, bytes):
                errors.append(_bad('MISSING_INDEPENDENT_RENDER_EXPECTATION:' + surface, slug))
                continue
            if data != target:
                errors.append(_bad('RENDERED_BYTES_DIFFER_FROM_AUTHENTIC_SOURCES:' + surface, slug))
            if b'\r\n' in data:
                errors.append(_bad('EXPORT_NONDETERMINISTIC_LINE_ENDINGS:' + surface, slug))
            if b'{{cite:' in data or b'{{link:' in data or b'{{inline-js:' in data:
                errors.append(_bad('UNRESOLVED_SOURCE_TOKEN_IN_EXPORT:' + surface, slug))
            if surface == 'wp':
                if not data.startswith(b'<!-- wp:html -->\n') or not data.endswith(b'\n<!-- /wp:html -->\n'):
                    errors.append(_bad('INVALID_WORDPRESS_DRAFT_BLOCK_WRAPPER', slug))
                for witness in (b'Draft: not public',
                                b'Independent safety/source and QD verification pending',
                                b'Sources and verification'):
                    if witness not in data:
                        errors.append(_bad('DRAFT_SOURCE_OR_REVIEW_WARNING_MISSING', slug))
                if ('data-slug="' + slug + '"').encode('ascii') not in data:
                    errors.append(_bad('WRONG_RENDERED_GUIDE_IDENTITY', slug))
            receipt.append({'slug': slug, 'surface': surface, 'actual': _fingerprint(data),
                            'expected': _fingerprint(target), 'equal': data == target})
    if not isinstance(report, dict):
        errors.append('MISSING_AUTHENTIC_BUILD_REPORT')
        rows = []
        release = {}
    else:
        rows = report.get('articles')
        release = report.get('release_evidence')
        if not isinstance(rows, list) or len(rows) != EXPECTED_TOTAL:
            errors.append('BUILD_REPORT_NOT_41_GUIDES')
            rows = rows if isinstance(rows, list) else []
        if not isinstance(release, dict):
            release = {}
    lookup: dict[str, dict] = {}
    for r in rows:
        if not isinstance(r, dict) or not isinstance(r.get('slug'), str):
            errors.append('INVALID_BUILD_REPORT_ROW')
            continue
        slug = r['slug']
        if slug in lookup:
            errors.append('DUPLICATE_BUILD_REPORT_SLUG:' + slug)
        lookup[slug] = r
    if set(lookup) != set(expected):
        errors.append('BUILD_REPORT_GUIDE_SET_DRIFT')
    canonicals = []
    for slug, exp in expected.items():
        r = lookup.get(slug, {})
        if not isinstance(r, dict):
            errors.append(_bad('MISSING_BUILD_REPORT_ROW', slug))
            continue
        for key in ('words', 'minutes', 'sources', 'canonical'):
            if r.get(key) != exp.get(key):
                errors.append(_bad('BUILD_REPORT_READING_DEPTH_CITATION_OR_ROUTE_DRIFT:' + key, slug))
        canonical = r.get('canonical')
        if not isinstance(canonical, str) or not canonical.startswith('https://finalvestige.com/preparedness/') or not canonical.endswith('/'):
            errors.append(_bad('INVALID_CANONICAL_GUIDE_URL', slug))
        canonicals.append(canonical)
    if len(canonicals) != len(set(canonicals)):
        errors.append('DUPLICATE_CANONICAL_GUIDE_URLS')
    for key, value in [('state', 'HOLD'), ('article_drafts', 41), ('article_published', 0),
                       ('wordpress_publication_performed', False), ('independent_qa_verified', False)]:
        if release.get(key) != value or type(release.get(key)) is not type(value):
            errors.append('UNSAFE_OR_UNRECONCILED_RELEASE_EVIDENCE:' + key)
    return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors': sorted(set(errors)), 'expected_guides': len(expected),
            'verified_wordpress_outputs': sum(x['equal'] for x in receipt if x['surface'] == 'wp'),
            'verified_preview_outputs': sum(x['equal'] for x in receipt if x['surface'] == 'preview'),
            'export_receipts': receipt, 'source_safety_qd_approval': False,
            'wordpress_published': False, 'commercial_conversion_verified': False}


def _load_pin(root: Path, rel: str, sha: str):
    data = file_bytes(root, rel)
    if data is None or git_blob(data) != sha:
        raise ValueError('MISSING_OR_MODIFIED_PINNED_CODE:' + rel)
    spec = importlib.util.spec_from_file_location('fv_r316_pinned_' + Path(rel).stem, root / rel)
    if spec is None or spec.loader is None:
        raise ValueError('PINNED_CODE_IMPORT_FAILED:' + rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(root: Path) -> dict:
    """Complete authentic checkout only. Partial and stale trees fail closed."""
    root = root.resolve(strict=True)
    build = _load_pin(root, BUILD_PATH, BUILD_GIT_BLOB)
    r315 = _load_pin(root, R315_PATH, R315_GIT_BLOB)
    inherited = r315.run(root)
    led_bytes = file_bytes(root, r315.r312.LEDGER)
    if led_bytes is None or git_blob(led_bytes) != r315.r312.LEDGER_OID:
        raise ValueError('PINNED_35_ARTICLE_LINEAGE_MISSING')
    ledger = json.loads(led_bytes)
    arts = [r['slug'] for r in ledger['articles']]
    tools = list(r315.r310.SLUGS)
    if len(arts) != EXPECTED_ARTICLES or len(tools) != EXPECTED_TOOLS or len(set(arts + tools)) != EXPECTED_TOTAL:
        raise ValueError('SOURCE_SLATE_MISSING_DUPLICATE_OR_INCOMPLETE')
    lib = build.Library(root=root / 'preparedness')
    if set(lib.articles) != set(arts + tools):
        raise ValueError('BUILDER_LOADED_WRONG_ARTICLE_TOOL_SET')
    expected = {}
    for slug in arts + tools:
        rendered = build.build_article(lib, slug)
        meta = rendered['meta']
        expected[slug] = {
            'wp': build.wp_wrap(lib, rendered['inner']).encode('utf-8'),
            'preview': build.preview_wrap(lib, rendered['inner'],
                         f"{meta['h1']} | The Preparedness Archive", meta['description']).encode('utf-8'),
            'words': rendered['words'], 'minutes': rendered['minutes'],
            'sources': rendered['sources'], 'canonical': rendered['canonical']
        }
    report_raw = file_bytes(root, 'preparedness/build/build-report.json')
    report = json.loads(report_raw) if report_raw else None
    result = audit_exports(root, expected, report,
                           allowed_other_slugs={'hub-' + s for s in lib.sections})
    result['inherited_article_citation_safety_state'] = inherited['state']
    result['inherited_errors'] = inherited.get('errors', [])
    if inherited['state'] != 'DRAFT_HARD_HOLD' or inherited.get('errors'):
        result['errors'] += ['INHERITED_R315:' + x for x in inherited.get('errors', [])]
        result['errors'] = sorted(set(result['errors']))
        result['state'] = 'INVALID_HARD_HOLD'
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Read-only authentic FV 41-guide WP/preview parity gate')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        outcome = run(args.root)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:
        outcome = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                   'errors': ['AUTHENTIC_41_EXPORT_PROOF_UNAVAILABLE:' + type(error).__name__],
                   'source_safety_qd_approval': False, 'wordpress_published': False,
                   'commercial_conversion_verified': False}
    print(json.dumps(outcome, sort_keys=True, indent=2))
    return 1 if outcome['state'] == 'INVALID_HARD_HOLD' else 2


if __name__ == '__main__':
    raise SystemExit(main())
