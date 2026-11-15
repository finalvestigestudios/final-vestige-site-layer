"""R390: read-only checksum and safety custody for EVERY Preparedness export.

Addresses the R389 false-positive path where the 35 original articles match
but arbitrary supplemental hub/tool pages can be added to reach 50 exports.
This is a deterministic PRIVATE REVIEW docket, never a release or QD gate.
No network, CMS, merchant, analytics, or filesystem writes.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SHA = re.compile(r"[a-f0-9]{64}\Z")
SIZE_LIMIT = 3_000_000
REQUIRED = 50
CONTENT_CLASSES = frozenset({'pa-article', 'pa-tool', 'pa-page', 'pa-hub', 'pa-landing'})
VOID = frozenset({'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'})
ACTIVE = frozenset({'script', 'iframe', 'object', 'embed', 'form', 'button',
                    'input', 'textarea', 'select', 'video', 'audio'})
OFFSITE_MERCHANT = re.compile(r"(?:payhip\.com|gumroad\.com|checkout\.|stripe\.com|paypal\.com)", re.I)


def sha(raw: bytes) -> str:
    return sha256(raw).hexdigest()


class Surface(HTMLParser):
    """Inspect actual DOM tokens; track exact bounded article/tool subtree."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.issues: list[str] = []
        self.stack: list[str] = []
        self.root_count = 0
        self.root_depth: int | None = None
        self.content: list[str] = []
        self.content_slug: str | None = None
        self.robots = False
        self.canonicals: list[str] = []
        self.sources: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        text = self.get_starttag_text()
        classes = set((a.get('class') or '').split())
        if tag in ACTIVE:
            self.issues.append('ACTIVE_CONTENT:' + tag)
        for key, value in attrs:
            value = value or ''
            if key.lower().startswith('on') and len(key) > 2:
                self.issues.append('INLINE_EVENT_HANDLER')
            if key.lower() in {'href', 'src', 'action', 'formaction', 'xlink:href'}:
                v = value.strip().lower()
                if v.startswith(('javascript:', 'data:', 'vbscript:', '//')):
                    self.issues.append('UNSAFE_LINK_SCHEME')
                if key.lower() in {'href', 'action', 'formaction'} and OFFSITE_MERCHANT.search(value):
                    self.issues.append('UNVERIFIED_COMMERCE_DESTINATION')
        if tag == 'a' and a.get('href') is not None:
            self.links.append(a['href'])
        if tag == 'meta' and (a.get('name') or '').strip().lower() == 'robots':
            vals = {x.strip().lower() for x in (a.get('content') or '').split(',')}
            if {'noindex', 'nofollow'} <= vals:
                self.robots = True
        if tag == 'link' and 'canonical' in (a.get('rel') or '').lower().split():
            self.canonicals.append(a.get('href') or '')
        is_void = tag in VOID
        if self.root_depth is None and tag in {'div', 'section', 'article', 'main'} and classes & CONTENT_CLASSES:
            self.root_count += 1
            self.root_depth = len(self.stack)
            self.content_slug = a.get('data-slug')
        elif self.root_depth is not None and tag in {'div', 'section', 'article', 'main'} and classes & CONTENT_CLASSES:
            # Nested content roots are not a second top-level export.
            pass
        if self.root_depth is not None:
            self.content.append(text)
        if not is_void:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack:
            self.issues.append('ORPHAN_CLOSE')
            return
        if self.stack[-1] != tag:
            self.issues.append('MALFORMED_NESTING')
            if tag not in self.stack:
                return
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
        if self.root_depth is not None:
            self.content.append(f'</{tag}>')
        self.stack.pop()
        if self.root_depth is not None and len(self.stack) == self.root_depth:
            self.root_depth = None

    def handle_data(self, value):
        if self.root_depth is not None:
            self.content.append(value)

    def handle_entityref(self, name):
        if self.root_depth is not None:
            self.content.append('&' + name + ';')

    def handle_charref(self, name):
        if self.root_depth is not None:
            self.content.append('&#' + name + ';')

    def handle_comment(self, value):
        if self.root_depth is not None:
            self.content.append('<!--' + value + '-->')

    def finish(self):
        self.close()
        if self.root_depth is not None:
            self.issues.append('UNCLOSED_CONTENT_ROOT')
        if self.root_count != 1:
            self.issues.append('CONTENT_ROOT_COUNT:' + str(self.root_count))
        return sorted(set(self.issues))


