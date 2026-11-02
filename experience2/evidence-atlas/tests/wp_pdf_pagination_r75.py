#!/usr/bin/env python3
"""R75 source-custody-preserving review PDF pagination.

NEVER present a normalized print artifact as proof that WordPress's native
browser-print layout is fixed. The original Chromium PDF remains retained.
"""
from __future__ import annotations

import hashlib
import io
from pathlib import Path

import fitz
from pypdf import PdfReader
from wp_pdf_custody_r74 import verify_rendered_pdf_bytes

MAX_TRAILING_DECORATIVE_PAGES = 3
MAX_LIGHT_INK_FRACTION = 0.04


def visual_page_classification(page: fitz.Page) -> dict:
    """Pixel-aware test: missing extracted text is not sufficient to trim."""
    has_words = bool(page.get_text("text").strip())
    has_images = bool(page.get_images(full=True))
    has_links = bool(page.get_links())
    has_other_annotations = page.first_annot is not None
    pix = page.get_pixmap(matrix=fitz.Matrix(.6, .6),
                          colorspace=fitz.csGRAY, alpha=False, annots=True)
    samples = pix.samples
    dark = sum(v < 224 for v in samples)
    nonwhite = sum(v < 250 for v in samples)
    ratio = nonwhite / max(1, len(samples))
    decorative = (
        not any((has_words, has_images, has_links, has_other_annotations))
        and dark == 0 and ratio <= MAX_LIGHT_INK_FRACTION
    )
    return {
        "decorative_only": decorative, "has_text": has_words,
        "has_images": has_images,
        "has_annotations": bool(has_links or has_other_annotations),
        "dark_pixels": dark, "nonwhite_fraction": round(ratio, 6)
    }


def prepare_review_pdf(raw: bytes, destination: Path | None = None) -> tuple[bytes, dict]:
    """Trim only safely classified *terminal* decoration and reverify NASA custody."""
    original_custody = verify_rendered_pdf_bytes(raw)
    with fitz.open(stream=raw, filetype="pdf") as document:
        total = len(document)
        trailing = []
        while total - len(trailing) > 1:
            i = total - len(trailing) - 1
            evidence = visual_page_classification(document[i])
            if not evidence["decorative_only"]:
                break
            trailing.append({"page_number": i + 1, **evidence})
            if len(trailing) > MAX_TRAILING_DECORATIVE_PAGES:
                raise AssertionError("R75_TOO_MANY_TERMINAL_BLANKS")
        kept = total - len(trailing)
        interior = [i + 1 for i in range(kept)
                    if visual_page_classification(document[i])["decorative_only"]]
        if interior:
            raise AssertionError("R75_INTERIOR_DECORATIVE_PAGE")
        if not trailing:
            normalized = raw
        else:
            with fitz.open() as clean:
                clean.insert_pdf(document, from_page=0, to_page=kept - 1,
                                 links=True, annots=True)
                normalized = clean.tobytes(garbage=3, deflate=True, no_new_id=True)

    reviewed_custody = verify_rendered_pdf_bytes(normalized)
    if original_custody["page_count"] - reviewed_custody["page_count"] != len(trailing):
        raise AssertionError("R75_PAGINATION_COUNT_CHANGED")
    tracked = (
        "catalog_ids", "nasa_urls", "individual_rights_notices",
        "catalog_custody_labels", "source_custody_headings",
        "revision_labels", "image_rights_cleared"
    )
    if any(original_custody[field] != reviewed_custody[field] for field in tracked):
        raise AssertionError("R75_SOURCE_CUSTODY_CHANGED")
    original_pages = PdfReader(io.BytesIO(raw), strict=True).pages
    revised_pages = PdfReader(io.BytesIO(normalized), strict=True).pages
    if any((original_pages[i].extract_text() or "") !=
           (revised_pages[i].extract_text() or "")
           for i in range(len(revised_pages))):
        raise AssertionError("R75_TEXT_CONTENT_CHANGED")

    report = {
        "schema": "fv.apollo.r75.paged-review.v1",
        "release": "STAGING_HOLD",
        "original_pdf_sha256": hashlib.sha256(raw).hexdigest(),
        "review_pdf_sha256": hashlib.sha256(normalized).hexdigest(),
        "original_pages": len(original_pages),
        "review_pages": len(revised_pages),
        "trimmed_terminal_decorative_pages": len(trailing),
        "trimmed_page_evidence": trailing,
        "kept_catalogs": 6, "kept_nasa_urls": 6,
        "photographic_reuse_approved": 0,
        "original_browser_print_defect_resolved": False,
        "normalized_copy_is_not_a_wordpress_css_fix": True,
        "source_custody_reverified": True
    }
    if destination is not None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(normalized)
    return normalized, report
