#!/usr/bin/env python3
"""R405 read-only, cryptographically pinned E395/E397/E398 HTML/citation custody.

An integrity PASS only means that local bytes agree with a named receipt and that
basic static markup/source-preservation checks did not flag a structural problem.
It NEVER means content, science, emergency advice or publication is approved.
No network, file mutation, WordPress publishing or source selection is performed.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
from io import BytesIO
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit
from zipfile import ZipFile, BadZipFile

HOLD = 'DRAFT_HARD_HOLD'
ARTICLE = 'safe-jerky-dehydration'
PINS = {
    'E395_ZIP': '21a2142c6050eb3bae020c67744ee82439d854525ba63915ea9092a0b7bba46b',
    'E395_HTML': 'bc0537e611d35b195e10ee49ceb9772a904b7c8fea0749a6203da38e835f8184',
    'E397_HTML': 'edd96e850ada775e7394b08d0c59f79415efb2d08f2d088685265e5881e0d50c',
    'E398_HTML': 'be180cb0443ebf2dc16c0cd2c5e638a1dc3e49f1f282f03be4f946244d5e4643',
}
SOURCE_URLS = frozenset({
    'https://nchfp.uga.edu/how/dry/recipes/jerky/',
    'https://ask.fsis.usda.gov/article/Is-jerky-safe-when-stored-at-room-temperature',
    'https://extension.umn.edu/food/preparing/cooking-at-home/food-preservation/drying',
    'https://extension.umn.edu/natural-resources/weather-and-climate/prepare-for-risks/cooking-without-a-kitchen',
})
MAX_HTML_BYTES = 4 * 1024 * 1024
FORBIDDEN_TAGS = frozenset('script iframe frame frameset object embed form input textarea button select video audio canvas applet base svg math link'.split())
URL_ATTRIBUTES = frozenset({'href', 'src', 'srcset', 'poster', 'action', 'formaction', 'xlink:href', 'background', 'ping', 'data', 'cite', 'longdesc', 'manifest'})
CSS_REQUEST = re.compile(r'(?i)@import\b|url\s*\(')


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class CitationScanner(HTMLParser):
    """Records links and passive-HTML hazards; does NOT endorse article claims."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.failures: set[str] = set()
        self.urls: set[str] = set()
        self.ids: set[str] = set()
        self.fragments: set[str] = set()
        self.style_depth = 0

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        keys = [name.lower() for name, _ in attrs]
        if len(set(keys)) != len(keys):
            self.failures.add('duplicate_html_attribute')
        if tag in FORBIDDEN_TAGS:
            self.failures.add('active_or_unreviewed_element')
        if tag == 'style':
            self.style_depth += 1
        attributes = dict(attrs)
        ident = attributes.get('id')
        if ident is not None:
            if not ident or ident in self.ids:
                self.failures.add('duplicate_or_empty_html_id')
            self.ids.add(ident)
        for name, value in attrs:
            name = name.lower()
            value = value or ''
            if name.startswith('on') or name in ('srcdoc', 'contenteditable'):
                self.failures.add('active_html_attribute')
            if name == 'style' and CSS_REQUEST.search(value):
                self.failures.add('css_external_resource')
            if name in URL_ATTRIBUTES:
                href = value.strip()
                if href.startswith('#') and name == 'href':
                    self.fragments.add(href[1:])
                elif href.startswith('/') and not href.startswith('//') and name == 'href':
                    pass  # same-site relative navigation; never counted as a citation
                elif href.startswith('https://') and name == 'href':
                    u = urlsplit(href)
                    if not u.hostname or u.username or u.password or '\\' in href:
                        self.failures.add('unsafe_link_destination')
                    else:
                        self.urls.add(href.split('#', 1)[0])
                else:
                    self.failures.add('unsafe_link_or_resource')
        if tag == 'meta' and (attributes.get('http-equiv') or '').lower() == 'refresh':
            self.failures.add('active_or_unreviewed_element')

    def handle_endtag(self, tag):
        if tag.lower() == 'style' and self.style_depth:
            self.style_depth -= 1

    def handle_data(self, data):
        if self.style_depth and CSS_REQUEST.search(data):
            self.failures.add('css_external_resource')

    def finish(self):
        if self.style_depth:
            self.failures.add('unclosed_css_style')
        if any(frag and frag not in self.ids for frag in self.fragments):
            self.failures.add('unresolved_internal_anchor')
        return self


