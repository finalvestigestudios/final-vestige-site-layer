#!/usr/bin/env python3
"""Apollo R203: replace UI component jargon and reinforce source/reader trust.

Retains one free editorial CTA; no affiliate, tracking, image, or WP writes.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'apollo-r202'
DIST = HERE / 'dist'
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

CHANGES = (
    ('01 / ChronologyRail', '01 / The documented sequence'),
    ('02 / EvidencePlate', '02 / What the investigators found'),
    ('03 / SourceDrawer + curated archival gallery', '03 / NASA photographic records'),
    ('04 / The next evidence step', '04 / Continue the investigation'),
    ('Research Desk / Try the source test', 'Try it yourself / Compare the evidence'),
    ('Research Desk / how to read this case', 'How to read the evidence'),
    ('Source custody / claim-to-record crosswalk', 'From a finding to its source'),
)
NOTE = '''<p class="fv-apollo-citation-route"><strong>Check the original record:</strong> NASA’s <a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Apollo 204 Review Board report</a> documents the investigation, while the <a href="https://www.nasa.gov/image-detail/amf-s67-21294/">January 28, 1967 photograph catalog</a> documents the damaged spacecraft. These are different kinds of evidence; neither establishes the precise initiating spark. The source links are free to read.</p>'''
CSS = '''
/* R203: visitor-first source-reading language. Source IDs stay stable. */
.fv-apollo-atlas .fv-apollo-citation-route{margin:.8rem 0 1.3rem;padding:.8rem 1rem;border-left:3px solid var(--accent);background:var(--surface);overflow-wrap:anywhere;max-width:76ch}
.fv-apollo-atlas .fv-apollo-citation-route a:focus-visible{outline:3px solid var(--accent);outline-offset:3px}
@media(forced-colors:active){.fv-apollo-atlas .fv-apollo-citation-route{border-color:CanvasText}}
@media print{.fv-apollo-atlas .fv-apollo-citation-route{color:#111!important;background:#fff!important;border-color:#111!important}}
'''

def build() -> dict:
    sys.path.insert(0, str(PARENT))
    from build_r202 import build as parent_build
    parent=parent_build()
    prior=PARENT/'dist'
    for path,digest in parent['files'].items():
        assert sha((prior/path).read_bytes()) == digest, 'inherited file integrity: '+path
    original=(prior/'templates/atlas-fragment.html').read_bytes()
    html=original.decode('utf-8')
    for old,new in CHANGES:
        assert html.count(old)==1, 'not precisely one source string: '+old[:55]
        html=html.replace(old,new,1)
    needle='<!-- R191 print-only source custody; visible without JS in printed output. -->'
    assert html.count(needle)==1
    html=html.replace(needle, NOTE+needle,1)
    assert html.count('class="cta"')==1 and html.count('<details>')==8
    assert all(term not in html for term in ('ChronologyRail','EvidencePlate','SourceDrawer','research prototype','unpublished prototype','proposed product','affiliate conversion is claimed'))
    old_css=(prior/'assets/atlas-scoped.css').read_bytes()
    css=old_css+CSS.encode('utf-8')
    php=(prior/'fv-ex2-apollo-r202.php').read_text('utf-8').replace('r202','r203').replace('R202','R203')
    for old,new in ((original,html.encode('utf-8')),(old_css,css)):
        assert php.count(sha(old))==1, 'expected parent integrity pin'
        php=php.replace(sha(old),sha(new),1)
    js=(prior/'assets/campaign-handoff.js').read_bytes()
    assert sha(js) in php
    files={'templates/atlas-fragment.html':html.encode('utf-8'),
           'assets/atlas-scoped.css':css,
           'assets/campaign-handoff.js':js,
           'fv-ex2-apollo-r203.php':php.encode('utf-8')}
    for path,blob in sorted(files.items()):
        dest=DIST/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(blob)
    shim=(prior/'wp-render-shim-r202.php').read_text('utf-8').replace('r202','r203').replace('R202','R203')
    (DIST/'wp-render-shim-r203.php').write_text(shim,encoding='utf-8')
    plan={
      'product_hypothesis':'Original educator Apollo 1 source-analysis dossier, not a currently purchasable item',
      'audience':'Educators and research-oriented viewers of a future verified Grok Apollo long-form asset',
      'current_destination':'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',
      'current_single_action':'Read original investigation',
      'commercial_offer_status':'not_verified_for_sale',
      'published_grok_apollo_asset_id':None,
      'attribution_status':'unverified',
      '7_day_qualified_human_sessions':None,
      '30_day_qualified_human_sessions':None,
      'merchant_confirmed_orders':None,
      'realized_net_revenue':None,
      'net_revenue_per_1000_qualified_sessions':None,
      'release_gate':'staging_hold',
      'requirements':['verify product and rights','verify checkout/fulfillment','inspect completed orders, fees and refunds','real WP staging and accessibility/axe','founder approval'],
    }
    (DIST/'conversion-validation.json').write_text(json.dumps(plan,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    manifest={'release':'r203','parent_head':'ad10ccf0c0df350fc5ba0bfa4986957c11370e5d',
      'scope':'Remove residual prototype language and add free accessible NASA source comparison',
      'files':{k:sha(v) for k,v in sorted(files.items())},
      'conversion_validation_sha256':sha((DIST/'conversion-validation.json').read_bytes()),
      'parent_manifest_sha256':sha((prior/'manifest.json').read_bytes()),
      'r198_github_archive_drift':'BLOCKED', 'gate':'draft_only_not_live; canonical R198 ancestry, installed WP, axe-core, assistive technology, exact-head CI, seller rights and purchase proof open'}
    (DIST/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return manifest
if __name__=='__main__': print(json.dumps(build(),indent=2))
