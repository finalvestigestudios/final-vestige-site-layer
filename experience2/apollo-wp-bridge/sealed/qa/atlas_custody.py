#!/usr/bin/env python3
"""Pinned, non-geocoding Atlas provenance witness for Apollo private staging.

The six entries are WordPress publication *references*, not historical-geography
certifications. No lookups, no coordinates, no edges, no NASA images or CMS writes.
"""
from __future__ import annotations
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path

GENERATED = Path(__file__).resolve().parents[2] / 'generated'
EXPORT_MARKER = '{{FV_EX2_ATLAS_EXPORT}}'

# Editorial allowlist, copied only from pinned casefile's existing Atlas; not
# fabricated site links or an assertion of publication URL live-health.
EXPECTED = (
 ('434','engineering','The Hatch Opened Inward','https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),
 ('621','disasters','Six Miles an Hour','https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/'),
 ('370','disasters','The Lines Were in the Fire','https://finalvestige.com/2026/08/19/the-lines-were-in-the-fire-west-loch/'),
 ('269','disasters','The Watch Lost Its Hands','https://finalvestige.com/2026/08/18/the-watch-lost-its-hands-halifax-explosion/'),
 ('37','engineering','How Petra Made Water Flow Through Stone','https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/'),
 ('433','expeditions','All Well Was Written First','https://finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/'),
)

class AtlasHold(ValueError):
    pass

class AtlasParser(HTMLParser):
    """Parse only the actual Atlas subtree, without a regex-for-HTML shortcut."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_atlas = False
        self.atlas_depth = 0
        self.atlas_count = 0
        self.cards = []
        self.card = None
        self.capture = None
        self.buffer = []
        self.forbidden = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'section' and a.get('id') == 'atlas':
            if self.in_atlas or self.atlas_count:
                raise AtlasHold('Atlas root duplicated')
            self.in_atlas = True
            self.atlas_depth = 1
            self.atlas_count += 1
            return
        if not self.in_atlas:
            return
        if tag == 'section':
            self.atlas_depth += 1
        # Reject ALL source attempts to turn the evidence directory into an
        # implicitly licensed image/map/geospatial edge surface.
        for key, value in attrs:
            k = key.lower()
            if (k in ('lat','lng','lon','latitude','longitude','coordinates','data-geo',
                      'data-lat','data-lng','data-long','data-longitude','data-latitude',
                      'data-map-edge','data-connection','data-edge','data-geometry')
                or k.startswith('data-geo-') or k.startswith('on')):
                self.forbidden.append((tag, key, value))
        if tag in ('img','picture','video','svg','canvas','iframe','script','source'):
            self.forbidden.append((tag,'element',''))
        if tag == 'article':
            if self.card is not None or 'data-ex2-atlas-item' not in a:
                raise AtlasHold('Unexpected Atlas article hierarchy')
            self.card = {'theme':a.get('data-ex2-theme'), 'urls':[], 'title':'',
                         'wp':'', 'geonote':''}
        if self.card is not None:
            if tag == 'h3': self.capture='title';self.buffer=[]
            elif tag == 'span' and 'ex2-atlas__id' in (a.get('class') or '').split():
                self.capture='wp';self.buffer=[]
            elif tag == 'p' and 'ex2-atlas__geonote' in (a.get('class') or '').split():
                self.capture='geonote';self.buffer=[]
            elif tag == 'a': self.card['urls'].append(a.get('href'))

    def handle_data(self, data):
        if self.card is not None and self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if not self.in_atlas: return
        if self.card is not None and self.capture and (
          (self.capture=='title' and tag=='h3') or
          (self.capture=='wp' and tag=='span') or
          (self.capture=='geonote' and tag=='p')):
            self.card[self.capture]=' '.join(''.join(self.buffer).split())
            self.capture=None;self.buffer=[]
        if tag == 'article':
            if self.card is None: raise AtlasHold('Unexpected Atlas article close')
            self.cards.append(self.card)
            self.card=None
        if tag == 'section':
            self.atlas_depth -= 1
            if self.atlas_depth == 0: self.in_atlas=False


def vetted_records(generated: Path = GENERATED) -> tuple[list[dict],bytes]:
    raw=(generated/'fragment.html').read_bytes()
    parser=AtlasParser()
    try:
        parser.feed(raw.decode('utf-8'))
        parser.close()
    except (UnicodeDecodeError,ValueError) as exc:
        raise AtlasHold('Atlas source parsing rejected: '+str(exc)) from exc
    if parser.atlas_count != 1 or parser.in_atlas or parser.atlas_depth != 0:
        raise AtlasHold('Atlas root missing or unclosed')
    if parser.forbidden:
        raise AtlasHold('Map coordinates, edges, media or active HTML are prohibited in Atlas')
    if len(parser.cards)!=len(EXPECTED):
        raise AtlasHold('Atlas must contain exactly six reviewed publication references')
    records=[]
    for ordinal,(c,expected) in enumerate(zip(parser.cards,EXPECTED),1):
        wp,theme,title,url=expected
        if (c['wp'] != 'WP '+wp or c['theme']!=theme or c['title']!=title
            or c['urls']!=[url] or
            c['geonote']!='No mapped location: archival precision unreviewed.'):
            raise AtlasHold('Atlas publication, canonical link, or no-map notice drifted at '+str(ordinal))
        records.append({'order':ordinal,'wordpress_post_id':int(wp),
            'theme':theme,'title':title,'published_article_url':url,
            'link_status':'PINNED_IN_CASEFILE_NOT_LIVE_HTTP_VERIFIED',
            'geographic_evidence_status':'NOT_REVIEWED',
            'coordinates':None,'map_pin_eligible':False,
            'relationship_edges':[],'image_assets':[],
            'independent_historical_location_source':None})
    return records,raw


def build_atlas(generated: Path = GENERATED) -> tuple[str,str,str,dict]:
    records,raw=vetted_records(generated)
    payload={'schema':'fv-ex2-atlas-publication-custody-v1',
        'canonical_source_commit':'74375657f2cdaac0710f94c6de6c24534ee06858',
        'source_fragment_sha256':sha256(raw).hexdigest(),
        'editorial_state':'PUBLICATION_INDEX_ONLY_GEO_UNVERIFIED',
        'not_an_independent_source_verification':True,
        'not_a_geographic_certification':True,
        'published_link_live_status':'NOT_CHECKED_IN_THIS_OFFLINE_BUILD',
        'records':records,'record_count':6,'map_pin_count':0,
        'relationship_edge_count':0,'embedded_media_count':0}
    data=json.dumps(payload,sort_keys=True,indent=2,ensure_ascii=False)+'\n'
    cells=[]
    for row in records:
        cells.append('<li class="fv-ex2-atlas-custody__record" data-atlas-custody-id="'+str(row['wordpress_post_id'])+'">'
            '<span class="fv-ex2-atlas-custody__kind">'+escape(row['theme'].upper())+' · WP '+str(row['wordpress_post_id'])+'</span>'
            '<strong>'+escape(row['title'])+'</strong>'
            '<span>Location precision: <b>not independently reviewed</b> · map pins: none</span>'
            '<a href="'+escape(row['published_article_url'],quote=True)+'" target="_blank" '
            'rel="noopener noreferrer" referrerpolicy="no-referrer">Published article reference '
            '<span class="ex2-sr-only">(opens in a new tab)</span></a></li>')
    html='''<details id="fv-ex2-atlas-custody" class="fv-ex2-atlas-custody">
<summary>Inspect geographic evidence eligibility and source custody (six investigations)</summary>
<div class="fv-ex2-atlas-custody__body">
<p><strong>Six editorial publication references; zero verified map points.</strong> The existence of an article is not evidence for an exact coordinate, track or relationship edge. Every entry remains unmapped until independent place precision and primary sources have been reviewed. Do not infer a location from a title or from a NASA photograph.</p>
<ol class="fv-ex2-atlas-custody__list">'''+''.join(cells)+'''</ol>
<p>This index documents links in the pinned casefile, not a live-HTTP audit, source-image clearance, historical geocoding approval or NASA affiliation. Map edges are intentionally absent.</p>
<a class="fv-ex2-atlas-custody__download" href="'''+EXPORT_MARKER+'''" download="apollo-atlas-custody.json">Download Atlas editorial custody index (JSON)</a>
</div></details>'''
    css='''/* Geolocation is deliberately not displayed or simulated. Native no-JS disclosure. */
.fv-ex2-atlas-custody{margin:28px 0 16px;border:1px solid #806b4e;background:#151914;color:#f0e7d8;container-type:inline-size;overflow-wrap:anywhere}
.fv-ex2-atlas-custody>summary{cursor:pointer;padding:18px 22px;min-height:52px;font-weight:700;color:#f8d59a;line-height:1.6}
.fv-ex2-atlas-custody__body{padding:4px clamp(14px,3vw,26px) 24px;line-height:1.7}
.fv-ex2-atlas-custody__body>p{max-width:85ch;color:#e5dcd0}
.fv-ex2-atlas-custody__list{list-style:none;margin:16px 0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.fv-ex2-atlas-custody__record{border:1px solid #79674e;padding:16px;display:flex;flex-direction:column;gap:8px;min-width:0}
.fv-ex2-atlas-custody__record strong{font:normal 1.13rem/1.4 Georgia,serif;color:#fff4e4}
.fv-ex2-atlas-custody__kind{font:700 .72rem/1.5 ui-monospace,monospace;color:#d5b77e;letter-spacing:.04em}
.fv-ex2-atlas-custody a{color:#f6d597;display:inline-flex;align-items:center;min-height:44px;text-underline-offset:4px}
.fv-ex2-atlas-custody :focus-visible{outline:3px solid #ffe4a7;outline-offset:3px}
@container(max-width:850px){.fv-ex2-atlas-custody__list{grid-template-columns:1fr}}
@media(max-width:750px){.fv-ex2-atlas-custody__list{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.fv-ex2-atlas-custody *{transition:none!important;scroll-behavior:auto!important}}
'''
    if any(x in html.lower() for x in ('<img','<script','<iframe','<canvas','<svg')):
        raise AtlasHold('Atlas custody panel must remain link-only and static')
    digest=lambda t:sha256(t.encode('utf-8')).hexdigest()
    return html,css,data,{
        'status':'PASS_PINNED_PUBLICATION_INDEX_WITHOUT_GEO',
        'record_count':6,'map_pin_count':0,'relationship_edge_count':0,
        'media_embedded_count':0,'no_js_native_details':True,
        'atlas_html_sha256':digest(html),
        'atlas_css_sha256':digest(css),
        'atlas_index_sha256':digest(data),
        'source_fragment_sha256':sha256(raw).hexdigest(),
    }
