#!/usr/bin/env python3
"""Staging-only >=44px link target repair; no changes to pinned Apollo source."""
from __future__ import annotations
from hashlib import sha256

# Initial Chromium measurements on pristine R23: 79 links below 44px in 8 groups.
SELECTORS = (
    '.fv-ex2-apollo .ex2-hero__actions .ex2-textlink',
    '.fv-ex2-apollo .ex2-source__links a',
    '.fv-ex2-apollo .ex2-custody__claim > a',
    '.fv-ex2-apollo #claim-ledger p > a',
    '.fv-ex2-apollo .ex2-ledger__actions a',
    '.fv-ex2-apollo .ex2-gallery__links a',
    '.fv-ex2-apollo .ex2-atlas__item > a',
    '.fv-ex2-apollo .ex2-footer a',
)
CSS = (',\n'.join(SELECTORS) + '''{
    display:inline-flex;
    align-items:center;
    min-height:44px;
    max-width:100%;
    padding-block:8px;
    white-space:normal;
    overflow-wrap:anywhere;
    vertical-align:middle;
}
.fv-ex2-apollo :is(.ex2-hero__actions,.ex2-source__links,
 .ex2-ledger__actions,.ex2-gallery__links,.ex2-footer) a:focus-visible,
.fv-ex2-apollo #claim-ledger a:focus-visible,
.fv-ex2-apollo .ex2-atlas__item > a:focus-visible,
.fv-ex2-apollo .ex2-custody__claim > a:focus-visible{
    outline:3px solid #ffe4aa;
    outline-offset:3px;
}
@media (prefers-reduced-motion:reduce){
    .fv-ex2-apollo a{transition:none!important;}
}
''')
REQUIRED_MARKERS = ('ex2-hero__actions','ex2-source__links','ex2-custody__claim',
                    'id="claim-ledger"','ex2-ledger__actions','ex2-gallery__links',
                    'ex2-atlas__item','ex2-footer')


def build_touch_targets(fragment: str) -> tuple[str, dict]:
    """Refuse to generate if original source regions drift; no rights promotion."""
    if not isinstance(fragment, str) or any(m not in fragment for m in REQUIRED_MARKERS):
        raise ValueError('R24 source-pinned touch-target regions missing or renamed')
    if any(x in CSS.lower() for x in ('<script','<img','http://','https://','@import','url(')):
        raise ValueError('R24 accessibility stylesheet must be self-contained')
    if CSS.count('min-height:44px') != 1 or len(SELECTORS) != 8:
        raise ValueError('R24 touch target contract changed without review')
    return CSS, {'status':'STAGING_TOUCH_TARGETS_ONLY',
                 'selectors':len(SELECTORS),'target_min_height_css_px':44,
                 'css_sha256':sha256(CSS.encode('utf-8')).hexdigest(),
                 'source_modified':False, 'javascript_required':False,
                 'external_media_embedded':False,'geography_added':False}
