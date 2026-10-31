#!/usr/bin/env python3
"""R21: editor-only, zero-JavaScript SHA-256 evidence-export verification shelf.

A checksum permits *byte comparison*, not authenticates a source or rights holder.
Do not mistake the digest for a signature or evidence of publication clearance.
"""
from __future__ import annotations
import hashlib
from html import escape
from pathlib import Path
import re

EXPORT_NAMES = (
    'evidence-export.csv', 'evidence-export.json',
    'response-export.csv', 'response-export.json',
    'source-context.json', 'atlas-admission.json', 'media-rights.json',
)
# URL substitution is performed only after the private PHP route checks the
# editor role and nonce, and after all seven compressed assets pass SHA-256.
PLACEHOLDER_PREFIX = '{{FV_EX2_CUSTODY_EXPORT:'
CASEFILE_SHA = '74375657f2cdaac0710f94c6de6c24534ee06858'

CSS = '''/* Private R21 evidence receipts; all controls are native and no JS is required. */
.fv-ex2-receipts{color:#f3eee5;background:#141916;border-block:1px solid #78633f;padding:clamp(24px,5vw,66px) clamp(16px,5vw,70px);font:inherit;line-height:1.55;overflow-wrap:anywhere;container-type:inline-size}
.fv-ex2-receipts *{box-sizing:border-box}
.fv-ex2-receipts__wrap{max-width:1250px;margin:auto}
.fv-ex2-receipts__eyebrow{color:#eac98a;letter-spacing:.11em;font:700 .75rem/1.6 ui-monospace,monospace;text-transform:uppercase}
.fv-ex2-receipts h2{color:#fff1dc;font:400 clamp(1.7rem,4vw,2.9rem)/1.18 Georgia,serif;margin:.5rem 0 1rem}
.fv-ex2-receipts p{max-width:86ch;color:#e5dccc}
.fv-ex2-receipts__list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;list-style:none;padding:0;margin:24px 0}
.fv-ex2-receipts__item{min-width:0;border:1px solid #88744e;background:#22251f;padding:clamp(14px,2vw,21px)}
.fv-ex2-receipts__item h3{color:#fff0d3;font:400 1.17rem/1.35 Georgia,serif;margin:.25rem 0 .8rem;overflow-wrap:anywhere}
.fv-ex2-receipts__item code{display:block;user-select:all;overflow-wrap:anywhere;word-break:break-word;font:.82rem/1.65 ui-monospace,monospace;background:#111712;color:#fff0cd;border:1px solid #685d44;padding:10px 12px}
.fv-ex2-receipts__item a,.fv-ex2-receipts__wrap>a{color:#ffe0a2;display:inline-flex;align-items:center;min-height:44px;text-decoration:underline;text-underline-offset:4px}
.fv-ex2-receipts :focus-visible{outline:3px solid #ffde91;outline-offset:3px}
.fv-ex2-receipts__warning{border-left:3px solid #e5b26e;padding:12px 18px;background:#30281c}
@container(max-width:740px){.fv-ex2-receipts__list{grid-template-columns:1fr}}
@media(max-width:780px){.fv-ex2-receipts__list{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.fv-ex2-receipts *{animation:none!important;transition:none!important}}
'''

class ReceiptError(ValueError):
    pass


def build_receipts(exports: dict[str, bytes]) -> tuple[str, str, dict]:
    """Return bounded HTML/CSS/receipt from *exact* bytes sent by PHP download.

    The caller must validate NASA/Atlas/rights crosswalks independently before
    passing these bytes. We never fetch external URLs or infer reuse clearance.
    """
    if list(exports) != list(EXPORT_NAMES):
        raise ReceiptError('The seven source-controlled export names/order are mandatory')
    rows = []
    item_hashes = {}
    for filename, content in exports.items():
        if not isinstance(content, bytes) or not 0 < len(content) <= 500_000:
            raise ReceiptError('Missing, invalid or oversized export: ' + filename)
        if not re.fullmatch(r'[a-z0-9-]+\.(?:json|csv)', filename):
            raise ReceiptError('Unsafe export filename')
        digest = hashlib.sha256(content).hexdigest()
        item_hashes[filename] = digest
        placeholder = f'{PLACEHOLDER_PREFIX}{filename}}}}}'
        rows.append(f'''<li class="fv-ex2-receipts__item" data-custody-receipt="{escape(filename,quote=True)}">
<h3>{escape(filename)}</h3>
<p>SHA-256 · {len(content)} verified bytes</p>
<code aria-label="SHA-256 of {escape(filename,quote=True)}">{digest}</code>
<a href="{placeholder}" download="apollo-{escape(filename,quote=True)}">Download and compare {escape(filename)} (private)</a></li>''')
    html = f'''<section id="fv-ex2-custody-receipts" class="fv-ex2-receipts" aria-labelledby="fv-ex2-receipts-title">
<div class="fv-ex2-receipts__wrap"><p class="fv-ex2-receipts__eyebrow">Research Desk / Evidence Custody</p>
<h2 id="fv-ex2-receipts-title">Download receipts for seven research evidence exports</h2>
<p>Each checksum identifies the exact bytes served by this private staging build. Download a record and compare its SHA-256 using a local hashing tool. All seven are restricted to the staging editor session. No JavaScript, map coordinate, embedded NASA photograph, or off-site tracking is required.</p>
<p>Canonical casefile source revision: <code>{CASEFILE_SHA}</code>.</p>
<ol class="fv-ex2-receipts__list">{''.join(rows)}</ol>
<p class="fv-ex2-receipts__warning">A matching checksum only detects a change relative to this reviewed build. It is not a digital signature, a NASA attestation, a historical fact check, a license, or approval to publish. The source catalog discrepancy and all six image-reuse reviews remain open.</p>
</div></section>'''
    if any(token in html.lower() for token in ('<script','<iframe','<img','data-lat=','data-lon=')):
        raise ReceiptError('Custody shelf must remain text-only and inert')
    return html, CSS, {'status':'EDITOR_ONLY_NOT_PUBLISHABLE', 'export_count':len(item_hashes),
                        'exports_sha256':item_hashes,
                        'html_sha256':hashlib.sha256(html.encode('utf-8')).hexdigest(),
                        'css_sha256':hashlib.sha256(CSS.encode('utf-8')).hexdigest(),
                        'canonical_source_revision':CASEFILE_SHA,
                        'not_a_signature':True,'media_reuse_clearances':0,
                        'atlas_admitted_coordinates':0}
