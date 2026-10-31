#!/usr/bin/env python3
"""R22 editorial evidence wayfinder, derived from audited source/rights/Atlas receipts.

This is navigational *presentation*, not NASA validation or a geo admission.
No JS, external imagery, interpreted map edges, or new WP endpoints.
"""
from __future__ import annotations
from hashlib import sha256
from html import escape
import json
from typing import Mapping

SOURCE_HEAD = '74375657f2cdaac0710f94c6de6c24534ee06858'

# Targets are existing canonical casefile or R14-R21 section IDs. They are
# checked against the composed PHP before any private response is transmitted.
SECTIONS = (
    ('source-concordance', 'Compare the source', 'Six NASA source records', 'SOURCE CONTEXT'),
    ('chronology', 'Follow the chronology', 'Evidence stages and limits', 'EVENT SEQUENCE'),
    ('source-gallery', 'Inspect the gallery', 'Six archival metadata plates', 'SOURCE GALLERY'),
    ('fv-ex2-research-desk-crosswalk', 'Check Research Desk', 'One catalog label needs review', 'EDITORIAL HOLD'),
    ('fv-ex2-media-rights', 'Review image use', 'Six reuse reviews remain open', 'RIGHTS HOLD'),
    ('atlas', 'Explore the Atlas', 'Zero admitted point coordinates', 'GEOGRAPHY HOLD'),
    ('fv-ex2-custody-receipts', 'Verify source exports', 'Seven private checksums', 'EDITOR ACCESS'),
)

CSS = '''/* R22 provenance-first, no-JavaScript investigation wayfinder. Scoped to private preview. */
.fv-ex2-wayfinder{color:#f5e9d7;background:#111815;border-block:1px solid #a08456;padding:clamp(22px,4vw,52px) clamp(16px,5vw,68px);container-type:inline-size;line-height:1.5}
.fv-ex2-wayfinder *{box-sizing:border-box}
.fv-ex2-wayfinder__inner{max-width:1220px;margin:0 auto}
.fv-ex2-wayfinder__eyebrow{color:#ffdd9e;font:700 .75rem/1.5 ui-monospace,monospace;text-transform:uppercase;letter-spacing:.11em;margin:0 0 10px}
.fv-ex2-wayfinder h2{font:400 clamp(1.5rem,3.6vw,2.7rem)/1.18 Georgia,serif;color:#fff1dc;margin:0 0 .75em}
.fv-ex2-wayfinder__intro,.fv-ex2-wayfinder__caution{color:#f2e3cf;max-width:85ch;margin:0 0 1.1rem}
.fv-ex2-wayfinder__list{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:11px;list-style:none;padding:0;margin:20px 0}
.fv-ex2-wayfinder__list li{min-width:0}
.fv-ex2-wayfinder__list a{display:flex;flex-direction:column;gap:5px;min-height:106px;padding:14px 16px;border:1px solid #927b53;background:#212922;color:#ffe3aa;text-decoration:none;text-underline-offset:4px;overflow-wrap:anywhere}
.fv-ex2-wayfinder__list a:hover,.fv-ex2-wayfinder__list a:focus-visible{background:#354035;border-color:#ffdb99}
.fv-ex2-wayfinder__list a:focus-visible{outline:3px solid #ffde91;outline-offset:3px}
.fv-ex2-wayfinder__target{font:700 .69rem/1.5 ui-monospace,monospace;color:#e9c58d;text-transform:uppercase;letter-spacing:.08em}
.fv-ex2-wayfinder__label{font:400 1.14rem/1.3 Georgia,serif;color:#fff0d7;text-decoration:underline;text-underline-offset:4px}
.fv-ex2-wayfinder__detail{font-size:.88rem;color:#f0e5d5;text-decoration:none}
.fv-ex2-wayfinder__caution{padding:12px 14px;border-left:3px solid #efc580;background:#2a251d;margin-bottom:0}
@container(max-width:770px){.fv-ex2-wayfinder__list{grid-template-columns:repeat(2,minmax(0,1fr))}}
@container(max-width:480px){.fv-ex2-wayfinder__list{grid-template-columns:1fr}}
@media(max-width:700px){.fv-ex2-wayfinder__list{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.fv-ex2-wayfinder *{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
'''