def scan(directory: Path) -> tuple[dict[str, bytes], list[str]]:
    errors: list[str] = []
    if directory.is_symlink() or not directory.is_dir():
        return {}, ['INVALID_EXPORT_DIRECTORY']
    result: dict[str, bytes] = {}
    try:
        for entry in sorted(directory.iterdir(), key=lambda p: p.name):
            if entry.is_symlink() or not entry.is_file():
                errors.append('UNSAFE_EXPORT_ENTRY:' + entry.name)
                continue
            if entry.suffix != '.html' or not SLUG.fullmatch(entry.stem):
                errors.append('UNEXPECTED_EXPORT_FILENAME:' + entry.name)
                continue
            # Do not follow embedded directories or symlinks and never read oversized blobs.
            if not 0 < entry.stat().st_size <= SIZE_LIMIT:
                errors.append('EXPORT_SIZE_INVALID:' + entry.name)
                continue
            result[entry.stem] = entry.read_bytes()
    except OSError:
        errors.append('EXPORT_READ_FAILURE')
    return result, sorted(set(errors))


def check_pair(slug: str, wp_raw: bytes, preview_raw: bytes, is_article: bool) -> dict:
    issues: list[str] = []
    wp, preview = Surface(), Surface()
    try:
        wtext, ptext = wp_raw.decode('utf-8'), preview_raw.decode('utf-8')
        wp.feed(wtext); preview.feed(ptext)
        issues.extend('WP:' + x for x in wp.finish())
        issues.extend('PREVIEW:' + x for x in preview.finish())
        if not wtext.lstrip().startswith('<!-- wp:html -->'):
            issues.append('WORDPRESS_DRAFT_WRAPPER_MISSING')
        if not ptext.lstrip().lower().startswith('<!doctype html>'):
            issues.append('PREVIEW_DOCTYPE_MISSING')
        if not preview.robots:
            issues.append('PREVIEW_NOINDEX_NOFOLLOW_MISSING')
        if not is_article:
            if wp.content_slug != slug or preview.content_slug != slug:
                issues.append('SUPPLEMENTAL_SLUG_PROVENANCE_UNVERIFIED')
            if ''.join(wp.content) != ''.join(preview.content):
                issues.append('SUPPLEMENTAL_WORDPRESS_PREVIEW_CONTENT_DRIFT')
            if not all(token in ''.join(wp.content).lower() for token in ('draft', 'review')):
                issues.append('SUPPLEMENTAL_REVIEW_WARNING_MISSING')
            if not all(token in ''.join(preview.content).lower() for token in ('draft', 'review')):
                issues.append('SUPPLEMENTAL_PREVIEW_REVIEW_WARNING_MISSING')
        if len(wp.canonicals) > 1 or len(preview.canonicals) > 1:
            issues.append('DUPLICATE_CANONICAL_DECLARATION')
        if wp.canonicals and preview.canonicals and wp.canonicals != preview.canonicals:
            issues.append('CROSS_EXPORT_CANONICAL_DRIFT')
    except (UnicodeError, ValueError) as exc:
        issues.append('MALFORMED_EXPORT:' + type(exc).__name__)
    return {'slug': slug, 'kind': 'original_article' if is_article else 'unreviewed_supplemental',
            'wp_bytes': len(wp_raw), 'preview_bytes': len(preview_raw),
            'wp_sha256': sha(wp_raw), 'preview_sha256': sha(preview_raw),
            'subtree_sha256': sha(''.join(wp.content).encode('utf-8')) if wp.root_count == 1 else None,
            'canonical_urls': sorted(set(wp.canonicals + preview.canonicals)),
            'errors': sorted(set(issues)), 'qualified_review_required': True,
            'merchant_verified': False, 'release_allowed': False}