def scan_html(raw: object, receipt: str) -> dict:
    failures: set[str] = set()
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_HTML_BYTES:
        return {'integrity': 'FAIL', 'sha256_matched': False, 'citations': [],
                'source_scope_missing': sorted(SOURCE_URLS), 'failures': ['missing_or_oversized_html']}
    matched = sha256(raw) == receipt
    if not matched:
        failures.add('html_receipt_mismatch')
    try:
        html = raw.decode('utf-8', 'strict')
        scanner = CitationScanner()
        scanner.feed(html)
        scanner.close()
        scanner.finish()
        failures.update(scanner.failures)
        links = scanner.urls
    except (UnicodeDecodeError, ValueError, AssertionError):
        failures.add('invalid_html_input')
        links = set()
    # Scope-preservation is a review flag, never an automatic scientific judgment.
    missing = SOURCE_URLS - links
    if missing:
        failures.add('four_source_links_unproven')
    return {'integrity': 'FAIL' if failures else 'PASS', 'sha256_matched': matched,
            'citations': sorted(links), 'source_scope_missing': sorted(missing),
            'failures': sorted(failures)}


def inspect(html_variants: dict[str, bytes | None], *, receipts: dict[str, str] | None = None) -> dict:
    """Pure static lineage check; overrides only for controlled synthetic tests."""
    pins = PINS if receipts is None else receipts
    if not isinstance(html_variants, dict) or set(html_variants) != {'E395', 'E397', 'E398'}:
        return {'schema': 'r405.article11.lineage.v1', 'integrity': 'FAIL',
                'release': HOLD, 'eligible': False, 'failures': ['variant_inventory_mismatch']}
    if set(pins) != set(PINS) or any(not isinstance(v, str) or not re.fullmatch('[0-9a-f]{64}', v) for v in pins.values()):
        return {'schema': 'r405.article11.lineage.v1', 'integrity': 'FAIL',
                'release': HOLD, 'eligible': False, 'failures': ['receipt_inventory_invalid']}
    scans = {k: scan_html(html_variants[k], pins[k + '_HTML']) for k in ('E395', 'E397', 'E398')}
    differences = {}
    for before, after in (('E395', 'E397'), ('E397', 'E398')):
        older, newer = set(scans[before]['citations']), set(scans[after]['citations'])
        differences[before + '_to_' + after] = {'added': sorted(newer - older),
                                               'removed': sorted(older - newer)}
    problems = [k + ':' + issue for k, s in scans.items() for issue in s['failures']]
    # A derivative removing even a non-core citation requires qualified manual review.
    if any(v['removed'] for v in differences.values()):
        problems.append('derivative_removed_citation_requires_review')
    return {'schema': 'r405.article11.lineage.v1', 'article_slug': ARTICLE,
            'integrity': 'FAIL' if problems else 'PASS', 'release': HOLD,
            'eligible': False, 'scientific_safety_approved': False,
            'human_source_review': 'NOT_GRANTED', 'source_pages_directly_authenticated': False,
            'publication_approved': False, 'variant_selected': None,
            'variants': scans, 'citation_changes': differences, 'failures': sorted(set(problems))}



