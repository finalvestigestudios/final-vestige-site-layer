"""R389 Preparedness candidate-intersection and private-export integration custody.

Read-only. Correlates original Git-blob manuscript candidates across independent
source-impact, URL-alias, WordPress/preview-parity and claim-anchor audits.
A pass never selects a manuscript, verifies emergency advice, clears qualified
review, authorizes merchant offers, or approves publication.

Usage: python preparedness/tools/r389_integrated_candidate_custody.py
       --repo . --wp preparedness/build/wp --preview preparedness/build/preview
Always exits 2: this is an evidence docket, not a release gate.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parent
ORIGINAL_PINS = (
    '5e7d9a8972872c82b4bc46ac13aab18883d8149a',
    '24b49f0a423119c2f612455f021669709a3f22b5',
    'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
)
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
SHA = re.compile(r'[a-f0-9]{40}\Z')
REVIEW_STATUSES = {
    'packet': 'REVIEW_PACKET_HARD_HOLD',
    'impact': 'SOURCE_IMPACT_REVIEW_HARD_HOLD',
    'alias': 'SOURCE_URL_ALIAS_REVIEW_HARD_HOLD',
    'render': 'RENDER_PARITY_REVIEW_HARD_HOLD',
    'anchor': 'CLAIM_POSITION_REVIEW_HARD_HOLD',
}


def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw, usedforsecurity=False).hexdigest()


def load_dependency(name: str):
    file = ROOT / (name + '.py')
    if not file.is_file() or file.is_symlink():
        raise OSError('DEPENDENCY_NOT_LOCAL')
    spec = importlib.util.spec_from_file_location('r389_' + name, file)
    if not spec or not spec.loader:
        raise ImportError('DEPENDENCY_NOT_IMPORTABLE')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _candidate(row: dict, tag: str) -> tuple[str, str] | None:
    if not isinstance(row, dict):
        return None
    branch, sha = row.get('branch'), row.get('body_sha')
    if not isinstance(branch, str) or not branch.startswith('claude/prep-') or not isinstance(sha, str) or not SHA.fullmatch(sha):
        return None
    return branch, sha


def _inventory(directory: Path) -> tuple[set[str], list[str]]:
    errors = []
    if not directory.is_dir() or directory.is_symlink():
        return set(), ['MISSING_OR_SYMLINK_EXPORT_DIRECTORY']
    names = set()
    try:
        for item in sorted(directory.iterdir()):
            if item.is_symlink() or not item.is_file():
                errors.append('UNSAFE_EXPORT_ENTRY:' + item.name)
                continue
            if item.suffix.lower() != '.html' or not SLUG.fullmatch(item.stem):
                errors.append('UNEXPECTED_EXPORT_FILENAME:' + item.name)
                continue
            if item.stat().st_size > 3_000_000 or item.stat().st_size == 0:
                errors.append('EXPORT_SIZE_INVALID:' + item.name)
            names.add(item.stem)
    except OSError:
        errors.append('EXPORT_DIRECTORY_READ_FAILED')
    return names, errors


def reconcile(packet: dict, impact: dict, alias: dict, render: dict, anchor: dict,
              wp_dir: Path, preview_dir: Path, *, required_exports: int = 50) -> dict:
    """Correlate independent reports, never trust status alone or approve a release."""
    errors: list[str] = []
    rows: list[dict] = []
    reports = dict(packet=packet, impact=impact, alias=alias, render=render, anchor=anchor)
    for label, obj in reports.items():
        if not isinstance(obj, dict):
            errors.append('MISSING_OR_MALFORMED_REPORT:' + label)
            continue
        if obj.get('status') != REVIEW_STATUSES[label] or obj.get('errors') or obj.get('publication_approved') is not False or obj.get('qualified_safety_approved') is not False:
            errors.append('FAILED_OR_APPROVED_REPORT:' + label)
        if obj.get('release_state', obj.get('release')) != 'DRAFT_HARD_HOLD':
            errors.append('INVALID_RELEASE_STATE:' + label)
        if obj.get('live_release_allowed') is True or obj.get('merchant_offer_verified') is True:
            errors.append('INAPPROPRIATE_APPROVAL:' + label)
    if errors:
        return _result(errors, rows, {}, required_exports)
    articles = packet.get('articles')
    forks = packet.get('unselected_conflicts')
    if not isinstance(articles, list) or len(articles) != 35 or not isinstance(forks, list) or len(forks) != 9:
        errors.append('ORIGINAL_35_ARTICLE_9_FORK_INVENTORY_MISMATCH')
        articles = articles if isinstance(articles, list) else []
    if impact.get('counts', {}).get('original_articles') != 35 or impact.get('counts', {}).get('source_collision_groups') != 5:
        errors.append('FIVE_COLLISIONS_OR_ARTICLE_IMPACT_DRIFT')
    if alias.get('counts', {}).get('original_articles') != 35 or alias.get('counts', {}).get('unselected_source_collisions') != 5:
        errors.append('SOURCE_ALIAS_IMPACT_DRIFT')
    if render.get('counts', {}).get('original_articles') != 35 or render.get('counts', {}).get('matched_exports') != 35:
        errors.append('RENDER_35_ARTICLE_COVERAGE_MISSING')
    if anchor.get('counts', {}).get('original_articles') != 35 or anchor.get('counts', {}).get('checked_exports') != 35:
        errors.append('ANCHOR_35_ARTICLE_COVERAGE_MISSING')
    by_render = {r.get('slug'): r for r in render.get('articles', []) if isinstance(r, dict)}
    by_anchor = {r.get('slug'): r for r in anchor.get('articles', []) if isinstance(r, dict)}
    if len(by_render) != len(render.get('articles', [])) or len(by_anchor) != len(anchor.get('articles', [])):
        errors.append('DUPLICATE_ARTICLE_REPORT_ROW')
    slugs = set()
    for article in articles:
        if not isinstance(article, dict):
            errors.append('MALFORMED_ORIGINAL_ARTICLE')
            continue
        slug = article.get('slug')
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in slugs:
            errors.append('DUPLICATE_OR_INVALID_ORIGINAL_SLUG')
            continue
        slugs.add(slug)
        variants = article.get('variants', [])
        original = {_candidate(v, 'original') for v in variants}
        if None in original or not original or len(original) != len(variants):
            errors.append('INVALID_ORIGINAL_VARIANTS:' + slug)
            original.discard(None)
        wr = by_render.get(slug, {})
        ar = by_anchor.get(slug, {})
        rendered = {_candidate(v, 'render') for v in wr.get('matching_variant_candidates', [])} if isinstance(wr, dict) else set()
        anchored = {_candidate(v, 'anchor') for v in ar.get('matching_original_candidates', [])} if isinstance(ar, dict) else set()
        if wr.get('errors') or not rendered or not rendered.issubset(original):
            errors.append('RENDER_CANDIDATE_INVALID:' + slug)
        if not anchored or not anchored.issubset(original):
            errors.append('ANCHOR_CANDIDATE_INVALID:' + slug)
        overlap = original & rendered & anchored
        if not overlap:
            errors.append('CROSS_GATE_CANDIDATE_DISJOINT:' + slug)
        rows.append({'slug': slug,
                     'original_variant_count': len(original),
                     'render_candidate_count': len(rendered),
                     'anchor_candidate_count': len(anchored),
                     'matching_review_candidates': [{'branch': b, 'body_sha': s} for b, s in sorted(overlap)],
                     'auto_selected': False, 'qualified_review_required': True})
    if set(by_render) != slugs or set(by_anchor) != slugs:
        errors.append('ARTICLE_REPORT_SLUG_SET_MISMATCH')
    wp, wp_errors = _inventory(Path(wp_dir))
    preview, preview_errors = _inventory(Path(preview_dir))
    errors.extend('WP:' + e for e in wp_errors)
    errors.extend('PREVIEW:' + e for e in preview_errors)
    if wp != preview:
        errors.append('WP_PREVIEW_EXACT_FILE_SET_MISMATCH')
    if len(wp) < required_exports or len(preview) < required_exports:
        errors.append('FIFTY_PRIVATE_EXPORT_PAIRS_NOT_VERIFIED')
    if not slugs.issubset(wp & preview):
        errors.append('MISSING_ORIGINAL_ARTICLE_EXPORTS')
    if render.get('counts', {}).get('nonarticle_exports_needing_independent_review') != len(wp - slugs):
        errors.append('NONARTICLE_EXPORT_ACCOUNTING_DRIFT')
    counts = {'original_articles': len(slugs), 'unselected_manuscript_forks': len(forks),
              'unselected_source_collisions': 5, 'wp_exports': len(wp), 'private_previews': len(preview),
              'candidate_intersection_articles': sum(bool(x['matching_review_candidates']) for x in rows),
              'source_gaps_pending_human_review': impact.get('counts', {}).get('source_gaps', None),
              'source_alias_groups_pending_human_review': alias.get('counts', {}).get('alias_review_groups', None)}
    return _result(errors, rows, counts, required_exports)


def _result(errors, rows, counts, required_exports):
    serialized = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()
    return {'schema': 1, 'status': 'INVALID_HARD_HOLD' if errors else 'INTEGRATED_REVIEW_HARD_HOLD',
            'release_state': 'DRAFT_HARD_HOLD', 'publication_approved': False,
            'qualified_safety_approved': False, 'merchant_offer_verified': False,
            'live_release_allowed': False, 'human_approved': False,
            'automatic_variant_selection': False, 'required_private_export_pairs': required_exports,
            'errors': sorted(set(errors)), 'counts': counts,
            'candidate_intersections': rows, 'review_digest_sha256': hashlib.sha256(serialized).hexdigest(),
            'release_blockers': ['FIVE_SOURCE_EVIDENCE_COLLISIONS_REQUIRE_HUMAN_ADJUDICATION',
                                 'NINE_SHELTER_GIT_OBJECT_FORKS_REQUIRE_HUMAN_ADJUDICATION',
                                 'QUALIFIED_WATER_FOOD_EMERGENCY_PRIVACY_QD_REVIEW_UNGRANTED',
                                 'PURCHASABLE_RIGHTS_CLEARED_PREPAREDNESS_SKU_UNVERIFIED']}



def reconcile_with_all_exports(packet: dict, impact: dict, alias: dict,
                               render: dict, anchor: dict, wp_dir: Path,
                               preview_dir: Path, full: dict) -> dict:
    """R390 is required for the authentic native path, not optional evidence.

    R389's legacy reconcile() remains a synthetic cross-gate API. Never use it
    by itself to claim ALL export custody: supplemental tools/hubs might be
    arbitrary 1-byte placeholders and still reach the old 50-file threshold.
    """
    result = reconcile(packet, impact, alias, render, anchor, wp_dir, preview_dir)
    bad = []
    if not isinstance(full, dict) or full.get('status') != 'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD' or full.get('errors'):
        bad.append('R390_ALL_EXPORT_CUSTODY_NOT_PASSED')
    elif (full.get('release_state') != 'DRAFT_HARD_HOLD' or
          full.get('publication_approved') is not False or
          full.get('qualified_safety_approved') is not False or
          full.get('merchant_offer_verified') is not False or
          full.get('live_release_allowed') is not False):
        bad.append('R390_INAPPROPRIATE_RELEASE_STATE')
    else:
        counts = full.get('counts', {})
        expected = len(result.get('candidate_intersections', []))
        if (counts.get('original_articles') != 35 or
            counts.get('matched_export_pairs') != result.get('counts', {}).get('wp_exports') or
            counts.get('supplemental_exports_needing_independent_review') !=
                result.get('counts', {}).get('wp_exports', 0) - expected):
            bad.append('R390_COUNTS_NOT_RECONCILED')
        extra_slugs = {r.get('slug') for r in full.get('exports', [])
                       if isinstance(r, dict) and r.get('kind') == 'unreviewed_supplemental'}
        original_slugs = {r.get('slug') for r in result.get('candidate_intersections', [])}
        if (len(full.get('exports', [])) != counts.get('matched_export_pairs') or
            {r.get('slug') for r in full.get('exports', []) if isinstance(r, dict)} !=
                original_slugs | extra_slugs or extra_slugs & original_slugs):
            bad.append('R390_EXPORT_IDENTITIES_NOT_RECONCILED')
        disk_names, disk_errors = _inventory(Path(wp_dir))
        if disk_errors or {r.get('slug') for r in full.get('exports', [])} != disk_names:
            bad.append('R390_EXPORT_IDENTITIES_NOT_RECONCILED')
        if any(r.get('errors') or r.get('qualified_review_required') is not True or
               r.get('release_allowed') is not False or r.get('merchant_verified') is not False
               for r in full.get('exports', [])):
            bad.append('R390_UNVERIFIED_OUTPUT_OR_APPROVAL')
        if not isinstance(full.get('evidence_sha256'), str) or not re.fullmatch(r'[a-f0-9]{64}', full['evidence_sha256']):
            bad.append('R390_EVIDENCE_DIGEST_MISSING')
    result['all_export_custody'] = {'status': full.get('status') if isinstance(full, dict) else 'MISSING',
                                   'evidence_sha256': full.get('evidence_sha256') if isinstance(full, dict) else None,
                                   'supplemental_outputs_remain_unreviewed': True}
    if bad:
        result['status'] = 'INVALID_HARD_HOLD'
        result['errors'] = sorted(set(result.get('errors', []) + bad))
    result['release_blockers'] = sorted(set(result['release_blockers'] +
                                        ['SUPPLEMENTAL_EXPORTS_REQUIRE_INDEPENDENT_REVIEW']))
    return result


def native(repo: Path, wp: Path, preview: Path) -> dict:
    """Read pinned Git blob objects and run each independent validator afresh."""
    def read(sha):
        if not isinstance(sha, str) or not SHA.fullmatch(sha):
            raise ValueError('MALFORMED_SHA')
        data = subprocess.run(['git', '-C', str(repo), 'cat-file', 'blob', sha],
                              check=True, capture_output=True, timeout=20).stdout
        if blob_sha(data) != sha:
            raise ValueError('GIT_BLOB_HASH_MISMATCH')
        return data
    docs = [json.loads(read(sha)) for sha in ORIGINAL_PINS]
    r384 = load_dependency('r384_variant_review_packet')
    r385 = load_dependency('r385_source_claim_blast_radius')
    r386 = load_dependency('r386_rendered_citation_parity')
    r387 = load_dependency('r387_claim_anchor_custody')
    r388 = load_dependency('r388_source_url_alias_custody')
    packet = r384.build_packet(docs[0], read)
    impact = r385.build_original_docket(*docs, read)
    alias = r388.build_alias_docket(docs[1], docs[2], impact)
    urls = {'BASE': {}}
    for row in docs[2]['sources']:
        sid, url = row['id'], row['url']
        if sid in urls['BASE']:
            raise ValueError('DUPLICATED_BASE_SOURCE')
        urls['BASE'][sid] = url
    for group in docs[1]['source_id_variants']:
        for v in group['variants']:
            origin = urls.setdefault(v['branch'], {})
            if v['id'] in origin:
                raise ValueError('DUPLICATED_BRANCH_SOURCE')
            origin[v['id']] = v['url']
    render = r386.audit(packet, wp, preview, source_urls=urls)
    anchor = r387.audit_original_candidates(packet, wp, read)
    r390 = load_dependency('r390_all_export_custody')
    full = r390.audit(wp, preview, [article['slug'] for article in packet['articles']])
    result = reconcile_with_all_exports(packet, impact, alias, render, anchor, wp, preview, full)
    result['original_manifest_blob_ids'] = list(ORIGINAL_PINS)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--wp', type=Path, default=Path('preparedness/build/wp'))
    parser.add_argument('--preview', type=Path, default=Path('preparedness/build/preview'))
    args = parser.parse_args(argv)
    try:
        result = native(args.repo, args.wp, args.preview)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, ImportError,
            subprocess.SubprocessError, json.JSONDecodeError) as exc:
        result = _result(['AUTHENTIC_NATIVE_CUSTODY_UNAVAILABLE:' + type(exc).__name__], [], {}, 50)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2  # Evidence-only review gate; NEVER a publishing or QD authorization.


if __name__ == '__main__':
    raise SystemExit(main())
