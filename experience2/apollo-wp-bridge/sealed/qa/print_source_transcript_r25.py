#!/usr/bin/env python3
"""R25: source-verified, media-free Apollo 1 print transcript for private review.

No third-party images, WordPress nonce URLs or geographic inferences are printed.
The transcript is a NASA source/context ledger, not the full investigation.
"""
from __future__ import annotations
import hashlib
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit
from qa.nasa_editorial_gate import WITNESSES, audit
from qa.research_desk_crosswalk import build_crosswalk

CASEFILE = Path(__file__).resolve().parents[3] / 'apollo-casefile'
GENERATED = Path(__file__).resolve().parents[2] / 'generated'
NASA_POLICY = 'https://www.nasa.gov/nasa-brand-center/images-and-media/'
REPORT = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'

CSS = '''/* Apollo private R25 paper-readable record ledger: no javascript. */
#fv-ex2-print-transcript{display:none!important}
@media print{
 @page{margin:16mm}
 html,body{background:#fff!important;color:#111!important;overflow:visible!important;margin:0!important}
 #fv-ex2-apollo-document{background:#fff!important;color:#111!important;width:100%!important;
  max-width:none!important;margin:0!important;padding:0!important;overflow:visible!important}
 #fv-ex2-apollo-document > :not(#fv-ex2-print-transcript){display:none!important}
 #fv-ex2-apollo-document > #fv-ex2-print-transcript{display:block!important}
 #fv-ex2-print-transcript{background:#fff!important;color:#111!important;
  font:11pt/1.45 Georgia,serif!important;max-width:none!important;overflow-wrap:anywhere!important}
 #fv-ex2-print-transcript *{color:#111!important;background:transparent!important;
  box-shadow:none!important;text-shadow:none!important;animation:none!important;transition:none!important}
 #fv-ex2-print-transcript h2{font:bold 23pt/1.15 Georgia,serif!important;margin:0 0 8mm!important}
 #fv-ex2-print-transcript h3{font:bold 14pt/1.2 Georgia,serif!important;margin:0 0 3mm!important}
 #fv-ex2-print-transcript p{margin:2mm 0 3mm!important;max-width:none!important}
 #fv-ex2-print-transcript .fv-ex2-print__intro{border-bottom:2pt solid #111!important;padding-bottom:5mm!important}
 #fv-ex2-print-transcript .fv-ex2-print__item{border-top:1pt solid #555!important;
  padding:5mm 0 4mm!important;break-inside:avoid;page-break-inside:avoid}
 #fv-ex2-print-transcript a{color:#111!important;text-decoration:underline!important;overflow-wrap:anywhere!important}
 #fv-ex2-print-transcript a::after{content:' [ ' attr(href) ' ]';font:8pt/1.2 monospace;
  overflow-wrap:anywhere;word-break:break-word;text-decoration:none}
 #fv-ex2-print-transcript .fv-ex2-print__hold{font-weight:700!important}
 #fv-ex2-print-transcript footer{border-top:2pt solid #111!important;padding-top:4mm!important}
}'''

class PrintCustodyHold(ValueError):
    pass