class WayfinderError(ValueError):
    pass


def build_wayfinder(concordance: Mapping, media: Mapping, atlas: Mapping,
                    *, receipt_export_count: int = 7) -> tuple[str, str, dict]:
    """Reject stale/corrupt editorial snapshot and render seven actual anchors."""
    if (concordance.get('record_count') != 6 or
        concordance.get('research_desk_crosswalk',{}).get('catalog_label_review_holds') != 1 or
        concordance.get('photos_embedded') != 0 or
        concordance.get('geographic_pins') != 0 or
        media.get('status') != 'HOLD_ALL_IMAGE_REUSE' or
        media.get('records') != 6 or
        media.get('links_only') != 6 or
        media.get('catalog_label_holds') != 1 or
        media.get('images_embedded') != 0 or
        atlas.get('map_coordinates') != 0 or
        atlas.get('map_edges') != 0 or
        atlas.get('published_link_records') != 6 or
        atlas.get('pending_primary_source_location_review') != 6 or
        receipt_export_count != 7):
        raise WayfinderError('Editorial wayfinder refused inconsistent source/rights/Atlas holds')
    lines=[]
    for target,label,detail,status in SECTIONS:
        # All values are code-defined; escape regardless to prevent later misuse.
        lines.append('<li><a href="#' + escape(target,quote=True) + '">'
                     '<span class="fv-ex2-wayfinder__target">' + escape(status) + '</span>'
                     '<span class="fv-ex2-wayfinder__label">' + escape(label) + '</span>'
                     '<span class="fv-ex2-wayfinder__detail">' + escape(detail) + '</span>'
                     '</a></li>')
    html = ('<nav id="fv-ex2-wayfinder" class="fv-ex2-wayfinder" aria-labelledby="fv-ex2-wayfinder-title">'
            '<div class="fv-ex2-wayfinder__inner">'
            '<p class="fv-ex2-wayfinder__eyebrow">Research Desk / Apollo 1 · private staging</p>'
            '<h2 id="fv-ex2-wayfinder-title">Follow the evidence, not the appearance of certainty</h2>'
            '<p class="fv-ex2-wayfinder__intro">Choose a route through the documentary record. '
            'Each route leads to a source, an interpretation, or a stated limit; the gallery '
            'contains typographic archival plates, not copied NASA photographs.</p>'
            '<ol class="fv-ex2-wayfinder__list">' + ''.join(lines) + '</ol>'
            '<p class="fv-ex2-wayfinder__caution">Not publication approval: six image-reuse '
            'reviews remain open, one source catalog label is unresolved, and the Atlas has '
            'zero admitted point coordinates or inferred edges. Checksums compare bytes; '
            'they do not authenticate NASA records.</p>'
            '</div></nav>')
    if len(SECTIONS) != 7 or html.count('href="#') != 7 or any(t in html.lower() for t in ('<script','<img','<iframe','data-lat=')):
        raise WayfinderError('Wayfinder must remain bounded, linked and inert')
    return html, CSS, {
        'status': 'DRAFT_EDITORIAL_HOLDS_VISIBLE',
        'canonical_source_commit':SOURCE_HEAD,
        'wayfinder_targets':[t[0] for t in SECTIONS],
        'source_records':6,'media_rights_reuse_holds':6,
        'research_desk_identifier_review_holds':1,
        'admitted_coordinates':0,'admitted_edges':0,'custody_export_receipts':7,
        'no_js_native_anchor_links':True,
        'html_sha256':sha256(html.encode('utf-8')).hexdigest(),
        'css_sha256':sha256(CSS.encode('utf-8')).hexdigest(),
    }
