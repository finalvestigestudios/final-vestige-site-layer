#!/usr/bin/env python3
"""R74: verify source custody in the *rendered PDF* of real, disposable WordPress.

This is intentionally stricter than a DOM print-media selector check. Chromium
can omit the contents of closed <details> from PDF even when CSS/DOM tests say
those contents are visible. Never infer image-use clearance from NASA metadata.
"""
from __future__ import annotations

import hashlib
import io
import re
import unicodedata
from pathlib import Path
from pypdf import PdfReader

NASA_CATALOGS = (
    'S67-19766', 'S67-15717', 'S66-58038',
    'KSC-20170124-PH_KLS01_0164', 'S67-21294',
    'KSC-20170124-PH_KLS01_0090',
)
NASA_LINKS = (
    'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
    'https://www.nasa.gov/image-detail/amf-s67-15717/',
    'https://www.nasa.gov/image-detail/amf-s66-58038/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
    'https://www.nasa.gov/image-detail/amf-s67-21294/',
    'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
)


def verify_rendered_pdf_bytes(raw: bytes) -> dict:
    """Return redacted counts/digest only; never upload whole extracted CMS text."""
    if len(raw) < 1000 or not raw.startswith(b'%PDF-'):
        raise AssertionError('R74_NOT_A_REAL_PDF')
    reader = PdfReader(io.BytesIO(raw), strict=True)
    if not 1 <= len(reader.pages) <= 80:
        raise AssertionError('R74_UNEXPECTED_PRINT_PAGES')
    extracted = ' '.join(page.extract_text() or '' for page in reader.pages)
    printable = unicodedata.normalize('NFKC', extracted)
    # Chrome may line-wrap URLs and catalog identifiers midword in PDF text.
    # Compare whitespace-insensitive tokens for *known, pinned* NASA identifiers.
    compact = re.sub(r'\s+', '', printable).lower()
    for catalog in NASA_CATALOGS:
        if catalog.lower() not in compact:
            raise AssertionError('R74_PRINT_PDF_CATALOG_MISSING')
    for link in NASA_LINKS:
        if link.lower() not in compact:
            raise AssertionError('R74_PRINT_PDF_NASA_URL_MISSING')
    normalized = re.sub(r'\s+', ' ', printable)
    checks = {
        'individual_rights_notices': len(re.findall(r'Individual review required', normalized, re.I)),
        'catalog_custody_labels': len(re.findall(r'Catalog verification on NASA page', normalized, re.I)),
        'source_custody_headings': len(re.findall(r'Source custody and reuse status', normalized, re.I)),
        'revision_labels': len(re.findall(r'NASA page last updated', normalized, re.I)),
    }
    # The guide repeats two phrases, so require >=6 source-specific occurrences.
    if any(value < 6 for value in checks.values()):
        raise AssertionError('R74_PRINT_PDF_CLOSED_CUSTODY_MISSING')
    if re.search(r'commercial (?:reuse|use) (?:is )?(?:unconditionally )?approved', normalized, re.I):
        raise AssertionError('R74_PRINT_PDF_FALSE_RIGHTS_ASSURANCE')
    return {'schema': 'fv.apollo.r74.authentic-wordpress-pdf.v1',
            'release': 'STAGING_HOLD', 'actual_wordpress_source_required': True,
            'print_pdf_sha256': hashlib.sha256(raw).hexdigest(),
            'page_count': len(reader.pages), 'catalog_ids': 6, 'nasa_urls': 6,
            **checks, 'image_rights_cleared': 0,
            'hosted_cwv_certified': False, 'no_production_cms_write': True}


def verify_wordpress_print_page(page, destination: Path) -> dict:
    """Call only inside the genuine 1440px, JS-disabled local WordPress case."""
    if page.evaluate('window.top !== window.self || window.innerWidth !== 1440'):
        raise AssertionError('R74_NOT_TOP_LEVEL_WORDPRESS_PRINT')
    if page.locator('.fv-ex2-apollo-suite').count() != 1:
        raise AssertionError('R74_NOT_AUTHENTIC_APOLLO_PAGE')
    pdf = page.pdf(format='A4', print_background=True)
    receipt = verify_rendered_pdf_bytes(pdf)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # The PDF holds source-linked archival metadata only; no private WP URL,
    # credentials, cookies, user state, NASA image binaries or page HTML.
    destination.write_bytes(pdf)
    return receipt