def audit(wp_dir: Path, preview_dir: Path, original_slugs, *, min_pairs: int = REQUIRED) -> dict:
    errors: list[str] = []
    rows: list[dict] = []
    slugs = list(original_slugs) if isinstance(original_slugs, (list, set, tuple)) else []
    if len(slugs) != 35 or len(set(slugs)) != 35 or any(not isinstance(x, str) or not SLUG.fullmatch(x) for x in slugs):
        errors.append('ORIGINAL_35_SLUG_SET_INVALID')
    wp, we = scan(Path(wp_dir))
    pv, pe = scan(Path(preview_dir))
    errors += ['WP:' + e for e in we] + ['PREVIEW:' + e for e in pe]
    if set(wp) != set(pv):
        errors.append('EXACT_EXPORT_FILENAME_SET_MISMATCH')
    if len(wp) < min_pairs or len(pv) < min_pairs:
        errors.append('INSUFFICIENT_PRIVATE_EXPORT_PAIRS')
    if not set(slugs).issubset(set(wp) & set(pv)):
        errors.append('ORIGINAL_ARTICLE_OUTPUT_MISSING')
    all_canonicals: dict[str, str] = {}
    for slug in sorted(set(wp) & set(pv)):
        row = check_pair(slug, wp[slug], pv[slug], slug in slugs)
        rows.append(row)
        errors += [slug + ':' + x for x in row['errors']]
        for url in row['canonical_urls']:
            if url in all_canonicals and all_canonicals[url] != slug:
                errors.append('DUPLICATE_CANONICAL_URL:' + slug + ':' + all_canonicals[url])
            all_canonicals[url] = slug
    evidence = {'schema': 1, 'source': 'R390_ALL_EXPORT_CUSTODY',
                'rows': rows, 'errors': sorted(set(errors))}
    return {'schema': 1, 'status': 'INVALID_HARD_HOLD' if errors else 'ALL_EXPORT_BYTES_REVIEW_HARD_HOLD',
            'release_state': 'DRAFT_HARD_HOLD', 'publication_approved': False,
            'qualified_safety_approved': False, 'merchant_offer_verified': False,
            'live_release_allowed': False, 'automatic_variant_selection': False,
            'errors': sorted(set(errors)), 'counts': {'original_articles': len(slugs),
            'matched_export_pairs': len(rows), 'supplemental_exports_needing_independent_review':
            sum(r['kind'] == 'unreviewed_supplemental' for r in rows)},
            'exports': rows, 'evidence_sha256': sha(json.dumps(evidence, sort_keys=True, separators=(',', ':')).encode()),
            'release_blockers': ['EVERY_NONARTICLE_EXPORT_NEEDS_INDEPENDENT_REVIEW',
                                 'FIVE_SOURCE_COLLISIONS_UNADJUDICATED', 'NINE_SHELTER_FORKS_UNSELECTED',
                                 'QUALIFIED_WATER_FOOD_EMERGENCY_PRIVACY_QD_CLEARANCE_NOT_GRANTED',
                                 'PAID_PREPAREDNESS_SKU_NOT_VERIFIED']}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wp', type=Path, default=Path('preparedness/build/wp'))
    parser.add_argument('--preview', type=Path, default=Path('preparedness/build/preview'))
    parser.add_argument('--original-slug-file', type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        # Not a release path. CLI won't accept invented slugs as original custody.
        if args.original_slug_file is None:
            raise ValueError('AUTHENTIC_ORIGINAL_CUSTODY_REQUIRED')
        slugs = json.loads(args.original_slug_file.read_text())
        result = audit(args.wp, args.preview, slugs)
        result['status'] = 'INVALID_HARD_HOLD'  # supplied JSON never authenticates the source manifest
        result['errors'] = sorted(set(result['errors'] + ['CLI_ORIGINAL_GIT_BLOB_UNAUTHENTICATED']))
    except (OSError, ValueError, UnicodeError, TypeError, json.JSONDecodeError) as exc:
        result = {'status': 'INVALID_HARD_HOLD', 'release_state': 'DRAFT_HARD_HOLD',
                  'publication_approved': False, 'qualified_safety_approved': False,
                  'errors': ['AUTHENTIC_INPUTS_UNAVAILABLE:' + type(exc).__name__]}
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
