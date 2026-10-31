#!/usr/bin/env python3
"""R19 source-custody admission for the Atlas' six *published-link* cards.

This is not a map, a live WordPress availability check, or a geocoder.
The only primary input is PR215's source-pinned generated HTML. We admit no
map coordinate, spatial relationship or unverified equivalence to Apollo 1.
"""
from __future__ import annotations
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit

GENERATED = Path(__file__).resolve().parents[2] / 'generated'
EXPORT_MARKER = '{{FV_EX2_ATLAS_EXPORT}}'
SOURCE_HEAD = '74375657f2cdaac0710f94c6de6c24534ee06858'

# The six original *WP listing references* only, pinned to the canonical
# Apollo casefile. Never assume they identify a trustworthy map coordinate.
EXPECTED = (
    ('434', 'engineering', 'The Hatch Opened Inward', 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'),
    ('621', 'disasters', 'Six Miles an Hour', 'https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/'),
    ('370', 'disasters', 'The Lines Were in the Fire', 'https://finalvestige.com/2026/08/19/the-lines-were-in-the-fire-west-loch/'),
    ('269', 'disasters', 'The Watch Lost Its Hands', 'https://finalvestige.com/2026/08/18/the-watch-lost-its-hands-halifax-explosion/'),
    ('37', 'engineering', 'How Petra Made Water Flow Through Stone', 'https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/'),
    ('433', 'expeditions', 'All Well Was Written First', 'https://finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/'),
)

CSS = '''/* Atlas editorial admission, not a geographic interface. No JS required. */
.fv-ex2-atlas-admission{font:inherit;color:#f5efe3;margin:clamp(16px,3vw,32px) 0;padding:clamp(14px,2.4vw,26px);border:1px solid #977b51;background:#151815;overflow-wrap:anywhere;container-type:inline-size}
.fv-ex2-atlas-admission summary{cursor:pointer;min-height:48px;padding:10px 8px;font-weight:750;color:#f4d89e;line-height:1.6}
.fv-ex2-atlas-admission p{line-height:1.7;max-width:78ch;color:#e7ded1}
.fv-ex2-atlas-admission__counts{font:700 .81rem/1.65 ui-monospace,monospace;color:#f2d59e;letter-spacing:.02em}
.fv-ex2-atlas-admission__records{list-style:none;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;padding:0;margin:18px 0}
.fv-ex2-atlas-admission__record{min-width:0;padding:14px 16px;border:1px solid #665439;background:#202019}
.fv-ex2-atlas-admission__record strong{display:block;color:#fff6e7;font:normal 1.15rem/1.45 Georgia,serif;margin:6px 0}
.fv-ex2-atlas-admission__review{font:700 .8rem/1.6 ui-monospace,monospace;color:#f3d398}
.fv-ex2-atlas-admission__record p{font-size:.93rem;line-height:1.65;margin:7px 0}
.fv-ex2-atlas-admission a{color:#f3d79c;display:inline-flex;align-items:center;min-height:44px;text-underline-offset:4px}
.fv-ex2-atlas-admission :focus-visible{outline:3px solid #ffe4aa;outline-offset:4px}
@container(max-width:760px){.fv-ex2-atlas-admission__records{grid-template-columns:1fr}}
@media(max-width:780px){.fv-ex2-atlas-admission__records{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){.fv-ex2-atlas-admission *{scroll-behavior:auto!important;transition:none!important}}
'''

class AtlasHold(ValueError):
    pass


class _AtlasParser(HTMLParser):
    """Recover visible text and canonical URLs only from Atlas card elements."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inside = False
        self.level = 0
        self.cards = []
        self.card = None
        self.text_key = None
        self.unsafe = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == 'section' and attr.get('id') == 'atlas':
            if self.inside:
                self.unsafe.append('nested atlas')
            self.inside = True
            self.level = 1
            return
        if not self.inside:
            return
        if tag == 'section':
            self.level += 1
        if tag in ('script','img','iframe','canvas','svg','map') or any(
            k.startswith('on') or k in ('data-lat', 'data-lon','data-lng', 'data-geo','data-edge',
                                          'latitude','longitude','coords','data-coordinate') for k in attr
        ):
            self.unsafe.append('unreviewed spatial/media/executable element')
        if tag == 'article' and 'data-ex2-atlas-item' in attr:
            if self.card:
                self.unsafe.append('nested record')
            self.card = {'theme':attr.get('data-ex2-theme'), 'title':'', 'wp_id':'',
                         'href':'', 'geonote':'', 'summary':''}
        if self.card is None:
            return
        if tag == 'h3':
            self.text_key = 'title'
        elif tag == 'span' and 'ex2-atlas__id' in (attr.get('class') or '').split():
            self.text_key = 'wp_id'
        elif tag == 'p' and 'ex2-atlas__geonote' in (attr.get('class') or '').split():
            self.text_key = 'geonote'
        elif tag == 'p' and not self.card['summary'] and self.card['geonote'] == '':
            self.text_key = 'summary'
        elif tag == 'a':
            if self.card['href']:
                self.unsafe.append('multiple published links')
            self.card['href'] = attr.get('href')
            if attr.get('target') != '_blank' or 'noopener' not in (attr.get('rel') or ''):
                self.unsafe.append('published link security drift')

    def handle_data(self, data):
        if self.card is not None and self.text_key:
            self.card[self.text_key] += data

    def handle_endtag(self, tag):
        if not self.inside:
            return
        if tag in ('h3','p','span'):
            self.text_key = None
        if tag == 'article' and self.card is not None:
            for k in ('title','wp_id','geonote','summary'):
                self.card[k] = ' '.join(self.card[k].split())
            self.cards.append(self.card)
            self.card = None
        if tag == 'section':
            self.level -= 1
            if self.level == 0:
                self.inside = False


def build_atlas_admission(fragment: str | None = None, generated: Path = GENERATED) -> tuple[str,str,str,dict]:
    """Return native disclosure + CSS + deterministic private JSON export + audit."""
    if fragment is None:
        fragment = (generated/'fragment.html').read_text(encoding='utf-8')
    parser = _AtlasParser(); parser.feed(fragment); parser.close()
    if parser.inside or parser.unsafe or len(parser.cards) != 6:
        raise AtlasHold('Atlas staging HOLD: unsafe element, truncated cards, or spatial/media markup')
    records=[]
    for i, (card, expected) in enumerate(zip(parser.cards, EXPECTED, strict=True),1):
        wp_id, theme, title, link = expected
        parsed=urlsplit(card['href'] or '')
        if (card['theme'],card['title'],card['wp_id'],card['href']) != (theme,title,'WP '+wp_id,link):
            raise AtlasHold(f'Atlas staging HOLD: unexpected canonical WP listing/card {i}')
        if parsed.scheme!='https' or parsed.netloc!='finalvestige.com' or parsed.query or parsed.fragment:
            raise AtlasHold(f'Atlas staging HOLD: unsafe published destination {i}')
        if card['geonote'] != 'No mapped location: archival precision unreviewed.':
            raise AtlasHold(f'Atlas staging HOLD: map status changed without primary location evidence {i}')
        if not card['summary'] or len(card['summary']) > 300:
            raise AtlasHold(f'Atlas staging HOLD: missing/oversized source summary {i}')
        records.append({'wordpress_listing_id':int(wp_id), 'title':title, 'theme':theme,
                        'published_link_from_pinned_source':link,'casefile_summary':card['summary'],
                        'listing_origin':'PINNED_CASEFILE_LINK_NOT_LIVE_WORDPRESS_VERIFIED',
                        'geographic_admission':'WITHHELD_PENDING_DOCUMENTED_POINT_OR_REGION_PRECISION',
                        'coordinates':None,'geo_edges':[], 'map_pin_eligible':False,
                        'relationships_to_apollo_records':'NONE_ESTABLISHED',
                        'source_media_reuse':'NOT_CLEARED_BY_THIS_ATLAS_INDEX'})
    obj={'schema':'fv-ex2-atlas-admission-v1','canonical_source_commit':SOURCE_HEAD,
         'scope':'SIX_PUBLISHED_LINKS_ONLY_NOT_HISTORICAL_GEOGRAPHY',
         'not_live_wordpress_availability_check':True,
         'not_map_or_rights_clearance':True, 'admitted_point_coordinates':0,
         'admitted_relationship_edges':0,'pending_source_review':len(records),
         'record_count':len(records),'records':records}
    export=json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2)+'\n'
    rows=[]
    for row in records:
        rows.append(f'''<li class="fv-ex2-atlas-admission__record" data-admission-record="{row['wordpress_listing_id']}">
<div class="fv-ex2-atlas-admission__review">WP {row['wordpress_listing_id']} · {escape(row['theme'])} · LOCATION REVIEW PENDING</div>
<strong>{escape(row['title'])}</strong>
<p>Published entry URL is listed in the pinned casefile. A primary-source location record, precision and reusable mapping rights have not been admitted. No coordinates or inferred relation to Apollo 1.</p>
<a href="{escape(row['published_link_from_pinned_source'],quote=True)}" target="_blank" rel="noopener noreferrer" referrerpolicy="no-referrer">Open original published investigation <span class="ex2-sr-only">(opens in new tab)</span></a></li>''')
    html=f'''<details id="fv-ex2-atlas-admission" class="fv-ex2-atlas-admission">
<summary>Atlas source and mapping admission — six published links, zero approved pins</summary>
<p>These are curated links from the pinned Final Vestige casefile, not independently verified coordinates. Every listing remains geographically unadmitted pending primary-source and precision review. A familiar place name is not sufficient evidence for a map pin, route or relationship edge. This index makes no claim of direct documentary connection between these investigations.</p>
<p class="fv-ex2-atlas-admission__counts">6 published-entry links · 0 source-approved coordinates · 0 relationship edges · 6 location reviews pending</p>
<ol class="fv-ex2-atlas-admission__records">{''.join(rows)}</ol>
<p><a href="{EXPORT_MARKER}" download="apollo-atlas-admission.json">Download the Atlas admission / withheld-geography ledger (JSON)</a></p>
<p>This is an independent editorial status report, not a NASA/WordPress endorsement, a live WordPress availability check or media-reuse permission.</p></details>'''
    if any(x in html.lower() for x in ('<img','<script','<iframe','<canvas','<svg')):
        raise AtlasHold('Atlas cannot embed media, maps, or active HTML')
    digest=lambda s:sha256(s.encode('utf-8')).hexdigest()
    receipt={'status':'PASS_SIX_SOURCE_PINNED_LINKS_ZERO_GEOGRAPHY',
             'published_link_records':6,'map_coordinates':0,'map_edges':0,
             'pending_primary_source_location_review':6,'src_fragment_sha256':digest(fragment),
             'html_sha256':digest(html),'css_sha256':digest(CSS),'json_sha256':digest(export),
             'links_verified_live':False,'photos_embedded':0,'no_js_native_details':True}
    return html,CSS,export,receipt