def build_print_transcript(casefile: Path = CASEFILE, generated: Path = GENERATED) -> tuple[str, str, dict]:
    catalogue = json.loads((casefile/'records.json').read_text(encoding='utf-8'))
    export = json.loads((generated/'evidence-export.json').read_text(encoding='utf-8'))
    fragment = (generated/'fragment.html').read_text(encoding='utf-8')
    audit(catalogue, export, fragment)
    records = catalogue['records']
    crosswalk = build_crosswalk(records)[1]['records']
    if len(records)!=6 or len(WITNESSES)!=6 or len(crosswalk)!=6:
        raise PrintCustodyHold('Six records required')
    if catalogue['rights_policy']!=NASA_POLICY:
        raise PrintCustodyHold('NASA policy link drift')
    if sum(not x['catalog_identifier_label_match'] for x in crosswalk)!=1 or crosswalk[0]['catalog_identifier_label_match']:
        raise PrintCustodyHold('Research Desk identifier discrepancy must remain open')
    rows=[]
    for r,w in zip(records,WITNESSES,strict=True):
        rid,url,catalog,date,credit,era,terms,status,uses=w
        if (r['id'],r['image_url'],r['source_id'],r['source_date'],r['image_credit'],r['rights'])!=(rid,url,catalog,date,credit,status):
            raise PrintCustodyHold('Pinned NASA record mismatch '+rid)
        if urlsplit(url).scheme!='https' or urlsplit(url).hostname!='www.nasa.gov':
            raise PrintCustodyHold('Non-first-party NASA photo URL')
        if status not in ('link_only_persons_visible','link_only_image_transport_unreviewed'):
            raise PrintCustodyHold('Unapproved image reuse status')
        hold = ('<p class="fv-ex2-print__hold">IDENTITY REVIEW HOLD: Research Desk PR #158 uses '
                'NASA S67-19766 for this URL. The NASA source page does not independently confirm '
                'that catalog identifier. NASA S66-30236 identifies a different March 1966 portrait; '
                'no substitution has been approved.</p>') if rid=='01' else ''
        rows.append(f'''<article class="fv-ex2-print__item" data-r25-print-record="{rid}">
<h3>Record {rid} — {escape(r['title'])}</h3>
<p><strong>Claim chronology:</strong> {escape(r['time'])}. <strong>Photograph date:</strong> {escape(date)}. These are not interchangeable.</p>
<p><strong>Documentary finding:</strong> {escape(r['finding'])}</p>
<p><strong>What this photograph cannot prove:</strong> {escape(r['limit'])}</p>
<p><strong>NASA source identifier in casefile:</strong> {escape(catalog)}. <strong>Credit:</strong> {escape(credit)}.</p>
<p><strong>Reuse decision:</strong> LINK ONLY — IMAGE REUSE NOT CLEARED. No media included.</p>
{hold}
<p><a href="{escape(url,quote=True)}" rel="noopener noreferrer" referrerpolicy="no-referrer">View NASA source {rid}</a></p>
</article>''')
    html = f'''<section id="fv-ex2-print-transcript" aria-label="Printable NASA source-custody ledger">
<header class="fv-ex2-print__intro"><p>FINAL VESTIGE STUDIOS / PRIVATE EDITORIAL STAGING</p>
<h2>Apollo 1 — Six-Source Research Custody Ledger</h2>
<p>Print-only source and limitations register, not the full investigation or image-reuse license. Documentary findings derive from the Apollo 204 Review Board; source-photograph dates are not the underlying event dates.</p>
<p><strong>Release status:</strong> HOLD: six image-reuse reviews open, one catalog identifier unresolved, zero geographic pins/edges admitted.</p></header>
{''.join(rows)}
<footer><p>Historical primary source: <a href="{REPORT}">NASA Apollo 204 Review Board</a>.</p>
<p>Media guidance (not individual clearance): <a href="{NASA_POLICY}">NASA Images and Media Usage Guidelines</a>.</p>
<p>This transcript includes no photographs, third-party resources, scripts, authenticated download links or WordPress nonces. No NASA endorsement is implied.</p></footer></section>'''
    lowered=html.lower()
    if any(x in lowered for x in ('<img','<script','<iframe','_wpnonce','admin-ajax','data-lat=','data-lon=','{{fv_')):
        raise PrintCustodyHold('Forbidden media, tokens or speculative geo in print')
    if html.count('data-r25-print-record=')!=6 or html.count('LINK ONLY — IMAGE REUSE NOT CLEARED')!=6:
        raise PrintCustodyHold('Print record/rights count drift')
    receipt={'records':6,'source_urls':6,'images_embedded':0,'image_reuse_approved':0,
             'catalog_label_holds':1,'atlas_pins':0,'atlas_edges':0,'requires_javascript':False,
             'print_contains_nonce':False,
             'html_sha256':hashlib.sha256(html.encode()).hexdigest(),
             'css_sha256':hashlib.sha256(CSS.encode()).hexdigest()}
    return html,CSS,receipt
