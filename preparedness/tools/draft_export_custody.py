#!/usr/bin/env python3
"""R11: read-only, fail-closed custody audit of local WordPress DRAFT exports.

Does not build, publish, write, clean directories, decide safety, or verify claims.
The authoritative local checkout is re-rendered *byte for byte* and compared with
both WordPress block HTML and standalone noindex previews. Extra/stale artifacts
are a fatal error; this is not a WordPress importer.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_HTML_BYTES = 1024 * 1024
MAX_REPORT_BYTES = 8 * 1024 * 1024
SLUG_RE = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


class CustodyFailure(ValueError):
    """An export cannot be proven to correspond to this exact frozen draft corpus."""


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _check_slug(value: str, label: str) -> str:
    if not isinstance(value, str) or SLUG_RE.fullmatch(value) is None:
        raise CustodyFailure(f'{label}: invalid artifact slug')
    return value


def _plain_file(path: Path, parent: Path, limit: int) -> bytes:
    if path.parent != parent or path.is_symlink() or not path.is_file():
        raise CustodyFailure(f'{path.name}: absent, symlink, or wrong parent')
    st = path.stat()
    if st.st_size < 2 or st.st_size > limit or st.st_nlink != 1:
        raise CustodyFailure(f'{path.name}: empty, oversized or hard-linked artifact')
    return path.read_bytes()


def _verify_dir(path: Path, expected: set[str]) -> None:
    if path.is_symlink() or not path.is_dir():
        raise CustodyFailure(f'{path.name}: missing or unsafe directory')
    actual = {p.name for p in path.iterdir()}
    if actual != expected:
        raise CustodyFailure(f'{path.name}: stale, extra, or missing files: ' +
                             f'added={sorted(actual-expected)[:6]} missing={sorted(expected-actual)[:6]}')
    for child in path.iterdir():
        if child.is_symlink() or not child.is_file():
            raise CustodyFailure(f'{path.name}: nested directory, symlink or nonfile')


def _safe_build_root(lib, out: Path) -> Path:
    original = Path(lib.root)
    if original.is_symlink() or not original.is_dir():
        raise CustodyFailure('checkout: missing or symlinked root')
    expected = original / 'build'
    # Require physical identity, not merely an absolute path whose prefix fits.
    if out != expected or out.is_symlink() or not out.is_dir() or out.resolve() != expected.resolve():
        raise CustodyFailure('build: audit is restricted to the exact checkout/build directory')
    return out


def _expected_report(lib, renderer, articles: list[dict], hubs: list[dict], landing: dict) -> dict:
    # Re-derive rather than accept release-state counters from an existing file.
    variants = [s for versions in lib.source_variants.values() for s in versions]
    unresolved = sum(g.get('review_status') != 'resolved' for g in lib.crosswalk_groups.values())
    has_drafts = any(m['status']['publish'] != 'published' for m in lib.articles.values())
    return {
        'articles': [{k: item[k] for k in ('slug', 'words', 'minutes', 'sources', 'canonical')}
                     for item in articles],
        'landing': {k: landing[k] for k in ('populated_sections', 'article_cards')},
        'release_evidence': {
            'state': 'HOLD' if unresolved or has_drafts else 'REQUIRES_INDEPENDENT_QA',
            'note': 'A build artifact is not permission to publish or proof of medical/food/water safety.',
            'article_drafts': sum(m['status']['publish'] == 'draft' for m in lib.articles.values()),
            'article_published': sum(m['status']['publish'] == 'published' for m in lib.articles.values()),
            'raw_source_rows': len(variants),
            'human_link_checked_rows': sum(s.get('human_link_check') is True for s in variants),
            'source_collision_groups': len(lib.crosswalk_groups),
            'unresolved_collisions': unresolved,
            'independent_qa_verified': False,
            'wordpress_publication_performed': False,
        },
        'slate_status': dict(Counter(renderer.slate_status(lib, item['slug']) for item in lib.taxonomy['slate'])),
        'hubs': [{'section': item['section'], 'guides': item['guides']} for item in hubs],
    }


def _first_difference(a, b, path='$') -> str | None:
    # Avoid printing draft content or potentially sensitive reviewer input.
    if type(a) is not type(b):
        return path + ': type'
    if isinstance(b, dict):
        if a.keys() != b.keys():
            return path + ': keys'
        for key in sorted(b):
            mismatch = _first_difference(a[key], b[key], path + '.' + key)
            if mismatch:
                return mismatch
        return None
    if isinstance(b, list):
        if len(a) != len(b):
            return path + ': length'
        for pos, (x, y) in enumerate(zip(a, b)):
            mismatch = _first_difference(x, y, path + '[' + str(pos) + ']')
            if mismatch:
                return mismatch
        return None
    return None if a == b else path + ': value'


def audit_export(lib, out: Path, renderer, *, expected_articles=35, expected_tools=1,
                 expected_source_rows=224, expected_shared_groups=30,
                 expected_human_links=0, canonical_receipt: dict | None = None) -> dict:
    """Verify byte-for-byte draft/preview parity with exact current source inputs.

    A caller must independently execute the source freeze, `validate.validate`,
    and the R10 canonical gate; CLI does all three before calling this routine.
    The optional canonical receipt must be *recomputed*, never a reused approval.
    """
    out = _safe_build_root(lib, Path(out))
    if len(lib.articles) != expected_articles + expected_tools:
        raise CustodyFailure('corpus: expected 35 article drafts and one planning tool')
    if any(m.get('status', {}).get('publish') != 'draft' for m in lib.articles.values()):
        raise CustodyFailure('corpus: non-draft content; artifact custody is HOLD-only')
    slate = lib.taxonomy.get('slate')
    if not isinstance(slate, list) or len(slate) != expected_articles:
        raise CustodyFailure('corpus: taxonomy slate changed')
    slugs = [_check_slug(k, 'article') for k in lib.articles]
    if len(set(slugs)) != len(slugs):
        raise CustodyFailure('corpus: repeated article key')
    sections = lib.taxonomy.get('sections')
    if not isinstance(sections, list):
        raise CustodyFailure('taxonomy: no sections')
    if any(not isinstance(s, dict) for s in sections):
        raise CustodyFailure('taxonomy: malformed section')
    section_slugs = [_check_slug(s.get('slug'), 'section') for s in sections]
    if len(section_slugs) != len(set(section_slugs)):
        raise CustodyFailure('taxonomy: duplicate sections')
    variants = [row for variants in lib.source_variants.values() for row in variants]
    unresolved = sum(g.get('review_status') != 'resolved' for g in lib.crosswalk_groups.values())
    if (len(variants) != expected_source_rows or len(lib.crosswalk_groups) != expected_shared_groups
            or unresolved != expected_shared_groups
            or sum(row.get('human_link_check') is True for row in variants) != expected_human_links):
        raise CustodyFailure('source: expected unresolved, non-human-verified source-custody baseline changed')
    if canonical_receipt is not None:
        if (canonical_receipt.get('release_state') != 'HOLD'
                or canonical_receipt.get('may_publish') is not False
                or canonical_receipt.get('independent_human_source_checks_verified') != 0
                or canonical_receipt.get('qualified_safety_approvals') != 0
                or canonical_receipt.get('editorial', {}).get('draft_items') != len(lib.articles)
                or canonical_receipt.get('sources', {}).get('physical_source_records') != len(variants)):
            raise CustodyFailure('canonical R10 receipt: not a current HOLD-only corpus result')

    articles = [renderer.build_article(lib, slug) for slug in slugs]
    hubs = []
    artifacts: dict[str, str] = {}
    preview_map: dict[str, str] = {}
    for built in articles:
        slug = _check_slug(built['slug'], 'rendered article')
        if slug not in lib.articles or built['meta'] is not lib.articles[slug]:
            raise CustodyFailure('render: returned article identity does not match corpus')
        artifacts[slug + '.html'] = renderer.wp_wrap(lib, built['inner'])
        preview_map[slug + '.html'] = renderer.preview_wrap(
            lib, built['inner'], f'{built["meta"]["h1"]} | The Preparedness Archive',
            built['meta']['description'])
    for section in section_slugs:
        hub = renderer.build_hub(lib, section, include_drafts=True)
        if hub is None:
            continue
        slug = _check_slug(hub['slug'], 'rendered hub')
        if slug != 'hub-' + section or slug in lib.articles or slug + '.html' in artifacts:
            raise CustodyFailure('render: hub route collision or changed identity')
        artifacts[slug + '.html'] = renderer.wp_wrap(lib, hub['inner'])
        preview_map[slug + '.html'] = renderer.preview_wrap(lib, hub['inner'], hub['title'], hub['description'])
        hubs.append({'section': section, 'guides': hub['count']})
    if 'landing' in lib.articles or 'landing.html' in artifacts:
        raise CustodyFailure('render: landing collides with article')
    landing = renderer.build_landing(lib, include_drafts=True)
    artifacts['landing.html'] = renderer.wp_wrap(lib, landing['inner'])
    preview_map['landing.html'] = renderer.preview_wrap(
        lib, landing['inner'], 'The Preparedness Archive | Final Vestige',
        'Evidence-based household preparedness and a historical record of how earlier generations managed without modern infrastructure.')
    wp_dir, preview_dir = out / 'wp', out / 'preview'
    _verify_dir(wp_dir, set(artifacts))
    _verify_dir(preview_dir, set(preview_map))
    file_hashes = {}
    for filename in sorted(artifacts):
        expected_wp = artifacts[filename].encode('utf-8')
        expected_preview = preview_map[filename].encode('utf-8')
        wp = _plain_file(wp_dir / filename, wp_dir, MAX_HTML_BYTES)
        preview = _plain_file(preview_dir / filename, preview_dir, MAX_HTML_BYTES)
        if wp != expected_wp or preview != expected_preview:
            raise CustodyFailure(f'{filename}: source-to-export byte mismatch; stale/edited output')
        if b'<!-- wp:html -->' not in wp or b'<!-- /wp:html -->' not in wp:
            raise CustodyFailure(f'{filename}: expected WordPress draft wrapper absent')
        if b'<meta name="robots" content="noindex,nofollow">' not in preview:
            raise CustodyFailure(f'{filename}: non-indexable local preview protection absent')
        file_hashes[filename] = {'wp_sha256': _digest(wp), 'preview_sha256': _digest(preview)}
    raw_report = _plain_file(out / 'build-report.json', out, MAX_REPORT_BYTES)
    try:
        loaded_report = json.loads(raw_report.decode('utf-8'))
    except (UnicodeError, ValueError) as e:
        raise CustodyFailure('build report: invalid JSON or encoding') from e
    expected_report = _expected_report(lib, renderer, articles, hubs, landing)
    diff = _first_difference(loaded_report, expected_report)
    if diff is not None:
        raise CustodyFailure('build report: not authoritative: ' + diff)
    release = loaded_report['release_evidence']
    if (release['state'] != 'HOLD' or release['wordpress_publication_performed'] is not False
            or release['independent_qa_verified'] is not False or release['article_published'] != 0
            or release['unresolved_collisions'] != expected_shared_groups
            or release['human_link_checked_rows'] != expected_human_links):
        raise CustodyFailure('build report: unsafe or misleading release assertion')
    return {
        'schema_version': 1,
        'authority': 'MACHINE_LOCAL_DRAFT_EXPORT_CUSTODY_ONLY',
        'release_state': 'HOLD', 'may_publish': False,
        'does_not_verify_medical_food_water_or_fire_safety': True,
        'requires_human_source_and_independent_QD_review': True,
        'does_not_write_to_wordpress': True,
        'article_drafts': expected_articles,
        'tool_drafts': expected_tools,
        'word_press_draft_artifacts': len(artifacts),
        'preview_artifacts': len(preview_map),
        'unresolved_shared_source_groups': expected_shared_groups,
        'verified_human_source_links': expected_human_links,
        'report_sha256': _digest(raw_report),
        'artifact_index_sha256': _digest(json.dumps(file_hashes, sort_keys=True, separators=(',', ':')).encode('utf-8')),
        'artifacts': file_hashes,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json-out', type=Path, help='Optional private HOLD receipt within preparedness/build only')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tools'))
    import build, evidence_freeze, validate, claim_corpus_release_gate, source_review_queue
    lib = build.Library(root)
    frozen_errors = evidence_freeze.verify(lib)
    if frozen_errors:
        raise CustodyFailure('frozen-source lock failed: ' + '; '.join(frozen_errors[:3]))
    validation_errors, _ = validate.validate(lib)
    if validation_errors:
        raise CustodyFailure('source/article validator failed: ' + '; '.join(validation_errors[:3]))
    receipt = claim_corpus_release_gate.audit_corpus(
        lib, source_review_queue.source_rows(root), evidence_freeze.fingerprint)
    result = audit_export(lib, root / 'build', build, canonical_receipt=receipt)
    if args.json_out is not None:
        # Reuse existing R8 guarded local export. This is not an upload endpoint.
        from claim_occurrence_audit import safe_export
        safe_export(args.json_out, json.dumps(result, sort_keys=True, indent=2) + '\n', root / 'build')
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())