#!/usr/bin/env python3
"""R76: inspect the ORIGINAL native Chromium PDF, not R75's normalized copy.

Only for the isolated WordPress/Assembler Apollo fixture. Do not use this
local-browser result as hosted WordPress parity, rights clearance or CWV proof.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import fitz
from wp_pdf_custody_r74 import verify_rendered_pdf_bytes
from wp_pdf_pagination_r75 import visual_page_classification


def inspect_native_pdf(raw: bytes, last_page_png: Path | None = None) -> dict:
    custody = verify_rendered_pdf_bytes(raw)
    with fitz.open(stream=raw, filetype='pdf') as doc:
        if not len(doc):
            raise AssertionError('R76_NATIVE_EMPTY')
        terminal = visual_page_classification(doc[-1])
        if terminal['decorative_only']:
            raise AssertionError('R76_NATIVE_TRAILING_DECORATIVE_PAGE')
        interior = [i+1 for i in range(len(doc)-1)
                    if visual_page_classification(doc[i])['decorative_only']]
        if interior:
            raise AssertionError('R76_NATIVE_INTERIOR_DECORATIVE_PAGE')
        if last_page_png is not None:
            last_page_png.parent.mkdir(parents=True, exist_ok=True)
            doc[-1].get_pixmap(matrix=fitz.Matrix(.9,.9), alpha=False).save(str(last_page_png))
    return {
        'schema': 'fv.apollo.r76.native-wordpress-print.v1',
        'release': 'STAGING_HOLD',
        'source': 'UNMODIFIED_CHROMIUM_WORDPRESS_PDF',
        'native_pdf_sha256': hashlib.sha256(raw).hexdigest(),
        'native_pages': custody['page_count'],
        'terminal_decorative_only': False,
        'interior_decorative_count': 0,
        'nasa_catalog_ids': custody['catalog_ids'],
        'nasa_source_urls': custody['nasa_urls'],
        'individual_rights_cleared': 0,
        'hosted_wordpress_tested': False,
        'manual_assistive_technology_tested': False,
        'production_writes': False,
    }


def verify_native_apollo_print(page, raw: bytes, last_page_png: Path) -> dict:
    if not page.evaluate("window.top === window.self && matchMedia('print').matches"):
        raise AssertionError('R76_NOT_NATIVE_PRINT_CONTEXT')
    if page.locator('.fv-ex2-apollo-suite').count() != 1:
        raise AssertionError('R76_RESEARCH_SUITE_MISSING')
    # Only the outer Gutenberg *theme* footer is omitted on this research-print
    # page. The suite's two source-bearing footers must remain printed.
    if page.locator('footer.wp-block-template-part').count() != 1:
        raise AssertionError('R76_ASSEMBLER_FOOTER_SELECTOR_CHANGED')
    if not page.locator('footer.wp-block-template-part').evaluate(
            'e => getComputedStyle(e).display === "none"'):
        raise AssertionError('R76_PRINT_FOOTER_IS_NOT_EXCLUDED')
    if page.locator('.fva-footer').count() != 1 or page.locator('.fv-ex2-ledger__footer').count() != 1:
        raise AssertionError('R76_SOURCE_FOOTERS_MISSING')
    return {**inspect_native_pdf(raw, last_page_png),
            'gutenberg_template_footer_print_excluded': True,
            'source_footers_preserved_in_dom': True}