def inspect_original_zip(zip_bytes: object, original_html: object, *, receipts: dict | None = None) -> dict:
    """Run the prior audited R404 ZIP gate and bind its member to stand-alone E395 HTML.

    No reviewer-supplied new ZIP may substitute for immutable original E395 bytes.
    Hash overrides are intended only for synthetic regression tests.
    """
    pins = PINS if receipts is None else receipts
    if not isinstance(zip_bytes, bytes) or not isinstance(original_html, bytes):
        return {'integrity': 'FAIL', 'failures': ['missing_original_zip_or_html']}
    try:
        checker = Path(__file__).with_name('r402_external_editorial_custody.py')
        spec = importlib.util.spec_from_file_location('r404_prior_audited_gate', checker)
        if spec is None or spec.loader is None:
            raise ValueError('missing_prior_custody_checker')
        prior = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prior)
        report = prior.inspect(zip_bytes, expected_zip_sha=pins['E395_ZIP'],
                               expected_article_sha=pins['E395_HTML'])
        failures = ['r404:' + f for f in report['failures']]
        if report['archive_integrity'] != 'PASS':
            return {'integrity': 'FAIL', 'failures': sorted(set(failures)),
                    'zip_sha256_matched': report['archive_sha256_matched']}
        with ZipFile(BytesIO(zip_bytes), 'r') as zf:
            members = [i for i in zf.infolist() if i.filename.split('/')[-1] == prior.ARTICLE_MEMBER]
            if len(members) != 1:
                failures.append('article_zip_member_identity')
            elif zf.read(members[0]) != original_html:
                failures.append('standalone_article_differs_from_original_zip')
    except (OSError, ValueError, KeyError, BadZipFile, RuntimeError, OverflowError, EOFError):
        failures = ['unreadable_or_inconsistent_original_zip']
    return {'integrity': 'FAIL' if failures else 'PASS',
            'zip_sha256_matched': sha256(zip_bytes) == pins.get('E395_ZIP'),
            'failures': sorted(set(failures))}


def inspect_bundle(zip_bytes: object, html_variants: dict, *, receipts: dict | None = None) -> dict:
    """Composite receiver-side custody: prior ZIP receipt plus all three HTML receipts."""
    lineage = inspect(html_variants, receipts=receipts)
    original = html_variants.get('E395') if isinstance(html_variants, dict) else None
    custody = inspect_original_zip(zip_bytes, original, receipts=receipts)
    errors = list(lineage.get('failures', [])) + ['zip:' + s for s in custody['failures']]
    return {'schema': 'r405.article11.bundle.v1',
            'integrity': 'FAIL' if errors else 'PASS', 'eligible': False,
            'release': HOLD, 'source_safety_approved': False,
            'publication_approved': False, 'all_variants_unselected': True,
            'original_zip': custody, 'lineage': lineage, 'failures': sorted(set(errors))}

def read_html(path: Path | None) -> bytes | None:
    if path is None:
        return None
    # Follow the R403 no-follow hardlink rejection boundary for HTML receipts.
    import os
    import stat
    if not hasattr(os, 'O_NOFOLLOW'):
        raise ValueError('no_nofollow_support')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or not 0 < info.st_size <= MAX_HTML_BYTES:
            raise ValueError('unsafe_html_original')
        with os.fdopen(fd, 'rb') as fh:
            fd = -1
            data = fh.read(MAX_HTML_BYTES + 1)
            if len(data) != info.st_size or fh.read(1):
                raise ValueError('changed_html_original')
            return data
    finally:
        if fd >= 0:
            os.close(fd)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--e395-zip', type=Path)
    p.add_argument('--e395-html', type=Path)
    p.add_argument('--e397-html', type=Path)
    p.add_argument('--e398-html', type=Path)
    v = p.parse_args(argv)
    try:
        files = {'E395': read_html(v.e395_html), 'E397': read_html(v.e397_html),
                 'E398': read_html(v.e398_html)}
        # Imported from the exact adjacent R404 custody tool, no disk extraction.
        if v.e395_zip is None:
            archive = None
        else:
            checker = Path(__file__).with_name('r402_external_editorial_custody.py')
            spec = importlib.util.spec_from_file_location('r404_read_only_zip', checker)
            prior = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(prior)
            archive = prior.read_bounded_original(v.e395_zip)
        result = inspect_bundle(archive, files)
    except (OSError, ValueError):
        result = {'schema': 'r405.article11.lineage.v1', 'integrity': 'FAIL',
                  'release': HOLD, 'eligible': False, 'failures': ['unreadable_original_editorial_html']}
    print(json.dumps(result, sort_keys=True))
    return 2  # No HTML review or digest matching can approve publication.


if __name__ == '__main__':
    raise SystemExit(main())
