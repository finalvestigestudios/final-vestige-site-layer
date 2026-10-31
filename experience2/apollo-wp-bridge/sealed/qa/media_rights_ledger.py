#!/usr/bin/env python3
"""R20: conservative, source-derived NASA media reuse decision register.

A checked NASA source URL is not evidence of item-level reproduction clearance.
This generator is intentionally offline. It renders URL-only, native/JS-free
review cards and a private JSON decision ledger. Every item remains HOLD.
"""
from __future__ import annotations
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit
from qa.nasa_editorial_gate import WITNESSES, NASA_MEDIA_RULES, audit
from qa.research_desk_crosswalk import build_crosswalk

CASEFILE = Path(__file__).resolve().parents[3] / 'apollo-casefile'
GENERATED = Path(__file__).resolve().parents[2] / 'generated'
EXPORT_MARKER = '{{FV_EX2_RIGHTS_EXPORT}}'
SOURCE_HEAD = '74375657f2cdaac0710f94c6de6c24534ee06858'
RESEARCH_DESK_HEAD = '250d7f05a4de037e73826dcf0cfaef0ec4c29383'

CSS = '''/* Private R20 media review: editorial URLs only; never embeds NASA photographs. */
.fv-ex2-rights{color:#f5f0e7;background:#101410;border-block:1px solid #78613e;padding:clamp(25px,5vw,65px) clamp(16px,5vw,72px);font:inherit;line-height:1.65;container-type:inline-size;overflow-wrap:anywhere}
.fv-ex2-rights *{box-sizing:border-box}
.fv-ex2-rights__wrap{width:min(1260px,100%);margin:auto}
.fv-ex2-rights h2{font:400 clamp(1.8rem,4vw,3rem)/1.17 Georgia,serif;color:#fff6e9;margin:.5rem 0 1rem}
.fv-ex2-rights p{max-width:82ch;color:#e3d8c8}
.fv-ex2-rights__eyebrow{font:700 .78rem/1.5 ui-monospace,monospace;letter-spacing:.12em;color:#f0ce93}
.fv-ex2-rights__status{color:#ffe0a8;font:700 .8rem/1.6 ui-monospace,monospace}
.fv-ex2-rights__cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:28px 0;padding:0;list-style:none}
.fv-ex2-rights__card{min-width:0;background:#20231f;border:1px solid #7c6746;padding:clamp(14px,2vw,22px)}
.fv-ex2-rights__card h3{font:400 1.2rem/1.4 Georgia,serif;color:#fff3df;margin:9px 0}
.fv-ex2-rights__card details{border-top:1px solid #6b604d;margin-top:12px;padding-top:4px}
.fv-ex2-rights__card summary{cursor:pointer;min-height:46px;padding:11px 3px;color:#f7d99f;font-weight:700;line-height:1.6}
.fv-ex2-rights a{color:#ffe1a9;display:inline-flex;align-items:center;min-height:44px;text-underline-offset:4px}
.fv-ex2-rights :focus-visible{outline:3px solid #ffe0a8;outline-offset:3px}
.fv-ex2-rights__note{border-left:3px solid #f1ca87;padding:10px 17px;background:#25231c;margin-top:18px}
@container(max-width:740px){.fv-ex2-rights__cards{grid-template-columns:1fr}}
@media(max-width:780px){.fv-ex2-rights__cards{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.fv-ex2-rights *{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
'''

class MediaHold(ValueError):
    pass


