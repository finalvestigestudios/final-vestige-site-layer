#!/usr/bin/env python3
"""R231: compare both draft exports with an in-memory replay of pinned producer.

This is byte-level custody of the *generated* HTML, not a medical, citation,
source-access, legal, accessibility or release approval. No files are written.
The caller MUST authenticate the builder and every underlying producer input.
"""
from __future__ import annotations

HOLD = 'DRAFT_HARD_HOLD'
ROW_KEYS = ('slug', 'words', 'minutes', 'sources', 'canonical')


def verify_exact_export(page: str, mode: str, slug: str, meta: dict,
                        library, builder, row: dict) -> dict:
    """Fail closed on any export-byte or build-report difference for one draft."""
    if (type(page) is not str or mode not in ('wp', 'preview')
            or type(slug) is not str or not slug
            or type(meta) is not dict or type(row) is not dict):
        raise ValueError('R231 invalid draft export contract')
    if meta.get('slug') != slug or meta.get('status', {}).get('publish') != 'draft':
        raise ValueError('R231 article identity or draft status changed: ' + slug)
    built = builder.build_article(library, slug)
    if type(built) is not dict or type(built.get('inner')) is not str:
        raise ValueError('R231 producer did not return an HTML article: ' + slug)
    for key in ROW_KEYS:
        if row.get(key) != built.get(key):
            raise ValueError('R231 build-report discrepancy: ' + slug + ':' + key)
    if mode == 'wp':
        expected = builder.wp_wrap(library, built['inner'])
    else:
        try:
            expected = builder.preview_wrap(
                library, built['inner'], meta['h1'] + ' | The Preparedness Archive',
                meta['description'])
        except (KeyError, TypeError) as exc:
            raise ValueError('R231 preview metadata missing: ' + slug) from exc
    if type(expected) is not str or page.encode('utf-8') != expected.encode('utf-8'):
        raise ValueError('R231 exact export bytes changed: ' + mode + ':' + slug)
    return {'state': HOLD, 'release_authorized': False, 'exact_export_bytes': True,
            'mode': mode, 'slug': slug}