def build_media_rights(casefile: Path = CASEFILE, generated: Path = GENERATED) -> tuple[str,str,str,dict]:
    """Construct authenticated editor-only review UI/JSON; fail closed on drift."""
    records = json.loads((casefile/'records.json').read_text(encoding='utf-8'))
    exported = json.loads((generated/'evidence-export.json').read_text(encoding='utf-8'))
    fragment = (generated/'fragment.html').read_text(encoding='utf-8')
    audit(records, exported, fragment)
    crosswalk = build_crosswalk(records['records'])[1]
    cross = crosswalk['records']
    if len(cross) != 6 or sum(not r['catalog_identifier_label_match'] for r in cross) != 1 or cross[0]['catalog_identifier_label_match']:
        raise MediaHold('Research Desk catalog discrepancy must remain visible')
    if records['rights_policy'] != NASA_MEDIA_RULES:
        raise MediaHold('Original NASA media policy reference changed')
    if urlsplit(NASA_MEDIA_RULES).hostname != 'www.nasa.gov':
        raise MediaHold('Rights policy must remain on NASA domain')
    rows = []
    cards = []
    for source, witness, x in zip(records['records'],WITNESSES,cross,strict=True):
        rid,url,catalog,date,credit,era,description_terms,status,uses=witness
        if (source['id'],source['image_url'],source['source_id'],source['source_date'],source['image_credit'],source['rights']) != (rid,url,catalog,date,credit,status):
            raise MediaHold(f'NASA media review source drift at {rid}')
        if source['rights'] not in ('link_only_persons_visible','link_only_image_transport_unreviewed'):
            raise MediaHold(f'NASA inline reproduction risk unreviewed at {rid}')
        needs_person_review = status == 'link_only_persons_visible'
        mismatch = not x['catalog_identifier_label_match']
        if mismatch != (rid == '01'):
            raise MediaHold('Photograph ID uncertainty silently changed')
        row = {
            'claim_id':rid,'nasa_catalog_link':url,'nasa_catalog_label_in_casefile':catalog,
            'source_date':date,'image_credit':credit,'source_context':era,
            'current_delivery':'NASA_EXTERNAL_LINK_ONLY','inline_reuse_review':'HOLD_NOT_ADMITTED',
            'individual_publicity_review': 'PENDING_IF_COMMERCIAL_OR_PROMOTIONAL' if needs_person_review else 'NOT_ASSESSED',
            'third_party_rights_review':'PENDING_PER_ITEM','nasa_endorsement':'NOT_CLAIMED',
            'catalog_label_discrepancy':mismatch,
            'research_desk_label':x['research_desk_catalog_label'],
            'editorial_note':('Same URL, different catalog labels; confirm against first-party source before attribution.'
                              if mismatch else 'Matching draft labels do not independently prove reuse rights.'),
            'photo_embedded':False,'geo_coordinates':None,'source_drawer':f'#source-{rid}',
            'chronology':f'#stage-{rid}','nasa_policy':NASA_MEDIA_RULES,
        }
        rows.append(row)
        flag='CATALOG LABEL REVIEW OPEN' if mismatch else 'CATALOG URL SOURCE-PINNED'
        extra=('<p class="fv-ex2-rights__note">Research Desk calls this NASA S67-19766; the casefile instead '
               'uses a descriptive label. Identical URLs do not settle the catalog identifier.</p>' if mismatch else '')
        cards.append(f'''<li class="fv-ex2-rights__card" data-media-review="{rid}" data-media-hold="true">
<p class="fv-ex2-rights__status">{rid} / INLINE IMAGE REUSE ON HOLD / {flag}</p>
<h3>{escape(catalog)}</h3><p>Source date: {escape(date)}. Credit in casefile: {escape(credit)}.</p>
<details><summary>Review provenance and publication conditions for source {rid}</summary>
<p>NASA imagery is generally available for informational use under its guidelines, but third-party material, branding, and recognizable people can impose conditions. No per-item clearance is recorded here; source-page links are provided instead of reproducing images.</p>
{extra}<p><a href="{escape(url,quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Inspect NASA catalog record (opens in new tab)</a></p>
<p><a href="#source-{rid}">Inspect SourceDrawer {rid}</a> · <a href="#stage-{rid}">Review chronology {rid}</a></p></details></li>''')
    obj = {'schema':'fv-ex2-media-rights-hold-v1','canonical_source_commit':SOURCE_HEAD,
           'research_desk_draft_head':RESEARCH_DESK_HEAD,'review_scope':'EDITORIAL_RECORD_ONLY_NO_LEGAL_RIGHTS_CLEARANCE',
           'nasa_policy_url':NASA_MEDIA_RULES,'policy_guidance_rechecked':'2026-10-31',
           'not_an_item_level_license':True,'images_embedded':0,'cleared_images':0,
           'catalog_label_holds':1,'source_records':6,'records':rows}
    payload=json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    html=f'''<section id="fv-ex2-media-rights" class="fv-ex2-rights" aria-labelledby="fv-ex2-rights-title">
<div class="fv-ex2-rights__wrap"><p class="fv-ex2-rights__eyebrow">NASA MATERIAL / EDITORIAL RIGHTS DESK</p>
<h2 id="fv-ex2-rights-title">Six catalog links. Zero photographs cleared for embedding in this review.</h2>
<p>NASA's general informational-use guidance is not a blanket item-level attribution or rights determination. All six images remain external links while image-specific ownership, possible third-party rights, recognizable people and NASA-identifiers are assessed. This independent investigation does not imply NASA endorsement.</p>
<p class="fv-ex2-rights__status">6 source records · 6 image-reuse decisions pending · 1 catalog label discrepancy · 0 embedded images</p>
<ol class="fv-ex2-rights__cards">{''.join(cards)}</ol>
<p><a href="{NASA_MEDIA_RULES}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Read NASA Images and Media Usage Guidelines (opens in new tab)</a></p>
<a href="{EXPORT_MARKER}" download="apollo-media-rights-hold.json">Download this source-custody and image-rights hold index (JSON)</a>
<p class="fv-ex2-rights__note">The source rights register is an editorial control, not a license, proof of URL availability, nor proof of final publication eligibility.</p></div></section>'''
    if any(v in html.lower() for v in ('<img','<picture','<script','<iframe','data-lat=','data-lon=')):
        raise MediaHold('Media ledger must not include executable, embedded or geographic content')
    receipt={'status':'HOLD_ALL_IMAGE_REUSE','records':6,'links_only':6,'catalog_label_holds':1,
             'images_embedded':0,'nasa_policy_url':NASA_MEDIA_RULES,
             'html_sha256':sha256(html.encode('utf-8')).hexdigest(),
             'css_sha256':sha256(CSS.encode('utf-8')).hexdigest(),
             'json_sha256':sha256(payload.encode('utf-8')).hexdigest()}
    return html,CSS,payload,receipt
